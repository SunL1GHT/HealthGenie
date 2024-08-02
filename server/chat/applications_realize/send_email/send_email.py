# coding=utf-8

import os
import smtplib
from email.mime.text import MIMEText
from chat import utils

from loguru import logger

# 找到当前.py文件绝对路径
root = os.path.dirname(__file__)

account_numbers = utils.load_json_from_file(root + '/conf/account_numbers.json')
settings = utils.load_json_from_file(root + '/../../conf/settings.json')

SENDER = 'uibot_server@163.com'
PASSWORD = 'HDFCQJYGZNPKBEEP'


class SendEmail:
    """
    发送邮件
    """

    @staticmethod
    def send_email_to_user(subject: str, text: str):
        """
        发送邮件
        :param subject: 主题
        :param text: 内容
        :return: 邮件是否成功发送的描述信息
        """

        try_num = settings['universal_set']['try_num']
        while True:
            try:
                msg = MIMEText(text, 'plain')
                msg['Subject'] = subject
                msg['From'] = SENDER
                msg['To'] = account_numbers['1']

                server = smtplib.SMTP('smtp.163.com')
                server.login(SENDER, PASSWORD)
                server.send_message(msg)
                server.quit()
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    return {
                        "message": "发送邮件失败，原因未知！"
                    }
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue

        return {
            "message": "成功发送邮件！"
        }

    @staticmethod
    def send_email_to_other_people(email_number: str, subject: str, text: str):
        """
        给别人发送邮件
        :param email_number: 收件人邮箱号
        :param subject: 主题
        :param text: 内容
        :return: 邮件是否成功发送的描述信息
        """
        try_num = settings['universal_set']['try_num']
        while True:
            try:
                msg = MIMEText(text, 'plain')
                msg['Subject'] = subject
                msg['From'] = SENDER
                msg['To'] = email_number

                server = smtplib.SMTP('smtp.163.com')
                server.login(SENDER, PASSWORD)
                server.send_message(msg)
                server.quit()
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    return {
                        "message": "发送邮件失败，原因未知！"
                    }
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue

        return {
            "message": "成功发送邮件！"
        }

    @staticmethod
    def add_new_user_email(email_number: str):
        """
        添加新的邮箱
        :param email_number: 邮箱号
        :return:
        """
        account_numbers['1'] = email_number
        utils.dump_to_json(account_numbers, root + '/conf/account_numbers.json')
        return {
            "message": "成功添加该用户的邮箱，可以给该用户发送邮件了！"
        }

    @staticmethod
    def change_user_email(email_number: str):
        """
        修改用户邮箱
        :param email_number: 邮箱号
        :return:
        """
        account_numbers['1'] = email_number
        utils.dump_to_json(account_numbers, root + '/conf/account_numbers.json')
        return {
            "message": "成功修改该用户的邮箱！"
        }


if __name__ == '__main__':
    print(SendEmail.send_email_to_user('工作汇报', '今日任务已全部完成...'))
