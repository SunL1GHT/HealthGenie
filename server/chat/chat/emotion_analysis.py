# coding=utf-8
import time

import threading

import queue

import re
from threading import Thread

import utils
from chat.emotion_enum import EmotionEnum
from chat.solve_problem import GptRobot
from loguru import logger

# 配置信息
settings = utils.load_json_from_file('../conf/settings.json')


class EmotionAnalysis:
    """
    情感分析模块
    """

    def __init__(self):
        self.robot_conventional_information = utils.load_json_from_file('../conf/robot_conventional_information.json')
        """
        机器人常规信息
        """
        self.affective_value = self.robot_conventional_information['Initial_affective_value']
        """
        情感值
        """
        self.text_emotion_dict = {}
        """
        文本与情绪值的对应字典
        """
        self.lock = threading.Lock()
        """
        用于保护共享资源的锁
        """

    def affect_affective_value_by_new_conversation(self, new_conversation: str):
        """
        根据新的对话影响情感值
        :param new_conversation:
        :return:
        """
        pass

    def add_text_emotion_dict(self, text: str):
        app_end_thread = Thread(target=self.add_text_emotion_dict_by_gpt, args=(text,))
        app_end_thread.start()
        logger.info(f'情感分析线程：{text}')

    def add_text_emotion_dict_by_gpt(self, text: str):
        """
        通过文本内容获得情感文本描述
        :param text:
        :return:
        """
        emotion = GptRobot.ask_a_question(
            f'情绪分类为（恐惧、愤怒、厌恶、喜好、悲伤、高兴、惊讶、无明显情绪），输出格式为[情感分类]，请分析下面括号中句子的情感分类并按照要求的格式输出（{text}），注意，你必须按照格式输出，且只能输出[情感分类]，其他的任何内容都不要输出，输出的全部内容只有[情感分类]')

        pattern = r'\[(.*?)\]'  # 正则表达式模式，匹配以 "[" 开始，以 "]" 结束的内容

        match = re.search(pattern, emotion)  # 在文本中搜索第一个匹配项

        if match and match.group(1) in ['恐惧', '愤怒', '厌恶', '喜好', '悲伤', '高兴', '惊讶']:
            emotion = match.group(1)
        else:
            emotion = EmotionEnum.SPEAK.value

        with self.lock:
            self.text_emotion_dict[text] = emotion

    def get_affective_str_by_text(self, text: str) -> str:
        """
        根据文本获取情感值
        :param text: 文本
        :return:
        """
        time_log = time.time()
        emotion = EmotionEnum.SPEAK.value
        while text not in self.text_emotion_dict:
            if time.time() - time_log > 1:
                break
        if text in self.text_emotion_dict:
            emotion = self.text_emotion_dict[text]
            logger.info(f'获取情感值（{text}：{emotion}）')
        return emotion
