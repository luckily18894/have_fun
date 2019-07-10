# -*- coding=utf-8 -*-

import requests
import socket
import pandas
import time
import dns.resolver
import ipaddress
from bs4 import BeautifulSoup


data_dict = {
             # 所有记录
             'all_records': "select  * from domainrecord where  (id NOT IN (SELECT TOP 0 id FROM domainrecord order by id desc ))  order by id desc",
             # 已备案
             'signed': "select  * from domainrecord where recordstate = '2' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '2' order by id desc ))  order by id desc",
             # 未知
             'unknown_records': "select  * from domainrecord where recordstate = '0' or recordstate = '1' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '0' or recordstate = '1' order by id desc ))  order by id desc",
             # 未备案
             'unsignin': "select  * from domainrecord where recordstate = '3' and (id NOT IN (SELECT TOP 0 id FROM domainrecord where recordstate = '3' order by id desc ))  order by id desc",
             # 统计数据
             'statistics': "SELECT COUNT(*) AS number, recordstate FROM domainrecord GROUP BY recordstate",
             # 清空数据
             'clear': "delete from domainrecord",
             # 重启
             'reboot': 'r'
             }

domain_check_header = {'Connection': 'keep-alive',
                       'Authorization': 'Basic YWRtaW46MTM4MTk0NTUyMDE=',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                       'Content-Type': 'text',
                       'Accept': '*/*',
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'zh-CN,zh;q=0.9'
                       }

# domain_status_header = {'Cache-Control': 'max-age=0',
#                         'Upgrade-Insecure-Requests': '1',
#                         'Content-Type': 'application/x-www-form-urlencoded',
#                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
#                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#                         'Accept-Encoding': 'gzip, deflate',
#                         'Accept-Language': 'zh-CN,zh;q=0.9'
#                         }


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


# def read_header(head_file):
#     header_dict = {}
#
#     header_txt = open(head_file)
#     for header in header_txt.readlines():
#         key, val = header.strip().split(':')
#         header_dict[key.strip()] = val.strip()
#
#     return header_dict


# def check_domain_status(domain):
#     zhanzhang_url = 'http://icp.chinaz.com/record/' + domain
#     payl = 't=2&host=' + domain
#
#     client = requests.session()
#     comment = client.post(zhanzhang_url, headers=read_header(domain_status_header), data=payl)
#     comment.encoding = 'utf8'
#     comment_soup = BeautifulSoup(comment.text, 'lxml')
#
#     if comment_soup.find('div', class_="IcpMain02").text != '\n':
#         return '已备案'
#     else:
#         return '未备案'

# def get_domain_ip(domain):
#    try:
#        ipadd = socket.getaddrinfo(domain, 'http')
#        b = []
#        for a in ipadd:
#            address = a[4][0]
#            b.append(address)
#        l1 = list(set(b))
#        return l1
#    except socket.gaierror:
#        # print('{}无解析'.format(domain))
#        return '无解析'
#    except Exception as e:
#        print(e)


def get_domain_ip(domain):
    ips_list = []
    try:
        a_type = dns.resolver.query(domain, 'A')
        for i in a_type.response.answer:
            for j in i.items:
                # print(domain, type(j))
                if type(j) == dns.rdtypes.IN.A.A:
                    ips_list.append(j.address)
        return ips_list
    except dns.resolver.NXDOMAIN:
        return '无解析'
    except dns.resolver.NoAnswer:
        return '无解析'
    except Exception as e:
        print(e)


def get_soup(payload, url):
    client = requests.session()
    comment = client.post(url, headers=domain_check_header, data=payload)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    table = comment_soup.find_all('count')
    # print(table)
    if not table:
        print('无结果', '\n')
        return
    return table


def output(payload, state):
    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'
    table = get_soup(payload, url)

    if table:
        table_length = len(table)
        counter = 0
        l1, d2 = [], {}
        done_sign, none_sign = '>', '_'
        print('共{}条数据，查询并导出中，请稍等.....'.format(table_length))
        # 进度条 0%
        print("{:<33} {:>3}".format(none_sign * 33, 0) + '%', end='')

        # 客户ip字典
        c_dict = {'顺网': ['115.231.111.96/27', '124.90.38.96/27', '61.130.11.192/27', '115.231.111.64/27', '124.90.38.64/27', '183.131.14.0/24', '124.90.37.32/27', '115.236.57.64/27', '183.136.238.192/26', '183.136.238.0/26', '101.71.23.128/26', '115.236.57.192/28', '122.224.178.82', '122.224.178.83', '122.224.178.84', '122.224.178.85', '122.224.178.86', '122.224.178.66', '122.224.178.67', '122.224.178.68', '122.224.178.69', '122.224.178.70', '122.224.178.71', '122.224.178.72', '122.224.178.73', '122.224.178.74', '122.224.178.75', '122.224.178.76', '122.224.178.77', '122.224.178.78', '122.224.178.79', '122.224.178.80', '122.224.178.81', '115.236.57.224/28', '115.236.57.240/29', '115.236.57.217', '115.236.57.218', '115.236.57.219', '115.236.57.220', '115.236.57.221', '115.236.57.222', '115.236.57.223', '115.236.57.248', '112.13.94.160/28', '121.52.242.80/28', '115.236.57.0/26', '183.131.182.8/29', '121.52.242.96/27', '121.52.247.160/27', '122.224.114.128/26', '122.224.199.224/27', '122.224.178.106', '122.224.178.107', '122.224.178.108', '122.224.178.109', '122.224.178.110', '122.224.178.111', '122.224.178.112', '122.224.178.113', '122.224.178.114', '122.224.178.115', '122.224.178.116', '122.224.178.124', '122.224.178.125'],
                  '浮云': ['115.231.111.0/26', '183.134.105.0/25', '115.233.214.0/24', '124.160.112.0/26', '124.90.37.128/25', '124.90.36.0/24', '115.236.4.192/28'],
                  '思华': ['115.231.111.128/25', '183.131.20.64/27', '124.90.38.0/26', '223.93.140.32/27', '112.13.94.128/27', '218.108.65.64/28', '115.233.223.26', '115.233.223.27', '115.233.223.28', '115.233.223.29', '115.233.223.30'],
                  '华通': ['115.236.72.0/28', '115.236.72.16/28', '223.93.148.192/26', '223.93.148.128/28', '112.13.94.0/25', '124.90.37.0/28', '115.236.75.240/28', '115.236.75.224/28', '121.52.247.128/27', '121.52.246.0/24', '101.251.146.0/25', '115.231.18.224/28', '124.160.116.32/28', '124.160.124.0/28'],
                  '拓镜': ['60.190.245.16/28'],
                  '召唤': ['122.224.178.2', '122.224.178.3', '122.224.178.6', '122.224.178.29', '122.224.178.30', '122.224.178.31', '122.224.178.32', '122.224.178.33', '122.224.178.34', '122.224.178.35', '122.224.178.36', '122.224.178.37', '122.224.178.38', '122.224.178.39', '122.224.178.40', '122.224.178.41', '122.224.178.42', '122.224.178.51', '122.224.178.52', '122.224.178.53', '122.224.178.54', '122.224.178.62', '122.224.178.63', '122.224.178.64', '122.224.178.65', '122.224.178.101'],
                  '齐顺': ['122.224.178.4', '122.224.178.5', '122.224.178.99', '122.224.178.103', '122.224.178.104', '122.224.178.105', '122.224.178.117', '122.224.178.118', '122.224.178.119', '122.224.178.120', '122.224.178.121', '122.224.178.122', '122.224.178.123', '124.160.238.111', '124.160.238.112', '124.160.238.113', '124.160.238.114', '124.160.238.115', '124.160.238.116', '124.160.238.117', '124.160.238.118', '124.160.238.119', '124.160.238.120', '124.160.238.121', '124.160.238.122', '124.160.238.123'],
                  '搜视': ['115.236.57.160/28', '121.52.242.64/28'],
                  '彩虹庄': ['122.224.199.224/27', '124.160.238.96/27'],
                  '老外测试': ['218.108.65.240/28'],
                  }
        # 网段转换成单个地址的列表
        d2 = {}
        for custm in c_dict:
            ip_list = []
            for ips in c_dict[custm]:
                for ip in ipaddress.ip_network(ips):
                    ip_list.append(str(ip))
            d2.update({custm: ip_list})

        # 开始处理查询到的数据
        for a in table:
            d1 = {}
            counter += 1
            d1['计数'] = str(counter)
            d1['系统ID'] = a.find('id').text
            d1['域名'] = a.find('domainstr').text
            d1['最后访问页'] = a.find('lastpage').text
            d1['解析IP'] = get_domain_ip(d1['最后访问页'])
            d1['备案号'] = a.find('icpnumber').text
            d1['单位'] = a.find('unit').text
            d1['最后访问时间'] = a.find('lasttime').text
            d1['目的IP'] = a.find('dip').text
            # d1['signation_state'] = check_domain_status(d1['domain'])

            d1['所属客户'] = ''  # 先创建该键，确保没查到所属客户时 pandas也能写入该条目
            for d_ip in d1['解析IP']:
                for c_ip in d2:
                    if d_ip in d2[c_ip]:
                        d1['所属客户'] = c_ip

            # 处理完的数据字典加入列表 [{}, {}, {}]
            l1.append(d1)

            # 进度条更新完成度
            per = int((counter / table_length) * 100)  # 当前 已完成 百分比
            linetmpla = "{:%s<%s} {:>3}" % (none_sign, 33)  # 格式化打印 美化
            print('\r' + linetmpla.format(done_sign * int(per / 3), per) + '%', end='')

        # 导出至excel
        asdf = pandas.DataFrame(l1)
        asdf.to_excel('domain_{}.xlsx'.format(state),  # 文件名
                      sheet_name='{}记录查询'.format(state),  # sheet名
                      index=False,  # 不显示在第一列的索引号（序号）
                      columns=['所属客户', '解析IP', '域名', '最后访问页', '备案号', '单位', '最后访问时间', '系统ID', '目的IP', '计数']  # 列排序（实际作用是指定输出哪几列）
                      )

        print('\n')
        print('已导出{}条数据,文件路径E:\\123\\domain_{}.xlsx'.format(counter, state), '\n')
        # time.sleep(0.5)
        # print('表中显示为 未备案 的项，由于查询网站原因，不一定准确，务必手动复查', '\n')
        return


def get_count(payload):
    url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?number+recordstate'
    table = get_soup(payload, url)
    # try:
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


def clear_all_record(payload):
    url = 'http://124.160.238.107:81/cgi-bin/ms_saveconfig.cgi'
    client = requests.session()
    comment = client.post(url, headers=domain_check_header, data=payload)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    table = comment_soup.find('result')
    if table.text == '0':
        print('已清空数据', '\n')
        return
    else:
        print('有问题！！!!')


def reboot_system(payload):
    url = 'http://124.160.238.107:81/cgi-bin/reboot.cgi'
    client = requests.session()
    comment = client.post(url, headers=domain_check_header, data=payload)
    comment.encoding = 'utf8'
    print(comment)
    print(type(comment))
    print('已发送指令，设备重启中.....', '\n')

    # 倒计时60s
    countdown = 60
    while True:
        if countdown >= 0:
            print('\r' + '请务必等待{}秒后再操作！！'.format(countdown), end='')  # \r 再打印 可以覆盖掉之前的
            countdown -= 1
            time.sleep(1)
        else:
            print('\n')  # 也可以\r 覆盖掉 倒计时0秒
            break
    return


if __name__ == '__main__':
    # print(read_header('domain_check_header.txt'))
    # get_count('domain_check_header.txt', statistics)
    # output('domain_check_header.txt', signed, '未备案')

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
        try:
            status = input('请输入操作：')
            if status == 'exit':
                break
            elif status == '':
                continue
            elif status == '所有':
                pay = data_dict['all_records']
            elif status == '已备案':
                pay = data_dict['signed']
            elif status == '未知':
                pay = data_dict['unknown_records']
            elif status == '未备案':
                pay = data_dict['unsignin']
            elif status == '统计':
                pay = data_dict['statistics']
                get_count(pay)
                continue
            elif status == '清空':
                pay = data_dict['clear']
                clear_all_record(pay)
                continue
            elif status == '重启':
                pay = data_dict['reboot']
                reboot_system(pay)
                continue
            else:
                print('状态输入错误', '\n')
                continue
            output(pay, status)
            # print('\n')
        except KeyboardInterrupt:
            break
        except Exception as ex:
            print(ex)
            continue
