# coding=utf-8
import os
import time

import wave
from threading import Thread

import keyboard
import openai
import pyaudio
import utils
from api_key_hand_out import ApiKeyHandOut
from emotion_enum import EmotionEnum
from unity_controller import UnityController
from loguru import logger

# 项目根目录
project_path = os.path.dirname(os.path.dirname(__file__))

# 配置信息
settings_path = os.path.join(project_path, 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


class VoiceIn:
    """
    语音输入模块
    """

    def __init__(self, unity_controller: UnityController):
        self.is_key_down = False
        """
        按键是否按下
        """
        self.can_record = False
        """
        可否录音
        """
        self.rec = Recorder()
        """
        录音机
        """
        self.text = ''
        """
        语音转换的文本内容
        """
        self.key_dict = {}
        """
        快捷键字典，所有键都是true才能激活
        """
        for i in settings['universal_set']['recorder_key'].split('+'):
            self.key_dict[i] = False
        self.rec.start()

        self.unity_controller = unity_controller

    def record_start_and_end(self, key):
        """
        开始录音和结束录音控制（由按键按下和抬起控制）
        :param key: 按键
        :return:
        """
        if key.name not in self.key_dict.keys():
            return
        if not self.can_record:
            return
        all_key_down = False
        if key.event_type == 'up':
            self.key_dict[key.name] = False
        if key.event_type == 'down':
            for i in self.key_dict.keys():
                if self.key_dict[i]:
                    continue
                elif i != key.name:
                    break
                else:
                    self.key_dict[i] = True
            else:
                all_key_down = True
        if not self.is_key_down and all_key_down:
            self.is_key_down = True
            print(f"你按下了{self.key_dict.keys()}键，开始录音")
            self.unity_controller.send_any_message('聆听ing...', EmotionEnum.IDLE.value)
            self.rec.play()
        if self.is_key_down and not all_key_down:
            self.is_key_down = False
            print(f"你松开了{self.key_dict.keys()}键，结束录音")
            self.unity_controller.send_any_message('思考ing...', EmotionEnum.THINK.value)
            self.can_record = False
            self.rec.stop()
            input_path = os.path.join(project_path, f"files/input.wav")
            self.rec.save(input_path)
            audio_file = open(input_path, "rb")

            try_num = settings['universal_set']['try_num']
            while True:
                try:
                    client = openai.Client(api_key=ApiKeyHandOut.get_api_key(), 
                                           base_url = settings['whisper_set']['whisper_api_ip'])
                    transcript = client.audio.transcriptions.create(model=settings['whisper_set']['model_engine'],
                                                                    file=audio_file)
                    self.text = transcript.text
                    print(self.text)
                    break
                except Exception as err:
                    if try_num <= 0:
                        logger.error('错误次数过多，请联系开发者...')
                        break
                    logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                    try_num -= 1
                    continue

    def record_control(self):
        """
        录音控制
        :return:
        """
        keyboard.hook(self.record_start_and_end)

    def input(self):
        """
        语音输入
        :return: 输入的语音所转换成的文本内容
        """
        self.can_record = True
        print(f'按{settings["universal_set"]["recorder_key"]}开始语音输入...')
        while self.text == '':
            time.sleep(0.01)
        resp = self.text
        self.text = ''
        self.can_record = False
        return resp


class Recorder(Thread):
    """
    录音
    """

    def __init__(self, chunk=1024, channels=1, rate=64000):
        super().__init__()
        self.chunk = chunk
        self.format = pyaudio.paInt16
        self.channels = channels
        self.rate = rate
        self._running = False
        self._frames = []

    def run(self) -> None:
        while True:
            time.sleep(0.01)
            if self._running:
                self.__recording()

    def __recording(self):
        self._frames = []
        p_audio = pyaudio.PyAudio()
        stream = p_audio.open(format=self.format,
                              channels=self.channels,
                              rate=self.rate,
                              input=True,
                              frames_per_buffer=self.chunk)
        while self._running:
            data = stream.read(self.chunk)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p_audio.terminate()

    def play(self):
        """
        开始录音
        :return:
        """
        self._running = True

    def stop(self):
        """
        结束录音
        :return:
        """
        self._running = False

    def save(self, filename):
        """
        保存录音到本地
        :param filename:
        :return:
        """
        p_audio = pyaudio.PyAudio()
        if not filename.endswith(".wav"):
            filename = filename + ".wav"
        wav_file = wave.open(filename, 'wb')
        wav_file.setnchannels(self.channels)
        wav_file.setsampwidth(p_audio.get_sample_size(self.format))
        wav_file.setframerate(self.rate)
        wav_file.writeframes(b''.join(self._frames))
        wav_file.close()
        print("Saved")


if __name__ == '__main__':
    v = VoiceIn()
    print(12312)
    v.record_control()
    while True:
        pass
