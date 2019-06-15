# -*- coding=utf-8 -*-

import requests
import socket
import pandas
from bs4 import BeautifulSoup

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

# 查询
# url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'
# 统计
# url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?number+recordstate'


def read_header(head_file):
    header_dict = {}

    header_txt = open(head_file)
    for header in header_txt.readlines():
        key, val = header.strip().split(':')
        header_dict[key.strip()] = val.strip()

    return header_dict


def get_domain_ip(domain):
    try:
        ipadd = socket.getaddrinfo(domain, 'http')
        b = []
        for a in ipadd:
            address = a[4][0]
            b.append(address)
        l1 = list(set(b))
        return l1
    except socket.gaierror:
        # print('{}无解析'.format(domain))
        return '无解析'
    except Exception as e:
        print(e)


def get_soup(head_file, payload, url):
    client = requests.session()
    comment = client.post(url, headers=read_header(head_file), data=payload)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    table = comment_soup.find_all('count')
    # print(table)
    if not table:
        print('无结果', '\n')
        return
    return table


def output(head_file, payload, state):
    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'
    table = get_soup(head_file, payload, url)

    if table:
        print('查询并导出中，请稍等.....')

        counter = 1
        l1 = []
        for a in table:
            d1 = {}

            d1['number'] = str(counter)
            d1['id'] = a.find('id').text
            d1['domain'] = a.find('domainstr').text
            d1['dip'] = get_domain_ip(a.find('domainstr').text)
            d1['lastpage'] = a.find('lastpage').text
            d1['icp'] = a.find('icpnumber').text
            d1['unit'] = a.find('unit').text
            d1['lasttime'] = a.find('lasttime').text
            l1.append(d1)
            counter += 1

        asf = pandas.DataFrame(l1)
        asf.to_excel('domain_{}.xlsx'.format(state))
        print('已导出{}条数据,至运行目录寻找domain_{}.xlsx文件'.format(counter-1, state), '\n')
        return


def get_count(head_file, payload):
    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?number+recordstate'
    table = get_soup(head_file, payload, url)

    signed_count, unsigned_count, unknown_count = 0, 0, 0
    for a in table:
        if a.find('recordstate').text == '2':  # 已备案
            signed_count = a.find('number').text
        if a.find('recordstate').text == '3':  # 未备案
            unsigned_count = a.find('number').text
        if a.find('recordstate').text == '01':  # 未知
            unknown_count = a.find('number').text
    print('已备案域名：{}，未备案域名：{}，未知域名：{}'.format(signed_count, unsigned_count, unknown_count), '\n')
    return


if __name__ == '__main__':
    # print(read_header('domain_check_header.txt'))
    # get_count('domain_check_header.txt', statistics)
    # output('domain_check_header.txt', signed, '未备案')

    print('查询条件： 所有记录  已备案  未备案  未知  统计数据')
    print('查询条件： 所有记录  已备案  未备案  未知  统计数据')
    print('查询条件： 所有记录  已备案  未备案  未知  统计数据')
    print('\n')
    while True:
        print('输入查询条件：')
        status = input()
        if status == 'exit':
            break
        elif status == '':
            continue
        elif status == '所有记录':
            pay = all_records
        elif status == '已备案':
            pay = signed
        elif status == '未知':
            pay = unknown_records
        elif status == '未备案':
            pay = unsignin
        elif status == '统计数据':
            pay = statistics
            get_count('domain_check_header.txt', pay)
            continue
        else:
            print('状态输入错误', '\n')
            continue
        output('domain_check_header.txt', pay, status)
        # print('\n')


