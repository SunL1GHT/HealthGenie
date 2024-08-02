# coding=utf-8
import os
import copy
import queue
import time

from loguru import logger

import utils
from solve_problem import GptRobot

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


class Tool:
    """
    工具类
    """

    @staticmethod
    def condensed_text(text: str, length_limit: int) -> str:
        """
        精简文本内容
        :param text: 文本内容
        :param length_limit: 长度限制
        :return: 精简后的文本
        """
        resp = GptRobot.ask_a_question(
            f'将下列文章精简到{length_limit}字以内，注意所有细节千万都不要丢失，尤其是时间，地点，人物等的所有信息一定要全面，任何细节都不要丢失：{text}')
        return resp

    @staticmethod
    def timestamp_to_date(timestamp: float) -> str:
        """
        时间戳转换为日期
        :param timestamp: 时间戳
        :return: 日期
        """
        time_local = time.localtime(timestamp)
        return time.strftime("%Y年%m月%d日 %H时%M分", time_local)

    @staticmethod
    def list_de_weight(lst: list) -> list:
        """
        列表去重
        :param lst: 列表
        :return: 去重后的列表
        """
        return list(dict.fromkeys(lst))

    @staticmethod
    def queue_to_list(que: queue.Queue) -> list:
        """
        队列转换为列表
        :param que: 队列
        :return: 列表
        """
        lst = []
        for i in range(que.qsize()):
            logger.info(f'队列中的第{i}个元素添加进列表...')
            text = que.get()
            lst.append(text)
            que.put(text)
        logger.info(f'队列转列表：{lst}')
        return copy.deepcopy(lst)

    @staticmethod
    def voluntarily_get_and_put_in_queue(que: queue.Queue, ele):
        """
        队满自动出队的队列添加元素
        :param que: 队列
        :param ele: 要添加的元素
        :return:
        """
        if que.full():
            que.get()
        que.put(ele)

    @staticmethod
    def clear_queue(que: queue.Queue):
        """
        清空队列
        :param que:队列
        :return:
        """
        while True:
            if que.empty():
                return
            que.get()

    @staticmethod
    def get_data_and_time(accuracy: int) -> str:
        """
        获取不同精度日期的中文表示
        :param accuracy: 精度  0:秒  1:分  2:时  3:日  4:月  5:年
        :return:对应精度日期的中文表示
        """
        data_and_time = ''
        if accuracy == 0:
            data_and_time = time.strftime('%Y年%m月%d日 %H时%M分%S秒')
        elif accuracy == 1:
            data_and_time = time.strftime('%Y年%m月%d日 %H时%M分')
        elif accuracy == 2:
            data_and_time = time.strftime('%Y年%m月%d日 %H时')
        elif accuracy == 3:
            data_and_time = time.strftime('%Y年%m月%d日')
        elif accuracy == 4:
            data_and_time = time.strftime('%Y年%m月')
        elif accuracy == 5:
            data_and_time = time.strftime('%Y年')
        return data_and_time


if __name__ == '__main__':
    print(Tool.get_data_and_time(3))
    print(Tool.timestamp_to_date(1684073542.8331506))
