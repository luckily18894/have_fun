# -*- coding=utf-8 -*-
import openpyxl
import ipaddress


def ex_test(file):
    w = openpyxl.load_workbook(file)  # 读取文件，创建实例
    for e, f in w['Sheet1']['E5:F13']:  # 逐行读取Sheet1的这块区域，(<Cell 'Sheet1'.E5>, <Cell 'Sheet1'.F5>)返回的是每一行的组
        c = '/'.join(['0.0.0.0', f.value])  # 将F列的掩码整合到0.0.0.0地址上做计算，变成掩码位
        # //不知道如何直接算~~~
        a = ipaddress.IPv4Network(c).prefixlen  # 计算掩码的位数 255.255.255.255 ---> 32
        b = '/'.join([e.value, str(a)])  # 将计算好的掩码整合至地址
        w['Sheet1'].cell(row=e.row, column=7, value=b)  # 在相应行的后面一列 写入整合后的数据

        # w['Sheet1']['E4'] = b  # 直接对一个单元格赋值
    # print(w['Sheet1']['E4'].value)

    w.save('C:\\Users\\18568\\Desktop\\emos1.xlsx')  # 保存退出
    # w.close()  # 直接退出，不保存


if __name__ == "__main__":
    fil = 'C:\\Users\\18568\\Desktop\\emos.xlsx'
    ex_test(fil)

    # print(ipaddress.IPv4Network('1.1.1.0/255.255.255.252'))
    # print(_BaseV4._make_netmask("24"))

# https://www.jianshu.com/p/3f348b7552a7

# 类的各种方法
# ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_bind_value', '_comment', '_hyperlink', '_infer_value', '_style', '_value',
# 'alignment', 'base_date', 'border', 'check_error', 'check_string', 'col_idx', 'column', 'column_letter', 'comment', 'coordinate', 'data_type', 'encoding', 'fill', 'font', 'guess_types', 'has_style', 'hyperlink', 'internal_value', 'is_date', 'number_format', 'offset', 'parent', 'pivotButton', 'protection', 'quotePrefix', 'row', 'set_explicit_value', 'style', 'style_id', 'value']

# ipaddress.IPv4Network(agr)的相关属性
"""   
 Attributes: [examples for IPv4Network('192.0.2.0/27')]
            .network_address: IPv4Address('192.0.2.0')
            .hostmask: IPv4Address('0.0.0.31')
            .broadcast_address: IPv4Address('192.0.2.32')
            .netmask: IPv4Address('255.255.255.224')
            .prefixlen: 27
"""
