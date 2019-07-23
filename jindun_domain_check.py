# -*- coding=utf-8 -*-

import socket
import pandas
import re
import math
import time
import json
import requests
import dns.resolver
import ipaddress
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def read_header(head_file):
#     header_dict = {}
#
#     header_txt = open(head_file)
#     for header in header_txt.readlines():
#         key, val = header.strip().split(':')
#         header_dict[key.strip()] = val.strip()
#
#     return header_dict

# class Jindun:
#     def __init__(self):


# 绕过验证码，得到登录后的check_code，拼接至cookie，返回可用的cookie
def login_to_system():
    login_head = {'Host': '124.160.57.2:28099',
                  'Origin': 'https://124.160.57.2:28099',
                  'Accept': '*/*',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Accept-Language': 'zh-CN,zh;q=0.9',
                  'Referer': 'https://124.160.57.2:28099/?q=common/login',
                  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',

                  # check_code里 就是验证码的答案，由请求验证码图片url后 在response头部里自动set cookie
                  # 验证码 系统是随机得到 script的Math.random()，所以在前端并没有校验
                  'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; check_code=js7i',
                  'X-Requested-With': 'XMLHttpRequest',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
                  }

    client = requests.session()
    comment = client.post('https://124.160.57.2:28099/index.php?q=common/login',
                          headers=login_head,
                          params='q=common/login',

                          # 将cookie里check_code的验证码答案 填入data表单中这样服务器就能验证通过了。。。
                          data='name=admin&password=hzhby123!%40%23&checkcode=js7i&doLoginSubmit=1',
                          verify=False
                          )

    # 在response的头部里，cookie已被服务器重新set  取得服务器分配的 代表登录成功 的check_code=xxxx
    check_code = comment.headers['Set-Cookie'].split(';', 1)[0]
    # cookie = 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code  # 拼接cookie并返回

    return check_code  # 还是单独返回check_code吧，以防万一cookie不一样


# 基础 爬取一个html页面  post方法（好像兼容get？？？）
def get_soup(header, url, parameters=None, data=None, jsons=None, cookie=None):
    client = requests.session()
    # client.keep_alive = False
    comment = client.post(url, headers=header, params=parameters, data=data, json=jsons, cookies=cookie, verify=False)
    comment.encoding = 'UTF-8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')
    # table = comment_soup.find_all('count')
    # print(table)
    return comment_soup


# 获得域名的解析地址
def get_domain_ip(dl):
    ips_list = []

    # 传来的是域名的列表，对每一个域名进行解析
    for each_domain in dl:
        try:
            a_type = dns.resolver.query(each_domain, 'A')
            for i in a_type.response.answer:
                for j in i.items:
                    # print(each_domain, type(j))
                    if type(j) == dns.rdtypes.IN.A.A:
                        ips_list.append(j.address)
            # 返回所有解析地址
            return list(set(ips_list))
        except dns.resolver.NXDOMAIN:
            return '无解析'
        except dns.resolver.NoAnswer:
            return '无解析'
        except Exception as e:
            print(e)
            return


# 统计信息  已备案 xx  未备案 xx  待查询 xx
def get_count(check_code):
    count_head = {'Host': '124.160.57.2:28099',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate, br',
                  'Accept-Language': 'zh-CN,zh;q=0.9',
                  'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
                  }

    # 首页 上面有统计信息  已备案 未备案 待查询
    main_page_url = 'https://124.160.57.2:28099/?q=cp/count'
    total_para = 'q=cp/count'

    soup = get_soup(count_head, main_page_url, parameters=total_para)
    count = re.findall('"(.*)"', soup.find_all('script')[10].text.strip().split(':')[7])

    # 返回结果  count = ['已备案 xxx', '未备案 xxx', '待查询 xxx', 'chart']
    print('{}条，{}条，{}条'.format(count[0], count[1], count[2]), '\n')
    return


# 取得记录的页数
def get_page_number(check_code, status_code):
    page_number_head = {'Host': '124.160.57.2:28099',
                        'Origin': 'https://124.160.57.2:28099',
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest'
                        }

    # 首页 上面有统计信息  已备案 未备案 待查询
    get_number_url = 'https://124.160.57.2:28099/?q=webbeian/gettotal/pagetype/domain'
    get_number_para = 'q=webbeian/gettotal/pagetype/domain'

    # 取得  0待查询 1已备案 2未备案  的个数
    count_data = 'gettotal_paget=%3Fq%3Dwebbeian%2Fgettotal%2Fpagetype%2Fdomain&domain=&matching=1&status=' + status_code + '&bytime=&userid=&serviceid='

    soup = get_soup(page_number_head, get_number_url, parameters=get_number_para, data=count_data)
    # 获取的总条目数 / 每页默认显示18条 = 页数（向上取整）
    page_number = math.ceil(int(soup.text) / 18)

    return page_number, soup.text


# 得到 二级域名列表 和 目的地址列表  (只查找第一页！！！！)
def get_second_domain(check_code, domain_name):
    second_domain_head = {'Host': '124.160.57.2:28099',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36',
                          'Accept': 'application/json, text/javascript, */*; q=0.01',
                          'Accept-Encoding': 'gzip, deflate, br',
                          'Accept-Language': 'zh-CN,zh;q=0.9',
                          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                          'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
                          'X-Requested-With': 'XMLHttpRequest'
                          }
    url = 'https://124.160.57.2:28099/index.php?q=webbeianevent/index/domain/' + domain_name + '/ishttps/1/bytime/0/page/1/total/0/pagesize/18/ajax/1'
    para = 'q=webbeianevent/index/domain/' + domain_name + '/ishttps/1/bytime/0/page/1/total/0/pagesize/18/ajax/1'
    data = 'gettotal_paget=%3Fq%3Dwebbeianevent%2Fgettotal%2Fpagetype%2Fdomain%2Fhttps%2F1&https=1&domain=' + domain_name + '&matching=1&ipv=&site_user=&bytime=&userid=&serviceid='
    soupp = get_soup(second_domain_head, url, parameters=para, data=data)

    if len(json.loads(soupp.find_all('p')[0].text)) == 3:  # 判断该页是否有数据， 1 无  3 有

        dl, il = [], []  # domain_list, ip_list

        # 返回的是json，需要json.loads取出内容
        second_domain = BeautifulSoup(json.loads(soupp.find_all('p')[0].text)[1], 'lxml')

        # 第一项在<p>内，所以需要单独做一次，和正常操作基本一样
        # ---------------------------------<p>---------------------------------------开始
        each_second_domain_list = second_domain.find('p').text.split('\n', 7)[:7]  # 0 domain 1 IP 4 ICP 5 check_time 6 update_time
        dl.append(each_second_domain_list[0].strip())
        il.append(each_second_domain_list[1].strip())
        # ---------------------------------<p>---------------------------------------结束

        # 剩下的都在<tr>内，正操操作即可
        for tr in second_domain.find_all('tr'):
            each_second_domain_list = tr.text.strip().split('\n')[:7]  # 0 domain 1 IP 4 ICP 5 check_time 6 update_time
            dl.append(each_second_domain_list[0].strip())
            il.append(each_second_domain_list[1].strip())

        # 返回 域名列表 和 目的地址列表
        return list(set(dl)), list(set(il))
    else:
        return '无记录', '无记录'


#  核心 已完成一级域名导出，已加入 第一页 主机和目的IP   后几页有必要？？？？
def out_put(check_code, status):
    out_put_head = {'Host': '124.160.57.2:28099',
                    'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                    }
    status_dict = {'已备案': '1', '未备案': '2', '待查询': '0'}
    status_code = status_dict[status]

    page_number, table_length = get_page_number(check_code, status_code)

    # 若没有数据 返回 无结果
    if table_length == '0':
        print('无结果', '\n')
        return

    final_list = []
    counter = 0
    print('共{}条数据，查询并导出中，请稍等.....'.format(table_length))

    # 客户ip字典
    c_dict = {'顺网': ['115.231.111.96/27', '124.90.38.96/27', '61.130.11.192/27', '115.231.111.64/27', '124.90.38.64/27',
                     '183.131.14.0/24', '124.90.37.32/27', '115.236.57.64/27', '183.136.238.192/26', '183.136.238.0/26',
                     '101.71.23.128/26', '115.236.57.192/28', '122.224.178.82', '122.224.178.83', '122.224.178.84',
                     '122.224.178.85', '122.224.178.86', '122.224.178.66', '122.224.178.67', '122.224.178.68',
                     '122.224.178.69', '122.224.178.70', '122.224.178.71', '122.224.178.72', '122.224.178.73',
                     '122.224.178.74', '122.224.178.75', '122.224.178.76', '122.224.178.77', '122.224.178.78',
                     '122.224.178.79', '122.224.178.80', '122.224.178.81', '115.236.57.224/28', '115.236.57.240/29',
                     '115.236.57.217', '115.236.57.218', '115.236.57.219', '115.236.57.220', '115.236.57.221',
                     '115.236.57.222', '115.236.57.223', '115.236.57.248', '112.13.94.160/28', '121.52.242.80/28',
                     '115.236.57.0/26', '183.131.182.8/29', '121.52.242.96/27', '121.52.247.160/27',
                     '122.224.114.128/26', '122.224.199.224/27', '122.224.178.106', '122.224.178.107',
                     '122.224.178.108', '122.224.178.109', '122.224.178.110', '122.224.178.111', '122.224.178.112',
                     '122.224.178.113', '122.224.178.114', '122.224.178.115', '122.224.178.116', '122.224.178.124',
                     '122.224.178.125'],
              '浮云': ['115.231.111.0/26', '183.134.105.0/25', '115.233.214.0/24', '124.160.112.0/26', '124.90.37.128/25',
                     '124.90.36.0/24', '115.236.4.192/28'],
              '思华': ['115.231.111.128/25', '183.131.20.64/27', '124.90.38.0/26', '223.93.140.32/27', '112.13.94.128/27',
                     '218.108.65.64/28', '115.233.223.26', '115.233.223.27', '115.233.223.28', '115.233.223.29',
                     '115.233.223.30'],
              '华通': ['115.236.72.0/28', '115.236.72.16/28', '223.93.148.192/26', '223.93.148.128/28', '112.13.94.0/25',
                     '124.90.37.0/28', '115.236.75.240/28', '115.236.75.224/28', '121.52.247.128/27', '121.52.246.0/24',
                     '101.251.146.0/25', '115.231.18.224/28', '124.160.116.32/28', '124.160.124.0/28'],
              '拓镜': ['60.190.245.16/28'],
              '召唤': ['122.224.178.2', '122.224.178.3', '122.224.178.6', '122.224.178.29', '122.224.178.30',
                     '122.224.178.31', '122.224.178.32', '122.224.178.33', '122.224.178.34', '122.224.178.35',
                     '122.224.178.36', '122.224.178.37', '122.224.178.38', '122.224.178.39', '122.224.178.40',
                     '122.224.178.41', '122.224.178.42', '122.224.178.51', '122.224.178.52', '122.224.178.53',
                     '122.224.178.54', '122.224.178.62', '122.224.178.63', '122.224.178.64', '122.224.178.65',
                     '122.224.178.101'],
              '齐顺': ['122.224.178.4', '122.224.178.5', '122.224.178.99', '122.224.178.103', '122.224.178.104',
                     '122.224.178.105', '122.224.178.117', '122.224.178.118', '122.224.178.119', '122.224.178.120',
                     '122.224.178.121', '122.224.178.122', '122.224.178.123', '124.160.238.111', '124.160.238.112',
                     '124.160.238.113', '124.160.238.114', '124.160.238.115', '124.160.238.116', '124.160.238.117',
                     '124.160.238.118', '124.160.238.119', '124.160.238.120', '124.160.238.121', '124.160.238.122',
                     '124.160.238.123'],
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

    # 进度条 0%
    done_sign, none_sign = '>', '_'
    print("{:<33} {:>3}".format(none_sign * 33, 0) + '%', end='')

    # 开始对每一页的数据进行处理
    for page in range(page_number):
        page += 1  # 从0开始，下边缘不算，所以需要先 +1

        # 跳转至x页
        x_page_url = 'https://124.160.57.2:28099/?q=webbeian/index/status/' + status_code + '/bytime/0/page/' + str(page) + '/pagesize/18/ajax/1'
        x_page_para = 'q=webbeian/index/status/' + status_code + '/bytime/0/page/' + str(page) + '/pagesize/18/ajax/1'

        comm = get_soup(out_put_head, x_page_url, parameters=x_page_para)

        # 对返回的数据js化 并转换成html 方便处理
        o = BeautifulSoup(json.loads(comm.find_all('p')[0].text)[1], 'lxml')

        # 第一条是在<p>中 所以需要单独处理一次  和正常操作基本一样
        # -------------------------<p>--------------------------------开始
        each_domain_list = o.find('p').text.split('\n', 7)[:6]
        counter += 1
        d1 = {'备案号': ''}  # 初始化时 先创建 '备案号' 项  确保pandas能正常写入该条目
        d1['计数'] = str(counter)
        d1['域名'] = each_domain_list[0].strip()
        d1['备案号'] = each_domain_list[3].strip()
        d1['查询时间'] = each_domain_list[4].strip()
        d1['最后更新时间'] = each_domain_list[5].strip()

        dl, il = get_second_domain(check_code, d1['域名'])
        d1['目的IP'] = il
        d1['最后访问页'] = dl
        d1['解析IP'] = get_domain_ip(d1['域名']) if dl == '无解析' else get_domain_ip(dl)


        d1['所属客户'] = ''  # 先创建该键，确保没查到所属客户时 pandas也能写入该条目
        for d_ip in d1['解析IP']:
            for c_ip in d2:
                if d_ip in d2[c_ip]:
                    d1['所属客户'] = c_ip

        # 处理完的数据字典加入列表 [{}, {}, {}]
        final_list.append(d1)

        # 进度条更新完成度
        per = int((counter / int(table_length)) * 100)  # 当前 已完成 百分比
        linetmpla = "{:%s<%s} {:>3}" % (none_sign, 33)  # 格式化打印 美化
        print('\r' + linetmpla.format(done_sign * int(per / 3), per) + '%', end='')
        # -------------------------<p>--------------------------------结束

        # 其余的数据都在<tr>中 按正常操作即可
        for td in o.find_all('tr'):
            each_domain_list = td.text.strip().split('\n')[:6]
            counter += 1
            d1 = {'备案号': ''}  # 初始化时 先创建 '备案号' 项  确保pandas能正常写入该条目
            d1['计数'] = str(counter)
            d1['域名'] = each_domain_list[0].strip()
            d1['备案号'] = each_domain_list[3].strip()
            d1['查询时间'] = each_domain_list[4].strip()
            d1['最后更新时间'] = each_domain_list[5].strip()

            dl, il = get_second_domain(check_code, d1['域名'])
            d1['目的IP'] = il
            d1['解析IP'] = get_domain_ip(dl)
            d1['最后访问页'] = dl

            d1['所属客户'] = ''  # 先创建该键，确保没查到所属客户时 pandas也能写入该条目
            for d_ip in d1['解析IP']:
                for c_ip in d2:
                    if d_ip in d2[c_ip]:
                        d1['所属客户'] = c_ip

            # 处理完的数据字典加入列表 [{}, {}, {}]
            final_list.append(d1)

            # 进度条更新完成度
            per = int((counter / int(table_length)) * 100)  # 当前 已完成 百分比
            linetmpla = "{:%s<%s} {:>3}" % (none_sign, 33)  # 格式化打印 美化
            print('\r' + linetmpla.format(done_sign * int(per / 3), per) + '%', end='')

    # 导出至excel
    asdf = pandas.DataFrame(final_list)
    asdf.to_excel('jindun_domain_{}.xlsx'.format(status),  # 文件名
                  sheet_name='{}记录查询'.format(status),  # sheet名
                  index=False,  # 不显示在第一列的索引号（序号）
                  columns=['所属客户', '解析IP', '域名', '最后访问页', '备案号', '单位', '最后访问时间', '系统ID', '目的IP', '计数']  # 列排序（实际作用是指定输出哪几列）
                  # columns=['所属客户', '解析IP', '域名', '备案号', '查询时间', '最后更新时间', '计数']
                  )

    print('\n')
    print('已导出{}条数据,文件路径E:\\123\\jindun_domain_{}.xlsx'.format(counter, status), '\n')
    return


# if __name__ == '__main__':
#     check_code = login_to_system()  # 获得登录id号  必须！！！！
#
#     print('''操作说明：
#         已备案 ----- 查询所有 已备案 记录 并导出至excel
#         未备案 ----- 查询所有 未备案 记录 并导出至excel
#         待查询 ----- 查询所有 待查询 记录 并导出至excel
#         统计 ------- 查询 已备案 未备案 待查询 条目总数
# 回车立即生效，无确认项！！！''', '\n')
#
#     while True:
#         try:
#             status = input('请输入操作：')
#             if status == 'exit':
#                 break
#             elif status == '':
#                 continue
#             elif status == '统计':
#                 get_count(check_code)
#                 continue
#             elif status == '已备案' or status == '未备案' or status == '待查询':
#                 out_put(check_code, status)
#                 continue
#             # elif status == '清空':
#             #     pay = data_dict['clear']
#             #     clear_all_record(pay)
#             #     continue
#             # elif status == '重启':
#             #     pay = data_dict['reboot']
#             #     reboot_system(pay)
#             #     continue
#             else:
#                 print('状态输入错误', '\n')
#                 continue
#         except KeyboardInterrupt:
#             break
#         except Exception as ex:
#             print(ex)
#             continue


# 施工测试区！！！
if __name__ == '__main__':
    time_start = time.time()

    check_code = login_to_system()  # 获得登录id号  必须！！！！
    # print(check_code)
    #
    # print(get_count(check_code))
    # print(get_page_number(check_code, '未备案'))
    out_put(check_code, '未备案')  # 0.255
    # print(get_second_domain(check_code, 'sanji123.com'))

    time_end = time.time()
    print('totally cost:', time_end - time_start)  # 计时


