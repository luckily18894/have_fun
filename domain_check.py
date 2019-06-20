# -*- coding=utf-8 -*-

import requests
import socket
import pandas
import time
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
# 清空数据
clear = "delete from domainrecord"
# 重启
reboot = 'r'


# 添加新监控IP
# add_ip = "INSERT INTO 'iprules' SELECT NULL,'115.231.111.0','1000000','1000000','1480000','1000','1000','1000','10','1000','1000','1000','1','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000','1000000','1000000','1000000','1000000','1000000','1000000','1000000','1000000','1000000','1000000','1000000','1000000' ;"
# 删除地址需要先读取 该条目在数据库中的唯一id 再删除此id

# 查询
# url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'
# 统计
# url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?number+recordstate'
# 清空
# url = 'http://124.160.238.107:81/cgi-bin/ms_saveconfig.cgi'
# 重启
# url = 'http://124.160.238.107:81/cgi-bin/reboot.cgi'
# 添加新监控地址
# url = 'http://124.160.238.107:81/cgi-bin/saveconfig.cgi'


def read_header(head_file):
    header_dict = {}

    header_txt = open(head_file)
    for header in header_txt.readlines():
        key, val = header.strip().split(':')
        header_dict[key.strip()] = val.strip()

    return header_dict


def check_domain_status(domain):
    zhanzhang_url = 'http://icp.chinaz.com/record/' + domain
    payl = 't=2&host=' + domain

    client = requests.session()
    comment = client.post(zhanzhang_url, headers=read_header('d:\\123\\domain_status_header.txt'), data=payl)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    if comment_soup.find('div', class_="IcpMain02").text != '\n':
        return '已备案'
    else:
        return '未备案'


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
        print('查询并导出中，请稍等.....   时间参考：100条数据约30秒', '\n')

        counter = 0
        l1 = []
        for a in table:
            d1 = {}
            counter += 1
            d1['number'] = str(counter)
            d1['id'] = a.find('id').text
            d1['domain'] = a.find('domainstr').text
            d1['ip'] = get_domain_ip(a.find('domainstr').text)
            d1['last_page'] = a.find('lastpage').text
            d1['icp'] = a.find('icpnumber').text
            d1['unit'] = a.find('unit').text
            d1['last_time'] = a.find('lasttime').text
            d1['signation_state'] = check_domain_status(d1['domain'])
            l1.append(d1)
            # print(counter)

        asf = pandas.DataFrame(l1)
        asf.to_excel('domain_{}.xlsx'.format(state))
        print('已导出{}条数据,至运行目录寻找domain_{}.xlsx文件'.format(counter, state))
        time.sleep(0.5)
        print('表中显示为 未备案 的项，由于查询网站原因，不一定准确，务必手动复查', '\n')
        return


def get_count(head_file, payload):
    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?number+recordstate'
    table = get_soup(head_file, payload, url)

    signed_count, unsigned_count, unknown_count = 0, 0, 0
    for a in table:
        if a.find('recordstate').text == '2':  # 已备案
            signed_count = a.find('number').text
        elif a.find('recordstate').text == '3':  # 未备案
            unsigned_count = a.find('number').text
        elif a.find('recordstate').text == '0':  # 未知
            # else:  # 未知  只返回3条结果，不是前2条那就是第3条
            unknown_count = a.find('number').text

    print('已备案域名：{}，未备案域名：{}，未知域名：{}'.format(signed_count, unsigned_count, unknown_count), '\n')
    return


def clear_all_record(head_file, payload):
    url = 'http://124.160.238.107:81/cgi-bin/ms_saveconfig.cgi'
    client = requests.session()
    comment = client.post(url, headers=read_header(head_file), data=payload)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    table = comment_soup.find('result')
    if table.text == '0':
        print('已清空数据', '\n')
        return
    else:
        print('有问题！！!!')


def reboot_system(head_file, payload):
    url = 'http://124.160.238.107:81/cgi-bin/reboot.cgi'
    client = requests.session()
    comment = client.post(url, headers=read_header(head_file), data=payload)
    comment.encoding = 'utf8'
    print(comment)
    print(type(comment))
    print('已发送指令，设备重启中.....', '\n')
    time.sleep(1)
    print('请等待1分钟后再操作！！', '\n')
    return


if __name__ == '__main__':
    # print(read_header('domain_check_header.txt'))
    # get_count('domain_check_header.txt', statistics)
    # output('domain_check_header.txt', signed, '未备案')

    header_check = 'd:\\123\\domain_check_header.txt'

    print('''操作说明：
        所有 ------- 查询 所有记录 并导出至excel
        已备案 ----- 查询所有 已备案 记录 并导出至excel
        未备案 ----- 查询所有 未备案 记录 并导出至excel
        未知 ------- 查询所有 未知 记录 并导出至excel
        统计 ------- 查询 已备案 未备案 未知 条目总数
        清空 ------- 清空所有数据
        重启 ------- 重启设备

回车立即生效，无确认项！！！''', '\n')

    while True:
        print('请输入操作：')
        status = input()
        if status == 'exit':
            break
        elif status == '':
            continue
        elif status == '所有':
            pay = all_records
        elif status == '已备案':
            pay = signed
        elif status == '未知':
            pay = unknown_records
        elif status == '未备案':
            pay = unsignin
        elif status == '统计':
            pay = statistics
            get_count(header_check, pay)
            continue
        elif status == '清空':
            pay = clear
            clear_all_record(header_check, pay)
            continue
        elif status == '重启':
            pay = reboot
            reboot_system(header_check, pay)
            continue
        else:
            print('状态输入错误', '\n')
            continue
        output(header_check, pay, status)
        # print('\n')
