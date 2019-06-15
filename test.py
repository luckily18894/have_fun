# -*- coding=utf-8 -*-

import requests
from bs4 import BeautifulSoup


def read_header(head_file):
    header_dict = {}

    header_txt = open(head_file)
    for header in header_txt.readlines():
        key, val = header.strip().split(':')
        header_dict[key.strip()] = val.strip()

    return header_dict


def get_soup(head_file, payload, url):
    client = requests.session()
    comment = client.post(url, headers=read_header(head_file), data=payload)
    comment.encoding = 'utf8'
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    # table = comment_soup.find_all('count')
    # print()
    return comment_soup


def fenxi(head_file, payload, url):
    comment_soup = get_soup(head_file, payload, url)
    if comment_soup.find('div', class_="IcpMain02").text != '\n':

        # 获取各条目的名称，未完工。。。
        # biaodan =comment_soup.find('div', class_="IcpMain02").find('thead').find('tr')
        # for b in biaodan:
        #     print(b)

        # 应该是用上面注释掉的自动扒取网页上的标题，不能这样。。
        l1 = ['主办单位名称', '单位性质', '网站备案/许可证号', '网站名称', '网站首页网址', '审核时间', '记录时间', '变更项', '变更记录']
        neirong = comment_soup.find('tbody', id="result_table")
        l2 = []  # 优化！！！
        for a in neirong.find('tr'):  # 若有网站多次变更，就会有多条tr项，第一条就是最新的，要取得所有需要再次使用for？
            l2.append(a.text)
        res_dict = dict(zip(l1, l2))
        print(res_dict)
    else:
        print('未备案')


if __name__ == "__main__":
    domain = 'qytang.com'
    # 这是使用 站长之家 查询  其他的重扒
    url = 'http://icp.chinaz.com/record/' + domain
    payload = 't=2&host=' + domain

    # print(get_soup('test_header.txt', payload, url))
    fenxi('test_header.txt', payload, url)
