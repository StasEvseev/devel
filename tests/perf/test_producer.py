from dht.dht_service import init, connect, reactor, set_value, set_json_value
from twisted.internet.defer import Deferred, DeferredList

import os
from logs import lg
from main import settings

import argparse

parser = argparse.ArgumentParser(description="Generate and place records to DHT")
parser.add_argument("start", type=int, help="start number", default=1)
parser.add_argument("end", type=int, help="end number", default=10000)
args = parser.parse_args()


def run(nodes):
    def callback(*args, **kwargs):
        print(args, kwargs)

    def errback(*args, **kwargs):
        import sys
        print(sys.exc_info())

    def callback_dfl(*args):
        print(args)
        reactor.stop()

    errback_dfl = errback

    try:
        list_of_deffered_set_value = []
        for i in range(args.start, args.end):
            d = set_value(str(i), str(i), 60)
            list_of_deffered_set_value.append(d)

            d.addBoth(callback)
            d.addErrback(errback)

        dfl = DeferredList(list_of_deffered_set_value)
        dfl.addCallback(callback_dfl)
        dfl.addErrback(errback_dfl)

    except:
        print('ERRRORO!!')
        reactor.stop()


def main():
    import time


    time.sleep(10)
    settings.init()

    lg.set_debug_level(1)

    init(udp_port=14441, db_file_path=settings.DHTDBFile())

    seeds = []

    for seed_env in (os.environ.get('DHT_SEED_1'), os.environ.get('DHT_SEED_2')):
        seed = seed_env.split(':')
        seeds.append((seed[0], int(seed[1])))

    print(seeds)

    connect(seeds).addBoth(run)
    reactor.run()


if __name__ == '__main__':
    main()
