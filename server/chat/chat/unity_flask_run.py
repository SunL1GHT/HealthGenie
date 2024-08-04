# coding=utf-8
import os
import time

import threading
from threading import Thread

import utils
from conversational_manager import ConversationalManager
from unity_alive import UnityAlive
from flask import Flask
from loguru import logger

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

app = Flask(__name__)

shutdown_flag = threading.Event()


def app_thread(conversational_manager: ConversationalManager, unity_alive: UnityAlive):
    """
    flask监控线程，当检测到close被请求，则执行记忆存储以及进程结束程序
    :param unity_alive:
    :param conversational_manager: 对话管理器
    :return:
    """
    while not shutdown_flag.is_set():
        time.sleep(0.5)

    unity_alive.max_fail_number = 20
    time.sleep(0.5)
    print('flask端结束了...')
    conversational_manager.conversation_quick_end()
    logger.info('保存完了...')

    # noinspection PyProtectedMember
    def delayed_function():
        os._exit(0)

    def invoke_function_with_delay(delay, function):
        time.sleep(delay)
        function()

    thread = Thread(target=invoke_function_with_delay, args=(1, delayed_function))
    thread.start()


class UnityFlaskRun(Thread):
    """
    接收Unity发来的消息
    """

    def __init__(self, conversational_manager: ConversationalManager, unity_alive: UnityAlive):
        super().__init__()
        self.conversational_manager = conversational_manager
        self.unity_alive = unity_alive

    def run(self) -> None:
        manager = self.conversational_manager
        app_end_thread = Thread(target=app_thread, args=(manager, self.unity_alive))
        app_end_thread.start()
        app.run("127.0.0.1", 14362)

    @staticmethod
    @app.route('/alive', methods=["GET"])
    def alive():
        """
        是否存活
        :return:
        """
        return "OK"

    @staticmethod
    @app.route('/close', methods=["GET"])
    def close():
        """
        关闭进程
        :return:
        """
        shutdown_flag.set()
        return "OK"
