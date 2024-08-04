# coding=utf-8

from loguru import logger
import sys

sys.path.insert(0, sys.path[0]+"/../")
from applications_realize.send_email.send_email import SendEmail


class Applications:
    """
    应用层应用方法合集
    """

    @staticmethod
    def hello():
        logger.info('这个方法不要删掉，应为问题打包脚本调用这个类的时候是通过eval函数以字符串的形式调用的，因此我通过这个函数防止import被优化掉')

    @staticmethod
    def send_email_to_user(subject: str, text: str):
        """
        发送邮件
        :param subject: 主题
        :param text: 内容
        :return: 邮件是否成功发送的描述信息
        """
        return SendEmail.send_email_to_user(subject, text)

    @staticmethod
    def send_email_to_other_people(email_number: str, subject: str, text: str):
        """
        给别人发送邮件
        :param email_number: 收件人邮箱号
        :param subject: 主题
        :param text: 内容
        :return: 邮件是否成功发送的描述信息
        :return:
        """
        return SendEmail.send_email_to_other_people(email_number, subject, text)

    @staticmethod
    def add_new_user_email(email_number: str):
        """
        添加新的邮箱
        :param email_number: 邮箱号
        :return:
        """
        return SendEmail.add_new_user_email(email_number)

    @staticmethod
    def change_user_email(email_number: str):
        """
        修改用户邮箱
        :param email_number: 邮箱号
        :return:
        """
        return SendEmail.change_user_email(email_number)
    
    """
    查询当前时间的工具。返回结果示例：“当前时间：2024-04-15 17:15:18。”
    """
    @staticmethod
    def get_current_time():
        from datetime import datetime
        # 获取当前日期和时间
        current_datetime = datetime.now()
        # 格式化当前日期和时间
        formatted_time = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # 返回格式化后的当前时间
        return f"当前时间：{formatted_time}。"
