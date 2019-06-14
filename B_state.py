# -*- coding=utf-8 -*-

from bs4 import BeautifulSoup
import requests
import pandas as pan


def read_header(head_file):  # 可将头部信息的文本文件转换成字典
    header_dict = {}

    header_txt = open(head_file)
    for header in header_txt.readlines():
        key, val = header.strip().split(':')
        header_dict[key.strip()] = val.strip()

    return header_dict


def get_comment(head_file, cid):  # 得到弹幕的页面
    client = requests.session()
    # comment页面URL
    url = 'https://comment.bilibili.com/' + cid + '.xml'

    # 获取comment页面
    comment = client.get(url, headers=read_header(head_file))
    # 用utf8解码  不然显示不了中文
    comment.encoding = 'utf8'
    # lxml HTML 解析器
    comment_soup = BeautifulSoup(comment.text, 'lxml')

    # 返回收到的页面
    return comment_soup


def soupinfo_to_excel(cid):  # 将页面分值入字典并放入列表中
    comment_soup = get_comment('B_state_header.txt', str(cid))
    # 取得所有<d>标签的数据
    table = comment_soup.find_all('d')
    # print(table)

    l1 = []
    for a in table:  # 对每一条数据分值入字典
        d1 = {}  # 初始化字典内容
        # p = a.get('p')[-17:]
        d1['弹幕'] = a.text
        d1['这应该是位置信息'] = a.get('p')
        l1.append(d1)
    # print(l1)

    # 将l1内容写入excel
    file = pan.DataFrame(l1)
    file.to_excel(str(cid) + '的弹幕.xlsx')


if __name__ == "__main__":
    # print(read_header('B_state_header.txt'))
    # print(get_comment('B_state_header.txt', '96505889'))   17
    soupinfo_to_excel('96505889')

