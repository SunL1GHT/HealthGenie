# coding=utf-8
import time

import os
from threading import Thread

import requests
import utils
from chat.conversational_manager import ConversationalManager

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


class UnityAlive(Thread):
    """
    超时检测，如果超时则结束该进程
    """

    def __init__(self, conversational_manager: ConversationalManager):
        super().__init__()
        self.thread_working = True
        """
        本线程是否工作
        """
        self.frame = settings['universal_set']['life_frame']
        """
        生命周期帧率
        """
        self.previous_frame_end_time = time.time()
        """
        上一生命周期帧结束时间
        """
        self.fail_number = 0
        self.max_fail_number = 2
        self.unity_ip = settings["universal_set"]["unity_ip"]
        self.unity_send_message_url = self.unity_ip + '/alive'
        self.unity_proxies = {'http': self.unity_ip}

        self.conversational_manager = conversational_manager

    def run(self) -> None:
        self.previous_frame_end_time = time.time()
        while True:
            self.preprocessing()
            self.life_cycle()
            self.postprocessing()
            if not self.thread_working:
                break

    def life_cycle(self):
        """
        生命周期
        :return:
        """
        try:
            resp = requests.get(self.unity_send_message_url, proxies=self.unity_proxies, timeout=1.5)
            # 检查响应状态码
            if resp.text == "OK":
                self.fail_number = 0
                print("unity连接正常...")
            else:
                self.fail_number += 1
        except Exception as err:
            print(f'发送message至unity失败，发生如下错误：{err}')
            self.fail_number += 1
        if self.fail_number > self.max_fail_number:
            print('超出失败次数，关闭')
            self.fail_number = 0
            self.close()

    def preprocessing(self) -> None:
        """
        生命周期预处理
        """
        time.sleep(1 / self.frame * 1.5)

    def postprocessing(self) -> None:
        """
        生命周期后处理
        """
        self.previous_frame_end_time = time.time()

    def close(self):
        """
        是否存活
        :return:
        """
        print('开始结束程序...')

        self.conversational_manager.conversation_quick_end()

        # noinspection PyProtectedMember
        def delayed_function():
            os._exit(0)

        def invoke_function_with_delay(delay, function):
            time.sleep(delay)
            function()

        thread = Thread(target=invoke_function_with_delay, args=(0.5, delayed_function))
        thread.start()
