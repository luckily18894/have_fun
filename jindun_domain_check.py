# -*- coding=utf-8 -*-

import socket
import pandas
import re
import math
import time
import requests
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

    # 返回结果  （'已备案 xxx', '未备案 xxx', '待查询 xxx'）
    return count[0], count[1], count[2]


# 取得记录的页数
def get_page_number(check_code):
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
    for state_number in range(0, 3):
        count_data = 'gettotal_paget=%3Fq%3Dwebbeian%2Fgettotal%2Fpagetype%2Fdomain&domain=&matching=1&status=' + str(state_number) + '&bytime=&userid=&serviceid='
        soup = get_soup(page_number_head, get_number_url, parameters=get_number_para, data=count_data)

        # 获取的总条目数 / 每页默认显示18条 = 页数（向上取整）
        if state_number == 0:
            unknown_page_number = math.ceil(int(soup.text) / 18)
        elif state_number == 1:
            signed_page_number = math.ceil(int(soup.text) / 18)
        elif state_number == 2:
            unsigned_page_number = math.ceil(int(soup.text) / 18)

    # print('已备案域名：{}页，未备案域名：{}页，未知域名：{}页'.format(signed_page_number, unsigned_page_number, unknown_page_number))
    return signed_page_number, unsigned_page_number, unknown_page_number


#  核心 未完工！！！
def out_put(check_code):
    out_put_head = {'Host': '124.160.57.2:28099',
                    # 'Upgrade-Insecure-Requests': '1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                    'X-Requested-With': 'XMLHttpRequest'
                    }
    # 未备案
    unsigned_url = 'https://124.160.57.2:28099/?q=webbeian/index/status/2/menuid/2'
    unsigned_para = 'q=webbeian/index/status/2/menuid/2'
    soup = get_soup(out_put_head, unsigned_url, parameters=unsigned_para)

    for tr in soup.find_all('tr')[1:]:
        print(list(filter(None, tr.text.strip().split('\n')))[:4])  # 剔除空值 ''


# 施工区！！！！
if __name__ == '__main__':
    import pprint
    import json

    time_start = time.time()

    check_code = login_to_system()  # 获得登录id号  必须！！！！
    # print(check_code)

    head = {'Host': '124.160.57.2:28099',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'PHPSESSID=7d3aecb7edc128d327c336ff3e3a43e1; ' + check_code,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
            }

    page_number = '1'
    status_code = '1'  # 0待查询 1已备案 2未备案

    # 跳转至x页 通用   返回的是json？？？ 要json.loads？？？？
    url = 'https://124.160.57.2:28099/?q=webbeian/index/status/' + status_code + '/bytime/0/page/' + page_number + '/pagesize/18/ajax/1'
    para = 'q=webbeian/index/status/' + status_code + '/bytime/0/page/' + page_number + '/pagesize/18/ajax/1'

    comm = get_soup(head, url, parameters=para)
    # print(comm._content)
    # 已测试 需读取原始返回数据（b'xxx'）才能转成js 正常显示type=str，  接下来：读取正常soup能否转js？？？ js能否再转回html作分析
    # ss = json.loads(comm._content)[1]
    # print(type(ss))

    ss = json.loads(comm.find_all('p')[0].text)[1]
    print(ss)

    # for a in comm.find_all('tbody', id="content_list"):
    # v = re.compile('<tr>.*<.*/tr>')
    # print(comm.get_text())
    # asdf = v.findall(comm.get_text())[0]
    # qwer = BeautifulSoup(asdf, 'lxml')
    # print(len(qwer.find_all('td')))

    # for td in comm.find_all('tr')[0].find_all('td'):
    #     print(td.text.split('\n'))

    # print(comm.find_all('tr')[0].text.split('\\n'))

    # for a in comm.find_all('tr'):
    #     print(list(filter(None, a.text.strip().split('\n'))))

    # print(get_count(check_code))
    # print(get_page_number(check_code))
    # out_put(check_code)  # 0.255

    time_end = time.time()
    print('totally cost:', time_end - time_start)




    # 已备案 多页
    # url1 = 'https://124.160.57.2:28099/?q=webbeian/index/status/1/menuid/1'
    # para1 = 'q=webbeian/index/status/1/menuid/1'
    #
    # url2 = 'https://124.160.57.2:28099/?q=webbeian/index/status/1/page/2/total/0/pagesize/18/ajax/1'
    # para2 = 'q=webbeian/index/status/1/page/2/total/0/pagesize/18/ajax/1'
    # data2 = 'gettotal_paget=%3Fq%3Dwebbeian%2Fgettotal%2Fpagetype%2Fdomain&domain=&matching=1&status=1&bytime=&userid=&serviceid='
    #
    # url3 = 'https://124.160.57.2:28099/?q=webbeian/index/status/1/bytime/0/page/' + page_number + '/total/0/pagesize/18/ajax/1'
    # para3 = 'q=webbeian/index/status/1/bytime/0/page/' + page_number + '/total/0/pagesize/18/ajax/1'
    # data3 = 'gettotal_paget=%3Fq%3Dwebbeian%2Fgettotal%2Fpagetype%2Fdomain&domain=&matching=1&status=1&bytime=&userid=&serviceid='


