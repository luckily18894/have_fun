# -*- coding=utf-8 -*-

import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import re
import time


def send_mail(mailserver, username, password, From, To, Subj, Main_Body, Cc, files=None):
    # 使用SSL加密SMTP发送邮件, 此函数发送的邮件有主题,有正文,还可以发送附件
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

    if files:  # 如果存在附件文件
        for file in files:  # 逐个读取文件,并添加到附件
            real_filename = re.findall('.*\\\\(.*\.xls.*)', file)[0]  # 取得真实的文件名，不然就是文件路径，很难看
            # print(real_filename)
            part = MIMEApplication(open(file, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=real_filename)
            msg.attach(part)

    print('发送中...', '\n')
    server = smtplib.SMTP_SSL(mailserver, 465)  # 连接邮件服务器
    server.login(username, password)  # 通过用户名和密码登录邮件服务器

    # failed = server.sendmail(From, Tos + Ccs, msg.as_string())  # 发送邮件 (有抄送)
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

    # to = input()

    send_mail('smtp.139.com',  # mailsever
              '18368868186@139.com',  # username
              'luCKi1y18894',  # password

              '18368868186@139.com',  # from
              '185686792@qq.com',  # to(s)

              'test',  # 标题

              """亲爱的领导，亲爱的同事们：
                                  本人吴家杰，部门是IDC运营中心技术部，职位是网络工程师，已于2019年8月26日（星期一）正式到岗。此邮箱为联系邮箱，电话：18702592775。初来乍到，希望各部门领导和同事能多多指导关照。
                 吴家杰""",  # 内容

              Cc='',  # 抄送
              files=None  # 附件
              )

    # 倒计时
    countdown = 3
    while True:
        if countdown > 0:
            print('\r' + '将在{}秒后自动退出！！'.format(countdown), end='')  # \r 再打印 可以覆盖掉之前的
            countdown -= 1
            time.sleep(1)
        else:
            break




