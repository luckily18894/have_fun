# -*- coding=utf-8 -*-

import poplib, getpass, sys
import email
import base64
import paramiko
import time
import re


def decode_subject_base64(str):
    # 解码如下内容
    # =?utf-8?b?6ZmE5Lu25rWL6K+VX+S4u+mimA==?=
    #   utf-8   6ZmE5Lu25rWL6K+VX+S4u+mimA== (转码后为:附件测试_主题)
    try:
        re_result = re.match('=\?(.*)\?\w\?(.*)\?=', str).groups()
        # re_result[0] 为编码方式
        middle = re_result[1]  # 提取base64的内容 6ZmE5Lu25rWL6K+VX+S4u+mimA==
        decoded = base64.b64decode(middle)  # 对内容进行base64解码
        decoded_str = decoded.decode(re_result[0])  # 再对base64解码后内容,进行utf-8解码,转换为中文内容
    except Exception:
        decoded_str = str
    return decoded_str


def multicmd_ssh(ip, username, password, cmd_list, verbose=True):
    ssh = paramiko.SSHClient()  # 创建SSH Client
    ssh.load_system_host_keys()  # 加载系统SSH密钥
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 添加新的SSH密钥
    # 修改 allow_agent=False, look_for_keys=False ，默认为true 可能会在某些服务器上导致 AuthenticationException: Authentication failed.
    ssh.connect(ip, port=22, username=username, password=password, timeout=5, compress=True, allow_agent=False, look_for_keys=False)  # SSH连接

    chan = ssh.invoke_shell()  # 激活交互式shell
    time.sleep(1)

    for cmd in cmd_list:  # 读取命令
        chan.send(cmd.encode())  # 执行命令，注意字串都需要编码为二进制字串
        chan.send(b'\n')  # 一定要注意输入回车
        time.sleep(1)  # 由于有些回显可能过长，所以可以考虑等待更长一些时间

    chan.close()  # 退出交互式shell
    ssh.close()  # 退出ssh会话


def recive_mail(mailserver, mailuser, mailpasswd, mail_number, delete_email=False):
    server = poplib.POP3_SSL(mailserver, 995)  # 连接到邮件服务器
    server.user(mailuser)  # 邮件服务器用户名
    server.pass_(mailpasswd)  # 邮件服务器密码

    while 1:
        try:
            print(server.getwelcome())  # 打印服务器欢迎信息
            # msgCount, msgBytes = server.stat()  # 查询邮件数量与字节数
            hdr, message, octets = server.retr(48 + mail_number)  # 读取邮件（从最早的第一封开始的第几封）
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
                else:
                    mail_dict[header_name] = header_content

            # 初始化附件为空列表
            mail_dict['Attachment'] = []
            mail_dict['Images'] = []
            print(mail_dict['Subject'])

            # 获取邮件标题中的 ip:xxx.xxx.xxx.xxx 读出需求的地址
            addr = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', mail_dict['Subject']).groups()[0]
            # 补全命令（放开一个C）
            li1 = ['sys',
                   'policy interzone local untrust in',
                   'policy 8',
                   'policy source ' + addr + ' mask 24',
                   'policy interzone local untrust out',
                   'policy 4',
                   'policy destination ' + addr + ' mask 24']
            # ssh登陆设备 敲命令
            multicmd_ssh('112.17.12.29', 'wujiajie', 'wujiajie@zmcc123', li1)
            print(addr + '   compelete!!')

            with open('/root/saved_addr.txt', 'a') as f:
                f.write(addr + '\n\r')

            # 下一封
            mail_number += 1

            # 删除邮件(预留)False  应该可以使用
            if delete_email:
                server.dele(48 + mail_number)
                return

        # 标题不能匹配，下一个
        except AttributeError:
            time.sleep(2)
            mail_number += 1
        # 这一轮已经读完，退出等下一轮
        except poplib.error_proto:
            server.quit()  # 退出服务器
            break
        except KeyboardInterrupt:
            server.quit()  # 退出服务器
            break

    return mail_number


if __name__ == '__main__':
    mail_number = 0
    while 1:
        mail_number = recive_mail('pop3.js-datacraft.com', 'jj.wu@js-datacraft.com', 'luCKi1y18894', mail_number, delete_email=False)
        print('next round wait 150s')
        time.sleep(150)  # 每2分半 重新查看一遍邮箱

    # a = '本机IP: 120.193.10.242浙江省杭州市 移动'
    # addr = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', a).groups()[0]
    # print(addr)

    # addr = ['223.104.160.79',
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
    #     # ssh登陆设备 敲命令
    #     multicmd_ssh('112.17.12.29', 'wujiajie', 'wujiajie@zmcc123', li1)
    #     print(asd + '   compelete!!')


