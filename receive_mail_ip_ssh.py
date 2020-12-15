# -*- coding=utf-8 -*-

import poplib
import socket
import email
import base64
import paramiko
import time
import re
import ipaddress
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def decode_subject_base64(stre):
    # 解码如下内容
    # =?utf-8?b?6ZmE5Lu25rWL6K+VX+S4u+mimA==?=
    #   utf-8   6ZmE5Lu25rWL6K+VX+S4u+mimA==   (转码后为:附件测试_主题)
    # ['=?UTF-8?B?5pys5py6SVA6MTExLjIzLjE=?=\n =?UTF-8?B?NS4xMjPmuZbljZfnnIHplb/mspnluIIg56e75Yqo?=']  (怎么会有\n分段的)
    try:
        decoded_stre = ''
        for sss in stre.split('\n'):  # 解决有\n分段的问题
            re_result = re.match('=\?(.*)\?\w\?(.*)\?=', sss.strip()).groups()
            # re_result[0] 为编码方式
            middle = re_result[1]  # 提取base64的内容 6ZmE5Lu25rWL6K+VX+S4u+mimA==
            decoded = base64.b64decode(middle)  # 对内容进行base64解码
            decoded_stre += decoded.decode(re_result[0])  # 再对base64解码后内容,进行utf-8解码,转换为中文内容
    except Exception:
        decoded_stre = stre
    return decoded_stre


def send_mail(mailserver, username, password, From, To, Cc, Subj, Main_Body, tx, send_try=0):
    Tos = To.split(';')  # 把多个邮件接受者通过';'分开
    Ccs = Cc.split(';')  # 把多个邮件抄送者通过';'分开
    Date = email.utils.formatdate()  # 格式化邮件时间
    msg = MIMEMultipart()  # 产生MIME多部分的邮件信息
    msg["Subject"] = Subj  # 主题
    msg["From"] = From  # 发件人
    msg["To"] = To  # 收件人
    msg["Cc"] = Cc  # 抄送人
    msg["Date"] = Date  # 发件日期

    part = MIMEText(Main_Body)
    msg.attach(part)  # 添加正文

    # 只为表明能执行到这一行,定位log
    tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  发送中...", time.localtime()))
    try:
        server_send = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
        server_send.login(username, password)  # 通过用户名和密码登录邮件服务器
        failed = server_send.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件
        server_send.quit()  # 退出会话

        if failed:
            # 如果出现故障，写入故障原因！
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  Falied recipients: ", time.localtime()) + failed)
            return
        else:
            # 如果没有故障发生
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回信已经成功发出! TO: ", time.localtime()) + msg["To"])
            send_try = 0  # 重置尝试次数
            return
    except Exception as ex:
        # 发信时会话会被服务器干掉，原因不明，重试3次，还不行就跳过，继续下一封
        if re.search('Connection unexpectedly closed', str(ex)):
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  模块内部二次发送失败，waiting 15s' + '  send_try=' + str(send_try))
            send_try += 1
            # 重试3次
            if send_try >= 3:
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + '  模块内部二次发送失败 超过3次！')
                return
            else:
                time.sleep(15)
                send_mail(mailserver, username, password, From, To, Cc, Subj, Main_Body, tx, send_try=send_try)  # 递归调用 用 send_try 来解决死循环
                return
        else:
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(ex) + '  发信时有其他错误！')
            raise ex


def handle_full(filee):
    reset_cmd_list = [
                      'sys',
                      'policy interzone local untrust inbound',
                      'policy 9',
                      'undo policy source all',
                      'policy interzone local untrust outbound',
                      'policy 5',
                      'undo policy destination all',
                      '\n'
                      ]
    filee.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]   检测到策略已满，开始重置!", time.localtime()))
    multicmd_ssh('112.17.12.29', 'wujiajie', 'wujiajie@zmcc123', reset_cmd_list, filee, reset=True)


def check_ip_zmcc(addr, tx):
    per_list = [
        'policy source 223.93.164.169 0',
        'policy source 39.170.0.0 mask 16',
        'policy source 39.180.0.0 mask 16',
        'policy source 39.186.0.0 mask 16',
        'policy source 111.0.0.0 mask 16',
        'policy source 111.1.0.0 mask 16',
        'policy source 117.142.172.0 mask 24',
        'policy source 218.74.50.0 mask 24',
        'policy source 60.177.78.0 mask 24',
        'policy source 115.193.229.0 mask 24',
        'policy source 218.0.217.0 mask 24',
        'policy source 115.205.119.0 mask 24',
        'policy source 117.155.117.0 mask 24',
        'policy source 58.48.126.0 mask 24',
        'policy source 60.177.73.0 mask 24',
        'policy source 115.220.199.0 mask 24',
        'policy source 183.159.38.0 mask 24',
        'policy source 125.118.37.0 mask 24',
        'policy source 111.2.0.0 mask 16',
        'policy source 111.3.0.0 mask 16',
        'policy source 112.10.0.0 mask 16',
        'policy source 112.11.0.0 mask 16',
        'policy source 112.12.0.0 mask 16',
        'policy source 112.13.0.0 mask 16',
        'policy source 112.14.0.0 mask 16',
        'policy source 112.15.0.0 mask 16',
        'policy source 112.16.0.0 mask 16',
        'policy source 112.17.0.0 mask 16',
        'policy source 112.53.0.0 mask 16',
        'policy source 112.54.0.0 mask 16',
        'policy source 117.147.0.0 mask 16',
        'policy source 117.148.0.0 mask 16',
        'policy source 117.149.0.0 mask 16',
        'policy source 120.193.0.0 mask 16',
        'policy source 120.199.0.0 mask 16',
        'policy source 183.245.0.0 mask 16',
        'policy source 183.246.0.0 mask 16',
        'policy source 183.247.0.0 mask 16',
        'policy source 183.248.0.0 mask 16',
        'policy source 183.249.0.0 mask 16',
        'policy source 211.140.0.0 mask 16',
        'policy source 211.138.0.0 mask 16',
        'policy source 218.205.0.0 mask 16',
        'policy source 221.131.0.0 mask 16',
        'policy source 223.92.0.0 mask 16',
        'policy source 117.142.238.0 mask 23',
        'policy source 117.142.240.0 mask 23',
        'policy source 221.177.56.0 mask 21',
        'policy source 221.177.228.0 mask 22',
        'policy source 117.142.16.0 mask 23',
        'policy source 223.103.0.0 mask 24',
        'policy source 223.104.0.0 mask 24',
        'policy source 223.103.46.0 mask 24',
        'policy source 223.103.47.0 mask 24',
        'policy source 223.103.48.0 mask 24',
        'policy source 223.103.49.0 mask 24',
        'policy source 117.142.167.0 mask 24',
        'policy source 117.142.168.0 mask 24',
        'policy source 117.142.169.0 mask 24',
        'policy source 117.142.170.0 mask 24',
        'policy source 117.142.171.0 mask 24',
        'policy source 60.177.74.144 0',
        'policy source 219.142.131.194 0',
        'policy source 115.204.224.83 0',
        'policy source 115.204.224.0 mask 24',
        'policy source 115.199.158.0 mask 24',
        'policy source 219.140.248.0 mask 24',
        'policy source 183.157.19.0 mask 24',
        'policy source 120.227.0.0 mask 16',
        'policy source 125.121.33.0 mask 24',
        'policy source 223.93.170.0 mask 24',
        'policy source 39.171.0.0 mask 16',
        'policy source 39.172.0.0 mask 16',
        'policy source 39.173.0.0 mask 16',
        'policy source 39.174.0.0 mask 16',
        'policy source 39.175.0.0 mask 16',
        'policy source 39.181.0.0 mask 16',
        'policy source 39.182.0.0 mask 16',
        'policy source 39.183.0.0 mask 16',
        'policy source 39.184.0.0 mask 16',
        'policy source 39.185.0.0 mask 16',
        'policy source 39.187.0.0 mask 16',
        'policy source 39.188.0.0 mask 16',
        'policy source 39.189.0.0 mask 16',
        'policy source 39.190.0.0 mask 16',
        'policy source 39.191.0.0 mask 16',
        'policy source 117.136.0.0 mask 16',
        'policy source 61.158.0.0 mask 16',
        'policy source 120.242.0.0 mask 16',
        'policy source 60.222.0.0 mask 16',
        'policy source 155.213.0.0 mask 16',
        'policy source 125.122.217.0 mask 24',
        'policy source 60.186.33.0 mask 24',
        'policy source 220.191.107.0 mask 24',
        'policy source 183.157.20.0 mask 24',
        'policy source 110.53.0.0 mask 16',
        'policy source 223.104.0.0 mask 16',
        'policy source 218.0.219.0 mask 24',
        'policy source 115.197.233.0 mask 24',
        'policy source 58.217.16.0 mask 24',
        'policy source 60.177.77.0 mask 24',
        'policy source 36.63.154.0 mask 24',
        'policy source 36.63.155.0 mask 24',
        'policy source 117.155.112.0 mask 24',
        'policy source 36.6.199.0 mask 24',
        'policy source 60.177.54.0 mask 24',
        'policy source 117.155.123.0 mask 24',
        'policy source 125.120.123.0 mask 24',
        'policy source 60.186.32.0 mask 24',
        'policy source 60.186.115.0 mask 24',
        'policy source 125.120.90.0 mask 24',
        'policy source 125.122.182.0 mask 24',
        'policy source 122.234.0.0 mask 16',
        'policy source 218.109.0.0 mask 16',
        'policy source 122.235.230.0 mask 24',
        'policy source 61.153.126.0 mask 24',
        'policy source 60.177.60.0 mask 24',
        'policy source 115.193.23.0 mask 24',
        'policy source 125.120.88.0 mask 24',
        'policy source 60.176.0.0 mask 16',
        'policy source 220.184.0.0 mask 16',
        'policy source 115.196.0.0 mask 16',
        'policy source 58.100.107.0 mask 24',
        'policy source 115.206.245.0 mask 24',
        'policy source 58.101.0.0 mask 16',
    ]

    add_list = []

    for ev_comm in per_list:
        if re.search('mask', ev_comm):
            add = ev_comm.replace('policy source ', '').replace(' mask ', '/').strip()
        else:
            add = ev_comm.replace('policy source ', '').replace(' 0', '').strip()
        add_list.append(add)
    for ev_addr in add_list:
        if ipaddress.ip_address(addr) in ipaddress.ip_network(ev_addr):
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  是浙江移动地址，无需添加')
            return 'include zmcc'
    return 'need to be added'


def kaifang(mail_dict, mail_number, tx, addr):
    # 补全命令（放开一个C）
    li1 = [
           'sys',
           'policy interzone local untrust inbound',
           'policy 9',
           'action permit',
           'policy source ' + addr + ' mask 24',
           'policy interzone local untrust outbound',
           'policy 5',
           'action permit',
           'policy destination ' + addr + ' mask 24',
           '\n'
          ]
    # -----------------------------------------------------------------------
    try:
        # 开始ssh执行命令，并且发回信
        reset_status = start_ssh(li1, tx, addr, mail_dict)

        # 根据是否有重置策略，决定读不读下一封
        if reset_status == 'reset':
            # 已重置策略，继续执行本封邮件
            pass
        else:
            # 下一封
            mail_number += 1
            try_number = 0  # 重置超时尝试次数
    # -----------------------------------------------------------------------
    # ssh连接超时（第一次）懒的写了，就复制吧
    except socket.timeout:
        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  失败 ssh连接超时1次')
        time.sleep(10)
        try:
            # 开始ssh执行命令，并且发回信
            reset_status = start_ssh(li1, tx, addr, mail_dict)

            # 根据是否有重置策略，决定读不读下一封
            if reset_status == 'reset':
                # 已重置策略，继续执行本封邮件
                pass
            else:
                # 下一封
                mail_number += 1
                try_number = 0  # 重置超时尝试次数

        # ssh连接超时（第二次）退出
        except socket.timeout:
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  失败 ssh连接超时2次')
            return mail_number
        # 用户名密码错误
        except paramiko.ssh_exception.AuthenticationException:
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  失败 ssh用户名密码错误')
            return mail_number
    # ----------------------------------------------------------------------

    # 用户名密码错误
    except paramiko.ssh_exception.AuthenticationException:
        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  失败 ssh用户名密码错误')
        return mail_number

    return mail_number


def multicmd_ssh(ip, username, password, cmd_list, fil, reset=False, verbose=True):
    ssh = paramiko.SSHClient()  # 创建SSH Client
    ssh.load_system_host_keys()  # 加载系统SSH密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
    # 修改 allow_agent=False, look_for_keys=False ，默认为true 可能会在某些服务器上导致 AuthenticationException: Authentication failed.
    ssh.connect(ip, port=22, username=username, password=password, timeout=10, compress=True, allow_agent=False, look_for_keys=False)  # SSH连接

    chan = ssh.invoke_shell()  # 激活交互式shell
    x = chan.recv(40960).decode()  # 先读一次回显，不然回显会累计
    time.sleep(2)

    for cmd in cmd_list:  # 读取命令
        chan.send(cmd.encode())  # 执行命令，注意字串都需要编码为二进制字串
        chan.send(b'\n')  # 一定要注意输入回车
        x = chan.recv(40960).decode()  # 读取回显，有些回显可能过长，请把接收缓存调大
        fil.write(x)  # 将回显写入
        time.sleep(1)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间

        # 如果检测到已存在，就停止 并回信已存在
        if re.search('Error: Address item conflicts', x):
            chan.close()  # 退出交互式shell
            ssh.close()  # 退出ssh会话
            return 'exists'

        # 如果检测到策略已满，就停止 并自动重置策略
        if re.search('Error: The address items are full', x):
            chan.close()  # 退出交互式shell
            ssh.close()  # 退出ssh会话
            handle_full(fil)  # 执行重置
            reset = True  # 不清楚上面调用完后 reset的状态，手动设定一下
            # return 'full'

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话

    if reset:  # 判断是否在重置策略
        return 'reset_successfully'
    else:
        return 'good'


def start_ssh(li1, tx, addr, mail_dict):
    # ssh登陆设备 敲命令
    ret = multicmd_ssh('112.17.12.29', 'wujiajie', 'wujiajie@zmcc123', li1, tx)
    respond_dict = {
                    'good': ['[自动回复] 石桥VPN添加地址成功!', '成功添加!'],
                    'exists': ['[自动回复] 石桥VPN添加地址异常!', '已存在，无需添加!'],
                    'full': ['[自动回复] 石桥VPN添加地址失败!', '因策略已满，无法添加。请联系我!'],
                    'reset_successfully': ['自动重置策略成功!', '检测到策略已满，自动重置成功!']
                    }
    # 根据命令执行的状态 选择回信内容
    respond_mode = respond_dict[ret]

    # 发送邮件告知添加成功
    if ret == 'reset_successfully':  # 自动重置策略
        try:
            send_mail('smtp.js-datacraft.com',
                      'jj.wu@datatech-info.com',
                      'luCKi1y18894',
                      '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                      '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                      '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                      respond_mode[0],
                      time.strftime("[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + respond_mode[1],
                      tx)

        # Connection unexpectedly closed 连不上邮箱smtp??  10秒后再重试一次(但不论最终成功否，都会继续读下一封)
        except Exception as ee:
            if re.match('Connection unexpectedly closed', str(ee)):
                time.sleep(10)
                send_mail('smtp.js-datacraft.com',
                          'jj.wu@datatech-info.com',
                          'luCKi1y18894',
                          '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                          '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                          '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                          respond_mode[0],
                          time.strftime("[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + respond_mode[1],
                          tx)
            else:
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回复邮件发送失败，reason= ", time.localtime()) + str(ee))
        return 'reset'

    else:  # 其他正常情况
        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '   compelete!!')
        # 如果是已存在的情况，就不在 saved_addr.txt 中写入
        if ret != 'exists':
            with open('/root/saved_addr.txt', 'a') as f:
                # f.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + addr + '  From:' + mail_dict['fr'])
                # 对齐下格式
                f.write('\n{}  {:<15}  From: {}'.format(time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()), addr, mail_dict['fr']))
        try:
            send_mail('smtp.js-datacraft.com',
                      'jj.wu@datatech-info.com',
                      'luCKi1y18894',
                      '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                      mail_dict['From'],  # 收信人
                      '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                      respond_mode[0],
                      '您好' + mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + addr + respond_mode[1],
                      tx)

        # Connection unexpectedly closed 连不上邮箱smtp??  10秒后再重试一次(但不论最终成功否，都会继续读下一封)
        except Exception as ee:
            if re.match('Connection unexpectedly closed', str(ee)):
                time.sleep(10)
                send_mail('smtp.js-datacraft.com',
                          'jj.wu@datatech-info.com',
                          'luCKi1y18894',
                          '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                          mail_dict['From'],  # 收信人
                          '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                          respond_mode[0],
                          '您好' + mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + addr + respond_mode[1],
                          tx)
            else:
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  回复邮件发送失败，reason= ", time.localtime()) + str(ee))

        # 删除邮件(预留)False  应该可以使用(并不行..)
        # if delete_email:
        #     server.dele(49 + mail_number)
        #     return

        return 'normal'


# 新增操作
def choose_action(mail_dict, tx, ):

    # 石桥VPN开关
    # vpn_status = ''
    # if re.search('石桥VPN状态.*(关闭|开启).*', mail_dict['Subject']).groups():
    #     vpn_status = str(re.search('石桥VPN状态.*(关闭|开启).*', mail_dict['Subject']).groups()[0])

    # 增加石桥现场mac
    # 几种mac格式  BC:5F:F4:6B:3E:6F / BC-5F-F4-6B-3E-6F / BC5F:F46B:3E6F / BC5F-F46B-3E6F
    mac_addr = re.search('(([0-9A-F]{2,4}[:-]){2,5}[0-9A-F]{2,4})', mail_dict['Subject'], re.I)
    if mac_addr:
        if re.search(':', mac_addr.groups()[0]):  # 匹配是:号
            sp = mac_addr.groups()[0].split(':')  # 以:号分开，检查是分成了3个还是6个
            if len(sp) == 3:  # 3个就是正常格式，修改连接符号即可
                hw_mac = '-'.join(sp)
                return hw_mac
            elif len(sp) == 6:  # 6个就需要两两合并，并修改连接符号
                hw_mac = '-'.join([sp[0] + sp[1], sp[2] + sp[3], sp[4] + sp[5]])
                return hw_mac
        elif re.search('-', mac_addr.groups()[0]):  # 匹配是-号
            sp = mac_addr.groups()[0].split('-')  # 以-号分开，检查是分成了3个还是6个
            if len(sp) == 3:  # 3个就是正常格式，加回连接符即可
                hw_mac = '-'.join(sp)
                return hw_mac
            elif len(sp) == 6:  # 6个就需要两两合并，并加上连接符
                hw_mac = '-'.join([sp[0] + sp[1], sp[2] + sp[3], sp[4] + sp[5]])
                return hw_mac
        else:
            tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  mac格式有误!  ", time.localtime()) + mac_addr.groups()[0])
    else:
        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  无mac匹配!", time.localtime()))

    # 如果不是上面的操作，就继续进行老的添加地址流程
    return


def recive_mail(mailserver, mailuser, mailpasswd, mail_number, try_number, delete_email=False):
    with open('/root/ssh_mail_log.txt', 'a') as tx:
        try:
            server = poplib.POP3_SSL(mailserver, 995)  # 连接到邮件服务器
            server.user(mailuser)  # 邮件服务器用户名
            server.pass_(mailpasswd)  # 邮件服务器密码
            # POP3对行长度做了限制，默认为_MAXLINE = 2048，故若是邮件超过此长度就会提示“poplib.error_proto: line too long”。解决方案：在读取邮件代码中重新定义最大行长度，即给poplib._MAXLINE设置新值。
            poplib._MAXLINE = 20480

            # 打印服务器欢迎信息
            tx.write(time.strftime("\n\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(server.getwelcome()))
            while 1:
                try:
                    hdr, message, octets = server.retr(115 + mail_number)  # 读取邮件（从最早的第一封开始的第几封）
                    str_message = email.message_from_bytes(b'\n'.join(message))  # 把邮件内容拼接到大字符串
                    part_list = []
                    mail_dict = {}
                    for part in str_message.walk():  # 把邮件的多个部分添加到part_list
                        part_list.append(part)
                    # 把邮件的第一个[0]部分内容提取出来写入字典mail_dict
                    # 注意第一部分,所有邮件都会存在,是邮件的头部信息
                    for header_name, header_content in part_list[0].items():
                        if header_name == 'Subject':
                            mail_dict[header_name] = decode_subject_base64(header_content)  # base64解码Subject
                        elif header_name == 'From':
                            mail_dict[header_name] = header_content  # base64解码Subject
                            # 如果发件人没改显示名称或名称不为中文，则mail_dict['fro'] = "lee--jie@139.com" <lee--jie@139.com>(样例)
                            # 将发件人名称手动抓取出来，mail_dict['fro']在回信中调用了，新建mail_dict['fr']，用于代码log 和 回信内的显示
                            if re.match('".*" <.*>', header_content):
                                mail_dict['fro'] = re.match('"(.*)" <.*>', header_content).groups()[0]  # 把带有双引号 ".*" 的去掉引号
                            elif re.match('.*<.*>', header_content):
                                mail_dict['fro'] = re.match('(.*)<.*>', header_content).groups()[0]  # 提取 <> 前面的:样例15103220375<15103220375@139.com>
                            else:
                                mail_dict['fro'] = header_content
                            mail_dict['fr'] = decode_subject_base64(mail_dict['fro'])  # 添加解码后的发件人名，方便后面读取
                            mail_dict['mail_address'] = re.match('.*<(.*)>', header_content).groups()[0]  # 添加发件人邮箱地址，方便限制发件人
                        else:
                            mail_dict[header_name] = header_content

                    # 写入 谁发的邮件，标题
                    tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  From: ", time.localtime()) + mail_dict['fr'] + '  标题: ' + mail_dict['Subject'])

                    # 黑名单/白名单 限制加至此，读取txt内的黑/白名单数据，与信中的发件人邮箱<.*>匹配，命中则做相应操作。
                    # 黑/白名单：所有人的139、达科邮箱。
                    # 发邮件：请求添加执行白名单 ，回信：已添加，可以进行增加拨vpn地址操作。
                    # 写入 谁发的邮件，拒绝/允许
                    with open('/root/black_white_list.txt', 'r') as ff:
                        nane_list = ff.readlines()
                    permit_list = []
                    for person in nane_list:
                        permit_list.append(person.strip('\n'))

                    # # =================新增操作===================后续都在此按这个模板增加吧
                    # mac_addr = choose_action(mail_dict, tx)
                    # if mac_addr:
                    #     try:
                    #         #  先判断是否在白名单中
                    #         if mail_dict['mail_address'] in permit_list:
                    #             # 若在白名单里的人，可执行操作
                    #             mail_number = ...  # 添加 SW62 acl4000 mac 的操作，考虑单独起函数操作
                    #         else:
                    #             # 不在白名单里的人，不给加
                    #             tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + mail_dict['mail_address'] + '  不在白名单中!')
                    #             mail_number += 1
                    #             return mail_number
                    #     except Exception:
                    #         ...
                    # # =================新增操作===================后续都在此按这个模板增加吧

                    # ==============添加VPN地址 块================如有需要，直接单独做函数
                    # 获取邮件标题中的 ip:xxx.xxx.xxx.xxx 读出需求的地址
                    addr = str(ipaddress.ip_address(re.search('((\d{1,3}\.){3}\d{1,3})', mail_dict['Subject']).groups()[0]))

                    if mail_dict['mail_address'] in permit_list:
                        zmcc_status = check_ip_zmcc(addr, tx)  # 检查是否是浙江移动的地址 policy 4
                        # 若就是浙江移动地址，怼！
                        if zmcc_status == 'include zmcc':
                            mail_number += 1
                            send_mail('smtp.js-datacraft.com',
                                      'jj.wu@datatech-info.com',
                                      'luCKi1y18894',
                                      '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                                      mail_dict['From'],  # 收信人
                                      '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                                      '[自动回复] 石桥VPN拒绝添加地址!',
                                      '您好' + mail_dict['fr'] + time.strftime(":\n     [%Y-%m-%d %H:%M:%S]  您的地址", time.localtime()) + addr + '就是浙江移动地址，不用添加！\n 就不能先试一下吗',
                                      tx)
                        else:  # zmcc_status == 'need to be added'
                            # 若在白名单里的人，可执行操作，已添加命令act per
                            mail_number = kaifang(mail_dict, mail_number, tx, addr)
                            # server.dele(103 + mail_number)  # 操作完成，删除本封邮件(省的我手动删除)
                    else:
                        # 不在白名单里的人，不给加
                        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + mail_dict['mail_address'] + '  不在白名单中!')
                        mail_number += 1
                        return mail_number

                # IP地址格式有误 298.1.1.1 (样例)
                except ValueError as ee:
                    if re.findall('does not appear to be an IPv4 or IPv6 address', str(ee)):
                        tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  地址有误!", time.localtime()))
                        mail_number += 1
                # 标题不能匹配，下一个
                except AttributeError:
                    time.sleep(2)
                    mail_number += 1
                # ==============添加VPN地址 块================如有需要，直接单独做函数

                # 这一轮已经读完，退出等下一轮
                except poplib.error_proto:
                    server.quit()  # 退出服务器
                    break
                except KeyboardInterrupt:
                    server.quit()  # 退出服务器
                    break

            return mail_number

        # 连接邮件服务器超时 重试3次
        except socket.gaierror:
            if try_number < 3:
                tx.close()  # 先关了，不然又重复打开
                time.sleep(5)
                try_number += 1
                mail_number = recive_mail('pop3.js-datacraft.com', 'jj.wu@datatech-info.com', 'luCKi1y18894', mail_number, try_number, delete_email=False)
                return mail_number
            else:
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  本轮连接服务器已超时3次", time.localtime()))
                return mail_number

        # ----------------------------------------需测试就把下面的注释掉----------------------------------------------------
        # 其他错误，防崩(此处重要，尽量别崩在这！)  但不会读下一封(更新标题为空，下一封。为什么有SB这么发！)
        except Exception as exce:
            if re.match('\'Subject\'', str(exce)):
                mail_number += 1
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  标题为空!", time.localtime()))
                return mail_number

            # 这个问题的原因暂不明 连接邮箱服务器时偶尔会有此报错
            elif re.search('Connection reset by peer', str(exce)):
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(exce) + ' mail_number=' + str(mail_number))
                return mail_number

            # 发送的时候会有超时后30s模块内部重试？？第二次发送时，可能会产生此报错；本次回复邮件发不出就算了，继续下一封
            elif re.search('Connection unexpectedly closed', str(exce)):
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(exce) + ' mail_number=' + str(mail_number) + '  模块内部二次发送失败，waiting 15s')
                mail_number += 1
                return mail_number

            # 其他问题，发邮件通知我
            else:
                tx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(exce) + ' mail_number=' + str(mail_number))
                mail_number += 1
                try:
                    send_mail('smtp.js-datacraft.com',
                              'jj.wu@datatech-info.com',
                              'luCKi1y18894',
                              '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                              '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                              '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                              '代码捕获其他错误!',
                              time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(exce),
                              tx)
                except Exception as ee:
                    if re.search('Connection unexpectedly closed', str(ee)):
                        time.sleep(10)
                        send_mail('smtp.js-datacraft.com',
                                  'jj.wu@datatech-info.com',
                                  'luCKi1y18894',
                                  '=?GB2312?B?zuK80r3cLbTvv8Y=?= <jj.wu@datatech-info.com>',
                                  '=?GB2312?B?zuK80r3c?= <18368868186@139.com>',  # 收信人
                                  '=?GB2312?B?zuK80r3cLUND?= <185686792@qq.com>',  # 抄送
                                  '代码捕获其他错误!',
                                  time.strftime("\n     [%Y-%m-%d %H:%M:%S]  ", time.localtime()) + str(exce),
                                  tx)
                return mail_number
        # ----------------------------------------需测试就把上面的注释掉----------------------------------------------------

        # 手动 退出文件编辑，防止日志丢失
        finally:
            tx.close()


if __name__ == '__main__':
    mail_number = 0
    try_number = 0
    while 1:
        mail_number = recive_mail('pop3.js-datacraft.com', 'jj.wu@datatech-info.com', 'luCKi1y18894', mail_number, try_number, delete_email=False)
        with open('/root/ssh_mail_log.txt', 'a') as txx:
            txx.write(time.strftime("\n[%Y-%m-%d %H:%M:%S]  next round and wait 150s   mail_number=", time.localtime()) + str(mail_number))
        time.sleep(90)  # 每1分半 重新查看一遍邮箱

    # ---------------------测试区---------------------------------------
    # 'datatech-info.com' 新域名
    # 'pop.qq.com', '185686792@qq.com', 'purmejwztybrbifd'

    # a = '本机IP: 120.193.10.242浙江省杭州市 移动'
    # addr = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', a).groups()[0]
    # print(addr)

    # addr = ['122.234.156.116',
    #         ]
    #
    # for asd in addr:
    #     li1 = ['sys',
    #            'policy interzone local untrust in',
    #            'policy 8',
    #            'policy source ' + asd + ' mask 24',
    #            'policy interzone local untrust out',
    #            'policy 4',
    #            'policy destination ' + asd + ' mask 24',
    #            ]
    #
    #     with open('C:\\Users\\18568\\Desktop\\ssh_mail_log.txt', 'a') as tx:
    #         # ssh登陆设备 敲命令
    #         multicmd_ssh('112.17.12.29', 'wujiajie', 'wujiajie@zmcc123', li1, tx)
    #         print(asd + '   compelete!!')

