# -*- coding=utf-8 -*-

import requests
import socket
import pandas
import time
from bs4 import BeautifulSoup


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
    client.keep_alive = False
    comment = client.get(zhanzhang_url, headers=read_header('e:\\123\\test_header.txt'), data=payl, verify=False)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    if comment_soup.find('div', class_="IcpMain02").text != '\n':
        return '已备案'
    else:
        return '未备案'


def get_soup(head_file, payload, url):
    client = requests.session()
    #client.keep_alive = False
    comment = client.post(url, headers=read_header(head_file), data=payload, verify=False)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    #table = comment_soup.find_all('count')
    # print(table)
    return comment_soup


# def output(head_file, payload, state):
#     url = 'http://124.160.238.107:81/cgi-bin/ms_readconfig.cgi?id+domainstr+dip+recordstate+icpnumber+unit+phone+lasttime+lastpage+shieldstate+remark'
#     table = get_soup(head_file, payload, url)
#
#     if table:
#         print('查询并导出中，请稍等.....  ', '\n')
#
#         counter = 0
#         l1 = []
#         for a in table:
#             d1 = {}
#             counter += 1
#             d1['number'] = str(counter)
#             d1['sys_id'] = a.find('id').text
#             d1['domain'] = a.find('domainstr').text
#             d1['last_page'] = a.find('lastpage').text
#             d1['dip'] = get_domain_ip(d1['last_page'])
#             d1['icp'] = a.find('icpnumber').text
#             d1['unit'] = a.find('unit').text
#             d1['last_time'] = a.find('lasttime').text
#             #d1['signation_state'] = check_domain_status(d1['domain'])
#             l1.append(d1)
#             # print(counter)
#
#         asf = pandas.DataFrame(l1)
#         asf.to_excel('domain_{}.xlsx'.format(state))
#         print('已导出{}条数据,至运行目录寻找domain_{}.xlsx文件'.format(counter, state))
#         time.sleep(0.5)
#         print('表中显示为 未备案 的项，由于查询网站原因，不一定准确，务必手动复查', '\n')
#         return


if __name__ == '__main__':
    import pprint
    
    heads = 'test_header.txt'
    
    para = 'q=webbeian/index/status/2/menuid/2'
    para1 = 'q=webbeian/index/status/1/page/2/total/0/pagesize/18/ajax/1'
    para2 = 'q=webbeian/index/status/1/bytime/0/page/3/total/0/pagesize/18/ajax/1'
    
    url = 'https://124.160.57.2:28099/?q=webbeian/index/status/2/menuid/2'
    url1 = 'https://124.160.57.2:28099/?q=webbeian/index/status/1/page/2/total/0/pagesize/18/ajax/1'
    url2 = 'https://124.160.57.2:28099/?q=webbeian/index/status/1/bytime/0/page/3/total/0/pagesize/18/ajax/1'
    #print(read_header(heads))
    
    pprint.pprint(get_soup(heads, para, url))

