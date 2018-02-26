#!/usr/bin/python
# service_blockchain.py
#
# Copyright (C) 2008-2018 Veselin Penev, https://bitdust.io
#
# This file (service_blockchain.py) is part of BitDust Software.
#
# BitDust is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BitDust Software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with BitDust Software.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact us if you have any questions at bitdust.io@gmail.com
#
#
#
#

"""
..

module:: service_blockchain
"""

from services.local_service import LocalService


def create_service():
    return BlockchainService()


class BlockchainService(LocalService):

    service_name = 'service_blockchain'
    config_path = 'services/blockchain/enabled'

    def dependent_on(self):
        return ['service_tcp_connections',
                ]

    def installed(self):
        try:
            import os
            import sys
            dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
            blockchain_dir = os.path.abspath(os.path.join(dirpath, 'blockchain'))
            if blockchain_dir not in sys.path:
                sys.path.insert(0, blockchain_dir)
            from blockchain import pybc_service
        except:
            return False
        return True

    def start(self):
        import os
        from twisted.internet import reactor
        from main import config
        from main import settings
        from main import events
        from blockchain import pybc_service
        pybc_home = settings.BlockchainDir()
        seeds = config.conf().getString('services/blockchain/seeds')
        if seeds:
            seed_nodes = [(i.split(':')[0], int(i.split(':')[1]), ) for i in seeds.split(',')]
        else:
            seed_nodes = pybc_service.seed_nodes()
        pybc_service.init(
            host=config.conf().getData('services/blockchain/host'),
            port=config.conf().getInt('services/blockchain/port'),
            seed_nodes=seed_nodes,
            blockstore_filename=os.path.join(pybc_home, 'blocks'),
            keystore_filename=os.path.join(pybc_home, 'keys'),
            peerstore_filename=os.path.join(pybc_home, 'peers'),
            minify=None,
            loglevel='DEBUG',
            logfilepath=os.path.join(pybc_home, 'log'),
            stats_filename=None,
        )
        if config.conf().getBool('services/blockchain/explorer/enabled'):
            pybc_service.start_block_explorer(config.conf().getInt('services/blockchain/explorer/port'), pybc_service.node())
        if config.conf().getBool('services/blockchain/wallet/enabled'):
            pybc_service.start_wallet(config.conf().getInt('services/blockchain/wallet/port'), pybc_service.node(), pybc_service.wallet())
        if config.conf().getBool('services/blockchain/miner/enabled'):
            reactor.callFromThread(pybc_service.generate_block,
                                   json_data={},
                                   with_inputs=True,
                                   repeat=True, )
        events.add_subscriber(self._on_local_identity_modified, 'local-identity-modified')
        reactor.callLater(5, self._do_check_register_my_identity)
        return True

    def stop(self):
        from blockchain import pybc_service
        pybc_service.shutdown()
        return True

    def _on_local_identity_modified(self, evt):
        from twisted.internet import reactor
        reactor.callLater(0, self._do_check_register_my_identity)
        return True

    def _do_check_register_my_identity(self):
        from logs import lg
        from userid import my_id
        from blockchain import pybc_service
        from blockchain.pybc import util
        found = False
        for tr in pybc_service.node().blockchain.iterate_transactions_by_address(pybc_service.wallet().get_address()):
            for auth in tr.authorizations:
                auth_data = util.bytes2string(auth[2])
                if not auth_data or 'k' not in auth_data:
                    continue
                if auth_data['k'] == my_id.getLocalIdentity().publickey:
                    found = True
                    break
        if not found:
            if pybc_service.wallet().get_balance() < 2:
                pybc_service.generate_block(
                    json_data=None,
                    with_inputs=False,
                    repeat=False,
                    threaded=False,
                )
            if pybc_service.wallet().get_balance() < 2:
                lg.warn('not able to generate some balance')
                return
            pybc_service.new_transaction(
                destination=util.bytes2string(pybc_service.wallet().get_address()),
                amount=1,
                json_data=None,
                auth_data={
                    'k': my_id.getLocalIdentity().publickey,
                    'u': my_id.getLocalIdentity().getIDName(),
                    'd': my_id.getLocalIdentity().date,
                },
            )
