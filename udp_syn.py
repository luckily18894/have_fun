import logging
logging.getLogger("kamene.runtime").setLevel(logging.ERROR)  # 清除报错
from kamene.all import *
from kamene.layers.inet import IP, ICMP, UDP
from random import randint


def ping_one(dst):
    id_ip = randint(1, 65534)
    id_icmp = randint(1, 65534)
    seq_icmp = randint(1, 65534)
    ping_res = sr1(IP(dst=dst, ttl=100, id=id_ip) / ICMP(id=id_icmp, seq=seq_icmp), timeout=1, verbose=False)
    # pkt = IP(dst=str(ip), ttl=100, id=id_ip) / ICMP(id=id_icmp, seq=seq) / (b'w' * 32)
    # ping_res = sr1(IP(dst=dst, ttl=64) / ICMP() / b'w' * 32, timeout=1, verbose=False)
    print(ping_res)
    return 1 if ping_res else 0


def udp_syn(host, lport, hport):
    # ping = ping_one(host)
    # if ping == 0:
    #     print(host + '不可达')
    # else:
        result_raw = sr(IP(dst=host)/UDP(dport=(int(lport), int(hport))), timeout=float(1.0), verbose=False)
        scan_port = []  # 所有端口空的列表
        for x in range(int(lport), int(hport)):
            scan_port.append(x)  # 添加所有端口到列表
        port_not_open = []  # 添加不可达端口空的列表
        result_list = result_raw[0].res  # 设计为清单类型
        for i in range(len(result_list)):
            if result_list[i][1].haslayer(ICMP):
                port_not_open.append(result_list[i][1][3].fields['dport'])  # 添加到端口不可达空的列表
                # print(port_not_open)
        return list(set(scan_port).difference(set(port_not_open)))  # 全部端口和不可达端口作比较做一个差集，相当于一减，那就是开放端口集合


if __name__ == '__main__':
    while 1:
        try:
            print(ping_one(input('请输入ip地址:')))
        except KeyboardInterrupt:
            break
        except Exception as asd:
            print(asd)
            continue

    # while 1:
    #     try:
    #         host = input('ip地址：')
    #         lport = input('要扫描最低端口号：')
    #         hport = input('要扫描最高端口号：')
    #         for prot in udp_syn(host, lport, hport):
    #             print(prot)
    #
    #     except KeyboardInterrupt:
    #         break
    #     except Exception as asd:
    #         print(asd)
    #         continue
