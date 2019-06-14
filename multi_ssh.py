# -*- coding=utf-8 -*-

import paramiko
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool as ProcessPool
import ipaddress
import re
import time


def py_ssh(ip, username, password, port, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, port=port, timeout=5, compress=True)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        res = stdout.read().decode()

        if re.match(".*sysname \w+.*", res, re.S | re.M):
            res = '{0} 正常'.format(ip)
        else:
            res = '{0} 未能re匹配'.format(ip)

    except Exception as d:
        res = '{0} 报错 {1}'.format(ip, d)

    return res


def multi_ssh_reachable(ipadd, username, password, port=22, cmd='dis cu | in sysname'):
    l1 = []
    pool = ThreadPool(processes=100)
    # pool = ProcessPool(processes=100)

    ipaddr = ipaddress.ip_network(ipadd)
    for ip in ipaddr:
        res = pool.apply_async(py_ssh, args=(str(ip), username, password, port, cmd)).get()
        # res = py_ssh(str(ip), username, password, port, cmd)
        l1.append(res)

    pool.close()
    pool.join()

    for a in l1:
        print(a)


if __name__ == '__main__':
    time_start = time.time()

    # multi_ssh_reachable('192.168.1.104/29', 'username', 'password')

    time_end = time.time()
    print('time cost', time_end - time_start, 's')

    # print(py_ssh('192.168.1.107', 'username', 'password', port=22, cmd='dis cu | in sysname'))


