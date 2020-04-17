# -*- coding=utf-8 -*-

import re
import csv
import pandas


def nat(file):
    with open(file) as f:
        n = f.readlines()
    file_name = re.match('.*\\\(\w+)\.txt', file).groups()[0]
    # l1 = []

    with open('C:\\Users\\luckily18894\\Desktop\\' + file_name + '.csv', 'a', encoding='utf-8-sig', newline='') as fil:
        writer = csv.writer(fil)
        title = ['id_number', 'Global', 'Inside']
        d1 = {dd: dd for dd in title}  # 先写入每列标题

        writer.writerow([d1[ii] for ii in title])

        for e in n:
            b = re.match('.*nat server (\d+) global (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) inside (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*', e).groups()
            d1 = {title[nn]: b[nn] for nn in range(len(title))}
            writer.writerow([d1[ii] for ii in title])

    # asdf = pandas.DataFrame(l1)
    # asdf.to_excel('{}.xlsx'.format(file[-8:-4]),  # 文件名
    #               # sheet_name='{}记录查询'.format(state),  # sheet名
    #               index=False,  # 不显示在第一列的索引号（序号）
    #               columns=['Global', 'Inside']
    #               # 列排序（实际作用是指定输出哪几列）
    #               )


if __name__ == '__main__':
    fi = ['C:\\Users\\luckily18894\\Desktop\\FW01.txt',
          'C:\\Users\\luckily18894\\Desktop\\FW03.txt']
    for a in fi:
        nat(a)

