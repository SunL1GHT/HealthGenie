# coding=utf-8
import queue
import os

import requests
import utils
from chat.emotion_analysis import EmotionAnalysis
from chat.emotion_enum import EmotionEnum

from loguru import logger

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


class UnityController:
    """
    语音输入模块
    """

    def __init__(self, emotion_analysis: EmotionAnalysis):
        self.unity_message_queue = queue.Queue()
        """
        unity消息队列
        """
        self.emotion_analysis = emotion_analysis
        """
        情绪识别
        """

        self.unity_ip = settings["universal_set"]["unity_ip"]
        self.unity_send_message_url = self.unity_ip + '/message'
        self.unity_proxies = {'http': self.unity_ip}

    def add_message(self, text: str):
        message = {
            'text': text,
            'emotion': EmotionEnum.SPEAK
        }
        self.unity_message_queue.put(message)

    def send_message(self):
        try:
            logger.info(self.unity_send_message_url)
            json = self.unity_message_queue.get()
            # 这里判断一下，如果情感分析那里有东西，就使用，没东西就等待最多1秒
            json['emotion'] = self.emotion_analysis.get_affective_str_by_text(json['text'])
            logger.info(json)
            resp = requests.post(self.unity_send_message_url, json=json, proxies=self.unity_proxies)
            # 检查响应状态码
            if resp.status_code == 200:
                logger.success("成功将message发送至unity...")
            else:
                logger.error("发送message至unity失败. 状态码:", resp.status_code)
        except Exception as err:
            logger.error(f'发送message至unity失败，发生如下错误：{err}')

    def send_any_message(self, message: str, emotion: str):
        try:
            logger.info(self.unity_send_message_url)
            json = {
                'text': message,
                'emotion': emotion
            }
            logger.info(json)
            resp = requests.post(self.unity_send_message_url, json=json, proxies=self.unity_proxies)
            # 检查响应状态码
            if resp.status_code == 200:
                logger.success("成功将message发送至unity...")
            else:
                logger.error("发送message至unity失败. 状态码:", resp.status_code)
        except Exception as err:
            logger.error(f'发送message至unity失败，发生如下错误：{err}')
