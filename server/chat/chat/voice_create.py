# coding=utf-8
import queue
import time
from threading import Thread

import requests
from bio_robot.unity_controller import UnityController
from loguru import logger

import utils

# 配置信息
settings = utils.load_json_from_file('../conf/settings.json')

voice_url = f'{settings["universal_set"]["vits_simple_api_ip"]}/voice/vits'
proxies = {'http': settings["universal_set"]["vits_simple_api_ip"]}


class VoiceCreate(Thread):
    """
    语音文件生成模块
    """

    def __init__(self, unity_controller: UnityController):
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
        self.voice_out_queue = queue.Queue()
        """
        语音输出文本队列
        """
        self.voice_out_id = utils.load_json_from_file('../conf/robot_conventional_information.json')['voice_out_id']
        """
        语音输出的角色id
        """
        self.voice_out_file_queue = queue.Queue()
        """
        语音输出文件队列
        """
        self.unity_controller = unity_controller
        """
        unity控制器
        """
        self.voice_out_file_creating = False

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
        text = self.get_speaking_text()
        if text:
            self.voice_out_file_creating = True
            self.start_speak(text)
            self.voice_out_file_creating = False

    def preprocessing(self) -> None:
        """
        生命周期预处理
        """
        time.sleep(1 / self.frame / 10)

    def postprocessing(self) -> None:
        """
        生命周期后处理
        """
        self.previous_frame_end_time = time.time()

    def get_speaking_text(self) -> str:
        """
        获取需要说的话的文本
        :return:
        """
        if not self.voice_out_queue.empty():
            return self.voice_out_queue.get()
        return ''

    def get_voice_by_text(self, text: str):
        """
        文本转语音
        :param text: 文本内容
        :return:
        """
        params = {
            "text": text,
            "id": self.voice_out_id,
            "format": 'wav',
            "lang": "zh"
        }

        try_num = settings['universal_set']['try_num']
        while True:
            try:
                response = requests.get(url=voice_url, params=params, proxies=proxies)
                # 检查响应状态码
                if response.status_code == 200:
                    filename = f"../files/out{int(time.time() * 100)}.wav"
                    # 保存音频文件
                    with open(filename, "wb") as file:
                        file.write(response.content)
                    logger.info("音频文件已下载:", filename)
                    return filename

                logger.info("下载失败. 状态码:", response.status_code)
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                try_num -= 1
                continue
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue
        return None

    def start_speak(self, text: str):
        """
        开始说话
        :param text: 内容
        :return:
        """
        print(text)
        voice = self.get_voice_by_text(text)
        if voice:
            self.unity_controller.add_message(text)
            self.voice_out_file_queue.put(voice)
