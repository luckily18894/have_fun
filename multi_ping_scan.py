# -*- coding=utf-8 -*-

import logging
logging.getLogger('kamene.runtime').setLevel(logging.ERROR)
from kamene.all import *
from kamene.layers.inet import IP, ICMP
from random import randint
import ipaddress


def ping1(ipadd):

    id_icmp = randint(1, 65535)
    seq = 1
    # / time_in_bytes, timeout=1, verbose=False
    ipaddr = ipaddress.ip_network(ipadd)
    for ip in ipaddr:
        id_ip = randint(1, 65535)
        pkt = IP(dst=str(ip), ttl=100, id=id_ip) / ICMP(id=id_icmp, seq=seq) / (b'w'*32)
        res = sr1(pkt, timeout=0.5, verbose=False)

        if res:
            r = '通'
        else:
            r = '不'

        print(str(ip), r)
        seq += 1


if __name__ == '__main__':
    from multiprocessing.pool import ThreadPool

    scan_ip = '115.231.111.0/28'
    pool = ThreadPool(processes=100)

    print(pool.apply_async(ping1, args=(str(scan_ip),)).get())

    pool.close()
    pool.join()


