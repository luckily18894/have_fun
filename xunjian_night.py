# -*- coding=utf-8 -*-

import re
import time
import random
import datetime
import schedule
import requests

head = {'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': '__user=wjj; __username=%u5434%u5BB6%u6770; __userAuthority=255'
        }

url = 'http://10.10.66.249:4088/web/submit?callback=InspectionCB'  # 都是往同一个url发送的
pa = 'callback=InspectionCB'  # param 固定


def send_record(data):
    client = requests.session()
    comment = client.post(url, headers=head, params=pa, data=data)
    comment.encoding = 'utf8'

    errmsg = re.findall('"errmsg": "(.*)",', comment.text)

    return errmsg[0]


def xunjian_timing(dict1, dict2):
    # 获取当前时间对应的data  因为当前时间和data时间不一定一致,所以手动改成对应的时间  16点为00 所以要区分一下
    now_hour = datetime.datetime.now().strftime('%H:')
    timeee = now_hour + '00' if now_hour == '16:' else now_hour + '30'
    data_list1, data_list2 = dict1[timeee], dict2[timeee]

    # 将每个机房的温湿度赋值   room4 = [('21.9', '70.6'), ('', ''), ('', '')...] 有几个冷池就有几个组
    floor1 = re.findall('(\d{2}\.\d)/(\d{2}\.\d)', data_list1)
    wl, zh, room2, room3 = floor1[0], floor1[1], floor1[2:5], floor1[5]
    floor2 = re.findall('(\d{2}\.\d)/(\d{2}\.\d)', data_list2)
    room4, k = floor2[0:6], floor2[6]
    # print(zh, room4[2])  # 测试

    # 将各冷池的温湿度 填入 要发送的各data
    # [float, 'data'] 第0项是巡检该项目的用时（单位：min）  第1项是对应项目所需发送的data
    data_dict = {
        # 网运系统  30009
        '网运系统': [0.3,
             'CHINAIDSQK=%E6%AD%A3%E5%B8%B8&IDSDBQK=%E6%AD%A3%E5%B8%B8&CACTIEZMQK=%E6%AD%A3%E5%B8%B8&CACTIEZBQK=%E6%AD%A3%E5%B8%B8&CACTIEZQK=%E6%AD%A3%E5%B8%B8&CACTINEWQK=%E6%AD%A3%E5%B8%B8&ZABBIXQK=%E6%AD%A3%E5%B8%B8&ZABBIXCQK=%E6%AD%A3%E5%B8%B8&ZABBIXDQK=%E6%AD%A3%E5%B8%B8&ESIGHTQK=%E6%AD%A3%E5%B8%B8&BKNZXQK=%E6%AD%A3%E5%B8%B8&HSNZXQK=%E6%AD%A3%E5%B8%B8&TURBOMAILQK=%E6%AD%A3%E5%B8%B8&ZHSERQK=%E6%AD%A3%E5%B8%B8&ESXIAQK=%E6%AD%A3%E5%B8%B8&ESXIBQK=%E6%AD%A3%E5%B8%B8&ESXICQK=%E6%AD%A3%E5%B8%B8&ESXIDQK=%E6%AD%A3%E5%B8%B8&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30009&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E7%BD%91%E8%BF%90%E7%B3%BB%E7%BB%9F%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='],
        # 监控室  30008
        '监控室': [0.5,
                'ZBDLYXQK=%E6%AD%A3%E5%B8%B8&JKDPYXQK=%E6%AD%A3%E5%B8%B8&PINGYXZT=%E6%AD%A3%E5%B8%B8&GJFX=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30008&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E7%9B%91%E6%8E%A7%E5%AE%A4%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='],
        # 进线间  30007
        '进线间': [1,
                'JXJDCY=%E6%97%A0&GLZJD=%E6%AD%A3%E5%B8%B8&PXJZJD=%E6%AD%A3%E5%B8%B8&TQZJD=%E6%AD%A3%E5%B8%B8&PXGMGB=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30007&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E8%BF%9B%E7%BA%BF%E9%97%B4%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='],
        # 网络机房  30006
        '网络机房': [2.9,
                 'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_WL=%E6%AD%A3%E5%B8%B8&WLSBQK_WL=%E6%AD%A3%E5%B8%B8&JGMZT_WL=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_WL=%E6%AD%A3%E5%B8%B8&JFWD_WL={}&JFSD_WL={}&ZYSB_WL01_5328=%E6%AD%A3%E5%B8%B8&ZYSB_WL0102_9306=%E6%AD%A3%E5%B8%B8&ZYSB_WL0102_HX9306=%E6%AD%A3%E5%B8%B8&ZYSB_WL03_NE40E=%E6%AD%A3%E5%B8%B8&ZYSB_WL04_OSN8800=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_S2352=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_HXLZX=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_ChinaIDS=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_IDSDB=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_NTS732=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_ESXI02=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_620r=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_ESXI04=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_TPLGK=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_ESXI03=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_ESXI01=%E6%AD%A3%E5%B8%B8&ZYSB_WL05_BKLZX=%E6%AD%A3%E5%B8%B8&ZYDK_WL03_NE40XG200=%E6%AD%A3%E5%B8%B8&ZYDK_WL03_NE40XG100=%E6%AD%A3%E5%B8%B8&ZYDK_WL04_OSN880015=%E6%AD%A3%E5%B8%B8&ZYDK_WL04_OSN88006=%E6%AD%A3%E5%B8%B8&ZYDK_WL04_OSN880013=%E6%AD%A3%E5%B8%B8&ZYDK_WL11_S6720XG001=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30006&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E7%BD%91%E7%BB%9C%E6%9C%BA%E6%88%BF%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                     wl[0], wl[1])],
        # 智慧城市  30005
        '智慧城市': [1.8,
                 'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_ZH=%E6%AD%A3%E5%B8%B8&WLSBQK_ZH=%E6%AD%A3%E5%B8%B8&JGMZT_ZH=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_ZH=%E6%AD%A3%E5%B8%B8&JFWD_ZH={}&JFSD_ZH={}&ZYSB_ZH01S5500=%E6%AD%A3%E5%B8%B8&ZYSB_ZH01IBMP550=%E6%AD%A3%E5%B8%B8&ZYSB_ZH027609=%E6%AD%A3%E5%B8%B8&ZYSB_ZH31S9306=%E6%AD%A3%E5%B8%B8&ZYDK_ZH02_7609E81=%E6%AD%A3%E5%B8%B8&ZYDK_ZH02_7609E91=%E6%AD%A3%E5%B8%B8&ZYDK_ZH30_S5120G0028=%E6%AD%A3%E5%B8%B8&ZYDK_ZH30_S5122G0028=%E6%AD%A3%E5%B8%B8&ZYDK_ZH31_S9306XG500=%E6%AD%A3%E5%B8%B8&ZYDK_ZH31_S9306XG200=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30005&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E6%99%BA%E6%85%A7%E6%9C%BA%E6%88%BF%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                     zh[0], zh[1])],
        # 机房2  30004
        '机房2': [3.6,
                'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_A=%E6%AD%A3%E5%B8%B8&WLSBQK_A=%E6%AD%A3%E5%B8%B8&JGMZT_A=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_A=%E6%AD%A3%E5%B8%B8&JFWD_A={}&JFSD_A={}&FWQQK_B=%E6%AD%A3%E5%B8%B8&WLSBQK_B=%E6%AD%A3%E5%B8%B8&JGMZT_B=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_B=%E6%AD%A3%E5%B8%B8&JFWD_B={}&JFSD_B={}&FWQQK_C=%E6%AD%A3%E5%B8%B8&WLSBQK_C=%E6%AD%A3%E5%B8%B8&JGMZT_C=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_C=%E6%AD%A3%E5%B8%B8&JFWD_C={}&JFSD_C={}&ZYSB_B15=%E6%AD%A3%E5%B8%B8&ZYSB_B17=%E6%AD%A3%E5%B8%B8&ZYSB_B18_S5120=%E6%AD%A3%E5%B8%B8&ZYSB_B18_VNX5500=%E6%AD%A3%E5%B8%B8&ZYSB_B19_VNXe3200=%E6%AD%A3%E5%B8%B8&ZYSB_B19_IBMP570=%E6%AD%A3%E5%B8%B8&ZYDK_B12=%E6%AD%A3%E5%B8%B8&ZYDK_B18_G0052=%E6%AD%A3%E5%B8%B8&ZYDK_B18_G0049=%E6%AD%A3%E5%B8%B8&ZYDK_A01_GE8=%E6%AD%A3%E5%B8%B8&ZYDK_A01_VX230=%E6%AD%A3%E5%B8%B8&ZYDK_A01_VX230=%E6%AD%A3%E5%B8%B8&ZYDK_A01_XG102=%E6%AD%A3%E5%B8%B8&ZYDK_A01_XG002=%E6%AD%A3%E5%B8%B8&ZYDK_A15_XG002=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30004&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E6%9C%BA%E6%88%BF2%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                    room2[0][0], room2[0][1], room2[1][0], room2[1][1], room2[2][0], room2[2][1])],
        # 机房3  30003
        '机房3': [1.4,
                'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_D=%E6%AD%A3%E5%B8%B8&WLSBQK_D=%E6%AD%A3%E5%B8%B8&JGMZT_D=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_D=%E6%AD%A3%E5%B8%B8&JFWD_D={}&JFSD_D={}&ZYSB_D01_DX=%E6%AD%A3%E5%B8%B8&ZYSB_D01_LT=%E6%AD%A3%E5%B8%B8&ZYDK_D01_DX_G1052=%E6%AD%A3%E5%B8%B8&ZYDK_D01_LT_G1052=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30003&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E6%9C%BA%E6%88%BF3%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                    room3[0], room3[1])],
        # 机房4  30002
        '机房4': [5,
                'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_E=%E6%AD%A3%E5%B8%B8&WLSBQK_E=%E6%AD%A3%E5%B8%B8&JGMZT_E=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_E=%E6%AD%A3%E5%B8%B8&JFWD_E={}&JFSD_E={}&FWQQK_F=%E6%AD%A3%E5%B8%B8&WLSBQK_F=%E6%AD%A3%E5%B8%B8&JGMZT_F=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_F=%E6%AD%A3%E5%B8%B8&JFWD_F={}&JFSD_F={}&FWQQK_G=%E6%AD%A3%E5%B8%B8&WLSBQK_G=%E6%AD%A3%E5%B8%B8&JGMZT_G=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_G=%E6%AD%A3%E5%B8%B8&JFWD_G={}&JFSD_G={}&FWQQK_H=%E6%AD%A3%E5%B8%B8&WLSBQK_H=%E6%AD%A3%E5%B8%B8&JGMZT_H=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_H=%E6%AD%A3%E5%B8%B8&JFWD_H={}&JFSD_H={}&FWQQK_I=%E6%AD%A3%E5%B8%B8&WLSBQK_I=%E6%AD%A3%E5%B8%B8&JGMZT_I=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_I=%E6%AD%A3%E5%B8%B8&JFWD_I={}&JFSD_I={}&FWQQK_J=%E6%AD%A3%E5%B8%B8&WLSBQK_J=%E6%AD%A3%E5%B8%B8&JGMZT_J=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_J=%E6%AD%A3%E5%B8%B8&JFWD_J={}&JFSD_J={}&ZYSB_I16=%E6%AD%A3%E5%B8%B8&ZYDK_E01_T2=%E6%AD%A3%E5%B8%B8&ZYDK_E01_T1=%E6%AD%A3%E5%B8%B8&ZYDK_H06_G011=%E6%AD%A3%E5%B8%B8&ZYDK_H06_G013=%E6%AD%A3%E5%B8%B8&ZYDK_H04_G0025=%E6%AD%A3%E5%B8%B8&ZYDK_I16_G1500=%E6%AD%A3%E5%B8%B8&ZYDK_I16_G2500=%E6%AD%A3%E5%B8%B8&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30002&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E6%9C%BA%E6%88%BF4%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                    room4[0][0], room4[0][1], room4[1][0], room4[1][1], room4[2][0], room4[2][1], room4[3][0], room4[3][1], room4[4][0], room4[4][1], room4[5][0], room4[5][1])],
        # 机房5  30001
        '机房5': [1.3,
                'QTLSQK=%E6%97%A0&JFHZQK=%E6%97%A0&FWQQK_K=%E6%AD%A3%E5%B8%B8&WLSBQK_K=%E6%AD%A3%E5%B8%B8&JGMZT_K=%E6%AD%A3%E5%B8%B8&PDU_LEDQK_K=%E6%AD%A3%E5%B8%B8&ZYSB=%E6%AD%A3%E5%B8%B8&ZYDK=%E6%AD%A3%E5%B8%B8&JFWD={}&JFSD={}&WSQK=%E8%89%AF%E5%A5%BD&ZTQK=%E6%AD%A3%E5%B8%B8&checkinfo=&prj_sn=hbywl&ins_no=30001&ins_name=%E6%9D%AD%E5%B7%9E%E7%BA%A2%E5%AE%9D%E4%BA%91%E7%BD%91%E8%BF%90%E9%83%A8-%E6%9C%BA%E6%88%BF%E4%BA%94%E5%B7%A1%E6%A3%80&username=%E5%90%B4%E5%AE%B6%E6%9D%B0&__cmd=inspection&__param=add&uploadimages='.format(
                    k[0], k[1])],
    }

    # 模拟 可能 不是准时开始 延迟-20 - 90秒  负数就准时开始
    time_sleep = random.randint(-20, 90)
    while time_sleep > 0:
        print('\r' + '将于{}秒 后开始...'.format(time_sleep), end='')  # \r 再打印 可以覆盖掉之前的
        time_sleep -= 1
        time.sleep(1)
    else:
        print('               ')  # 把之前的 延时倒计时 覆盖掉  变成空行  相当于\n

    # print('\n')
    print('{} 开始巡检'.format(timeee), '\n')

    # 模拟实际 按一定间隔 逐一发送巡检记录
    for name, data_list in data_dict.items():
        # 模拟所需花费的时间  将分转换为秒
        time_sleep = int(data_list[0] * random.randint(50, 70))

        # 倒计时
        while time_sleep > 0:
            print('\r' + '{} 巡检中 倒计时{}秒'.format(name, time_sleep), end='')  # \r 再打印 可以覆盖掉之前的
            time_sleep -= 1
            time.sleep(1)

        errormsg = send_record(data_list[1])
        print('\r' + name + ' ' + errormsg + '！         ')

    print('\n')
    print('{} 巡检结束'.format(timeee), '\n')

    return


if __name__ == '__main__':
    print('''复制 温湿度记录 至此,可定时自动推送
    需带时间!!
    输入完一个楼层后 :wq 退出,进入下一环节
    
    绝对不能输入错误信息,否则后果不明.
    ''')

    try:
        # 一楼温湿度
        data1_list = []
        while 1:
            input_ch = input('输入一楼温湿度：')
            if input_ch == ':wq':  # :wq 为停止符
                break
            elif input_ch == '':
                pass
            else:
                data1_list.append(input_ch)
        # 一楼温湿度 字典{time: data}
        d1 = {}
        for a1 in data1_list:
            # 如果时间长度为4 （1：30） 就在前面加上0 （01：30） 长度为5 （10：30） 就正常写入
            d1.update({a1[:5].strip() if len(a1[:5].strip()) == 5 else '0' + a1[:5].strip(): a1[5:].strip('\n').strip()})

        # 二楼温湿度
        data2_list = []
        while 1:
            input_ch = input('输入二楼温湿度：')
            if input_ch == ':wq':  # :wq 为停止符
                break
            elif input_ch == '':
                pass
            else:
                data2_list.append(input_ch)
        # 二楼温湿度 字典{time: data}
        d2 = {}
        for a2 in data2_list:
            # 如果时间长度为4 （1：30） 就在前面加上0 （01：30） 长度为5 （10：30） 就正常写入
            d2.update({a2[:5].strip() if len(a2[:5].strip()) == 5 else '0' + a2[:5].strip(): a2[5:].strip('\n').strip()})

        # 巡检时间列表
        t_list = ['08:45', '10:30', '12:30', '14:30', '16:10', '17:45', '19:30', '21:30', '23:30', '01:30', '03:30', '05:30', '07:30']
        # 产生 所有时间点的巡检动作 让之后的schedule.run_pending() 去逐一匹配
        for timing in t_list:
            # do 里的函数 参数直接跟后面,不能用括号() 不然报错!
            schedule.every().day.at(timing).do(xunjian_timing, d1, d2)

        print('\n')

        while True:
            # 每30s 检查一次是否该巡检了  有2种方法？？？
            schedule.run_pending()
            # schedule.run_all(delay_seconds=30)

            # 等待下一次巡检显示 倒计时30秒
            wait_time = 30
            while wait_time >= 0:
                print('\r' + '未到时间，等待{}s 后再检查'.format(wait_time), end='')
                wait_time -= 1
                time.sleep(1)

            # time.sleep(30)

    except KeyboardInterrupt:
        pass
    except Exception as ex:
        print(ex)

    # 推送后返回的信息
    # InspectionCB({"state":0, "errmsg": "成功", "insdata_id": 747, "time": "201907"})

    # schedule.every(10).minutes.do(job)
    # schedule.every().hour.do(job)
    # schedule.every().day.at("10:30").do(job)
    # schedule.every(5).to(10).days.do(job)
    # schedule.every().monday.do(job)
    # schedule.every().wednesday.at("13:15").do(job)


