# coding=utf-8
import os
import wave
from threading import Thread
import time

import pyaudio
from chat.unity_controller import UnityController
from loguru import logger
from voice_create import VoiceCreate

import utils

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


class VoiceOut(Thread):
    """
    语音输出模块
    """

    def __init__(self, voice_create: VoiceCreate, unity_controller: UnityController):
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
        self.voice_create = voice_create
        """
        音频生成器
        """
        self.is_speaking = False
        """
        是否正在说话
        """
        self.unity_controller = unity_controller

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
        if not self.is_speaking and not self.voice_create.voice_out_file_queue.empty():
            self.play_voice_and_delete_voice_file(self.voice_create.voice_out_file_queue.get())

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

    def wait(self):
        """
        等待语音输出结束
        :return:
        """
        while not self.voice_create.voice_out_file_queue.empty() or not self.voice_create.voice_out_queue.empty() or self.voice_create.voice_out_file_creating or self.is_speaking:
            time.sleep(2)

    def play_voice_and_delete_voice_file(self, voice_road):
        """
        播放音频后删除音频文件
        :param voice_road:音频
        :return:
        """
        self.unity_controller.send_message()
        self.is_speaking = True
        try_num = settings['universal_set']['try_num']
        while True:
            try:
                VoiceOut.playsound(voice_road)
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue
        os.remove(voice_road)
        self.is_speaking = False

    @staticmethod
    def playsound(file_road: str):
        """
        音频播放器
        :param file_road: 待播放音频路径
        :return:
        """
        chunk = 1024
        wave_file = wave.open(file_road, 'rb')
        p_audio = pyaudio.PyAudio()
        stream = p_audio.open(format=p_audio.get_format_from_width(wave_file.getsampwidth()),
                              channels=wave_file.getnchannels(),
                              rate=wave_file.getframerate(),
                              output=True)

        data = wave_file.readframes(chunk)

        while len(data) > 0:
            stream.write(data)
            data = wave_file.readframes(chunk)

        stream.stop_stream()
        stream.close()

        p_audio.terminate()
