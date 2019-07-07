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
        # 若有网站多次变更，就会有多条tr项，第一条就是最新的，要取得所有需要再次使用for？
        l2 = [a.text for a in neirong.find('tr')]

        res_dict = dict(zip(l1, l2))
        print(res_dict)
        return
    else:
        print('未备案')
        return


if __name__ == "__main__":
    domain = 'qytang.com'
    # 这是使用 站长之家 查询  其他的重扒
    url = 'http://icp.chinaz.com/record/' + domain
    payload = 't=2&host=' + domain

    # print(get_soup('domain_status_header.txt', payload, url))
    # fenxi('domain_status_header.txt', payload, url)

    import time

    # lineLength = 20
    # delaySeconds = 0.25
    # frontSymbol = '='
    # frontSymbol2 = ['—', '\\', '|', '/']
    # backSymbol = ' '
    #
    # for i in range(10):
    #     lineTmpla = "{:%s<%s} {} {:<2}" % (backSymbol, lineLength)
    #     print(lineTmpla)
    #     for j in range(lineLength):
    #         tmpSymbol = frontSymbol2[j % (len(frontSymbol2))]
    #         print("\r" + lineTmpla.format(frontSymbol * j, tmpSymbol, j), end='')
    #         time.sleep(delaySeconds)

    # t = 5
    # while True:
    #     if t >= 0:
    #         print('\r'+'请务必等待{}秒后再操作！！'.format(t), end='')
    #         t -= 1
    #         time.sleep(1)
    #     else:
    #         print('\n')
    #         break

    table_length = 14
    counter = 0
    for a in range(table_length):
        counter += 1

        per = int((counter / table_length) * 100)
        frontsymbol = '='
        backsymbol = ' '
        linetmpla = "{:%s<%s} {:<2}" % (backsymbol, 33)
        for j in range(table_length):
            print('\r' + linetmpla.format(frontsymbol * int(per / 3), per) + '%', end='')
        time.sleep(0.4)


