#!/usr/bin/python
#stun_client.py
#
# <<<COPYRIGHT>>>
#
#
#
#

"""
.. module:: stun_client

"""

from services.local_service import LocalService

def create_service():
    return StunClientService()
    
class StunClientService(LocalService):
    
    name = 'stun_client'
    
    def dependent_on(self):
        return ['distributed_hash_table',
                'udp_datagrams',
                ]
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    

    