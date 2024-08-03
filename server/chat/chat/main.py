# coding=utf-8

"""
主模块
"""
import time

import os
from enum import Enum

import openai
import requests
import utils
from chat.emotion_enum import EmotionEnum
from chat.unity_controller import UnityController
from conversational_manager import ConversationalManager
from emotion_analysis import EmotionAnalysis
from loguru import logger
from memory_manager import MemoryManager
from question_packaging_and_answer import QuestionPackagingAndAnswer
from unity_flask_run import UnityFlaskRun
from vector_database import VectorDatabase
from voice_create import VoiceCreate
from voice_in import VoiceIn
from voice_out import VoiceOut
from unity_alive import UnityAlive

# 项目根目录
project_path = os.path.dirname(os.path.dirname(__file__))

# 配置信息
settings_path = os.path.join(project_path, 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

# 日志路径
log_path = os.path.join(project_path, 'logs')

class LogMode(Enum):
    """
    存储模式
    """
    FILE = 0
    """
    文件
    """
    CONSOLE = 1
    """
    控制台
    """


def log_mode(mode: LogMode):
    if mode == LogMode.CONSOLE:
        return
    elif mode == LogMode.FILE:
        logger.remove(0)
        logger.add(log_path + 'runtime_{time}.log', rotation="50 MB", retention='10 days')


def vits_alive():
    """
    检查vits是否在线
    :return:
    """
    api_ip = settings["universal_set"]["vits_simple_api_ip"]
    url = api_ip + '/alive'
    proxies = {'http': api_ip}
    print('正在连接vits端...')
    while True:
        time.sleep(2)
        try:
            response = requests.get(url, proxies=proxies)
            print(response)
            if response.text == "OK":
                print('连接成功...')
                return
        except Exception as err:
            logger.error(err)
            continue


# 好感度也应该加入到问题打包模块内，应当在人际关系那里描述上关系的好感度
# 情绪识别
# 声纹识别
# 印象计算

if __name__ == '__main__':

    # if settings['universal_set']['openai_api_proxy']:
    #     os.environ["OPENAI_API_BASE"] = settings['universal_set']['openai_api_proxy_url']
    #     openai.api_base = settings['universal_set']['openai_api_proxy_url']
    # elif settings['universal_set']['proxy_port'] != '':
    #     os.environ["http_proxy"] = f"http://127.0.0.1:{settings['universal_set']['proxy_port']}"
    #     os.environ["https_proxy"] = f"http://127.0.0.1:{settings['universal_set']['proxy_port']}"

    log_mode(LogMode.FILE)

    vits_alive()

    VectorDatabase.self_inspection()

    memory_manager = MemoryManager()
    memory_manager.start()

    emotion_analysis = EmotionAnalysis()

    unity_controller = UnityController(emotion_analysis)

    voice_create = VoiceCreate(unity_controller)
    voice_create.start()

    question_answer = QuestionPackagingAndAnswer(memory_manager, emotion_analysis, voice_create)
    conversational_manager = ConversationalManager(question_answer, memory_manager, emotion_analysis, unity_controller)
    conversational_manager.start()

    voice_in = VoiceIn(unity_controller)
    voice_in.record_control()

    voice_out = VoiceOut(voice_create, unity_controller)
    voice_out.start()

    unity_alive = UnityAlive(conversational_manager)
    unity_alive.start()

    unity_flask = UnityFlaskRun(conversational_manager, unity_alive)
    unity_flask.start()

    while True:
        user_input = voice_in.input()
        memory_manager.is_speaking = True
        answer = question_answer.get_conversation_answer(user_input)
        voice_out.wait()
        unity_controller.send_any_message('', EmotionEnum.IDLE.value)
        memory_manager.is_speaking = False
