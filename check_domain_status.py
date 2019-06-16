# -*- coding=utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time


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

    time.sleep(0.5)
    client = requests.session()
    comment = client.post(zhanzhang_url, headers=read_header('domain_status_header.txt'), data=payl)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    if comment_soup.find('div', class_="IcpMain02").text != '\n':
        return '已备案'
    else:
        return '未备案'


if __name__ == "__main__":
    domain = ['qytan.com', 'qytang.com']
    # 这是使用 站长之家 查询  其他的重扒
    for asdf in domain:
        zhanzhang_url = 'http://icp.chinaz.com/record/' + asdf
        payl = 't=2&host=' + asdf
        print(check_domain_status('domain_status_header.txt'))
