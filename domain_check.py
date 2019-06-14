# -*- coding=utf-8 -*-

import requests
import socket
import pandas
from bs4 import BeautifulSoup


def read_header(head_file):
    header_dict = {}

    header_txt = open(head_file)
    for header in header_txt.readlines():
        key, val = header.strip().split(':')
        header_dict[key.strip()] = val.strip()

    return header_dict


def get_comment(head_file, state):
    # 所有记录
    all_records = "select  * from domainrecord where  (id NOT IN (SELECT TOP 0 id FROM domainrecord order by id desc ))  order by id desc"
    # 已备案
    signed = "select  * from domainrecord where recordstate = '2' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '2' order by id desc ))  order by id desc"
    # 未知
    unknown_records = "select  * from domainrecord where recordstate = '0' or recordstate = '1' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '0' or recordstate = '1' order by id desc ))  order by id desc"
    # 未备案
    unsignin = "select  * from domainrecord where recordstate = '3' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '3' order by id desc ))  order by id desc"
    # 统计数据
    statistics = "SELECT COUNT(*) AS number, recordstate FROM domainrecord GROUP BY recordstate"

    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'

    if state == '所有记录':
        payload = all_records
    elif state == '已备案':
        payload = signed
    elif state == '未知':
        payload = unknown_records
    elif state == '未备案':
        payload = unsignin
    else:
        print('状态输入错误')
        return

    client = requests.session()
    comment = client.post(url, headers=read_header(head_file), data=payload)

    comment.encoding = 'utf8'

    comment_soup = BeautifulSoup(comment.text, 'lxml')

    table = comment_soup.find_all('count')
    # print(table)
    if not table:
        print('无结果')
        return

    counter = 1
    l1 = []
    for a in table:
        d1 = {}

        d1['number'] = str(counter)
        d1['id'] = a.find('id').text
        d1['domain'] = a.find('domainstr').text
        d1['dip'] = get_domain_ip(a.find('dip').text)
        d1['lastpage'] = a.find('lastpage').text
        d1['icp'] = a.find('icpnumber').text
        d1['unit'] = a.find('unit').text
        d1['lasttime'] = a.find('lasttime').text
        l1.append(d1)
        counter += 1

    asf = pandas.DataFrame(l1)
    asf.to_excel('domain_check.xlsx')
    print('已导出{}条数据,至运行目录寻找domain.xlsx文件'.format(counter-1))
    return


def get_domain_ip(domain):
    ipadd = socket.getaddrinfo(domain, 'http')
    b = []
    for a in ipadd:
        address = a[4][0]
        b.append(address)
    l1 = list(set(b))
    return l1


if __name__ == '__main__':
    # print(read_header('header.txt'))
    print('查询条件： 所有记录  已备案  未备案  未知')
    print('查询条件： 所有记录  已备案  未备案  未知')
    print('查询条件： 所有记录  已备案  未备案  未知')
    print('\n')
    while True:
        print('输入查询条件：')
        status = input()
        if status == 'exit':
            break
        get_comment('header.txt', status)
        print('\n')

