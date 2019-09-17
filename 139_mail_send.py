# -*- coding=utf-8 -*-

import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re
import time


def send_mail(mailserver, username, password, From, To, Subj, Main_Body, Cc, files):
    # 使用SSL加密SMTP发送邮件, 此函数发送的邮件有主题,有正文,还可以发送附件
    Tos = To.split(';')  # 把多个邮件接受者通过';'分开
    if Cc != '':
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

    if files:  # 如果存在附件文件
        for file in files:  # 逐个读取文件,并添加到附件
            real_filename = re.findall('.*/(.*\.\w+)', file)[0]  # 取得真实的文件名，不然就是文件路径，很难看
            # print(real_filename)
            part = MIMEApplication(open(file, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=real_filename)
            msg.attach(part)

    print('发送中...', '\n')
    server = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
    server.login(username, password)  # 通过用户名和密码登录邮件服务器

    if Cc != '':
        failed = server.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件 (有抄送)
    else:
        failed = server.sendmail(From, Tos, msg.as_string())  # 发送邮件 (无抄送)

    server.quit()  # 退出会话
    if failed:
        print('Falied recipients:', failed)  # 如果出现故障，打印故障原因！
        return
    else:
        print('邮件已经成功发出！！！', '\n')  # 如果没有故障发生
        return


if __name__ == '__main__':
    # 使用Linux解释器 & WIN解释器

    print("""结束输入请使用 :wq  
    """)

    # 收件人
    to_list = []
    while 1:
        to_s = input('发送给：')
        if to_s == ':wq':  # :wq 为停止符
            break
        elif to_s == '':
            pass
        else:
            to_list.append(to_s)
    to = ';'.join(to_list)

    # 抄送人
    cc_list = []
    while 1:
        cc_s = input('抄送给：')
        if cc_s == ':wq':  # :wq 为停止符
            break
        elif cc_s == '':
            pass
        else:
            cc_list.append(cc_s)
    cc = ';'.join(cc_list)

    # 标题
    while 1:
        sub_s = input('标题：')
        if sub_s == '':
            pass
        else:
            sub = sub_s
            break

    # 正文
    body_list = []
    while 1:
        body_s = input('正文：')
        if body_s == ':wq':  # :wq 为停止符
            break
        elif body_s == '':
            pass
        else:
            body_list.append(body_s)
    body = '\n'.join(body_list)

    # 签名
    signature = """

——————————————————————————————————————
吴家杰

※※※※※※※※※※※※※※※※※※※※※※※※※※ 
中国移动通信集团浙江有限公司IDC运营中心
个人手机：18368868186
个人邮箱：18368868186@139.com
服务热线：4001100867
服务QQ：4001100867
微信公众号：浙江移动IDC
地址：杭州市下城区华西街330号
"""

    # 附件
    file_list = []
    while 1:
        file_s = input('附件路径：')
        if file_s == ':wq':  # :wq 为停止符
            break
        elif file_s == '':
            pass
        else:
            file_list.append(file_s)

    # 开始发送
    send_mail('smtp.139.com',  # mailsever
              '18368868186@139.com',  # username
              'luCKi1y18894',  # password
              '18368868186@139.com',  # from

              to,  # to(s)
              sub,  # 标题
              body + signature,  # 内容
              cc,  # 抄送
              file_list  # 附件

              )

    # 倒计时
    countdown = 2
    while True:
        if countdown >= 0:
            print('\r' + '将在{}秒后自动退出！！！'.format(countdown), end='')  # \r 再打印 可以覆盖掉之前的
            countdown -= 1
            time.sleep(1)
        else:
            break




