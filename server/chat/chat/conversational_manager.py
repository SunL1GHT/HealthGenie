# coding=utf-8
import time

from threading import Thread

import utils
from chat.emotion_enum import EmotionEnum
from chat.unity_controller import UnityController
from emotion_analysis import EmotionAnalysis
from loguru import logger
from memory_manager import MemoryManager
from question_packaging_and_answer import QuestionPackagingAndAnswer

# 配置信息
settings = utils.load_json_from_file('../conf/settings.json')


# 起话头 超额对话收集存储 用户说话过程中要不断重置时间 用户单次说话过长触发提醒事件
# 对话结束逻辑需要改进

class ConversationalManager(Thread):
    """
    对话管理线程（对话中的各种事件）
    """

    def __init__(self, question_object: QuestionPackagingAndAnswer, memory_manager: MemoryManager,
                 emotion_analysis: EmotionAnalysis, unity_controller: UnityController):
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
        self.question_object = question_object
        """
        问题对象
        """
        self.memory_manager = memory_manager
        """
        记忆管理器
        """
        self.previous_frame_unread_message = 0
        """
        上一帧未读消息数目
        """
        self.conversation_end_clock = settings['conversation']['conversation_end_clock_max']
        """
        对话结束倒计时
        """
        self.conversation_buffer_max_length = settings['conversation']['conversation_buffer_max_length']
        """
        对话缓冲区最大数量
        """
        self.emotion_object = emotion_analysis
        """
        情感模块对象
        """
        self.unity_controller = unity_controller
        """
        unity控制器
        """

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
        self.conversation_end_judge()
        self.conversation_buffer_judge_and_save()

    def preprocessing(self) -> None:
        """
        生命周期预处理
        """
        time.sleep(1 / self.frame)

    def postprocessing(self) -> None:
        """
        生命周期后处理
        """
        self.previous_frame_end_time = time.time()

    def conversation_end_judge(self):
        """
        对话结束判断
        :return:
        """

        if self.conversation_end_clock <= 0:
            """
            倒计时结束，进行对话结束处理
            """
            self.conversation_end()
        else:
            self.conversation_end_clock -= (time.time() - self.previous_frame_end_time)  # 倒计时自减

        if self.question_object.unread_message != self.previous_frame_unread_message:
            """
            如果未读消息数量发生变动，则说明对话仍在进行中，或者有新的对话开始，重置对话结束计时器
            """
            self.previous_frame_unread_message = self.question_object.unread_message
            self.conversation_end_clock = settings['conversation']['conversation_end_clock_max']
            logger.info('未读消息发生变动，对话继续，倒计时已重置...')

    def conversation_buffer_judge_and_save(self):
        """
        判断对话缓冲区是否达到阈值，如果达到阈值，则进行保存，并清空对话缓冲区
        :return:
        """
        if self.question_object.conversation_buffer_queue.qsize() >= self.conversation_buffer_max_length:
            self.conversation_buffer_save()

    def conversation_buffer_save(self):
        """
        保存并清空对话缓冲区
        :return:
        """
        conversation_text = ''
        for i in range(self.question_object.conversation_buffer_queue.qsize()):
            conversation_text += f"{self.question_object.conversation_buffer_queue.get()['content']} "
        affective_value = self.emotion_object.affective_value
        self.memory_manager.memory_and_knowledge_save(conversation_text, affective_value)

    def conversation_end(self):
        """
        对话结束
        :return:
        """
        if self.question_object.conversation_queue.qsize() > (self.conversation_buffer_max_length // 2):
            self.question_object.conversation_buffer_queue.put(self.question_object.conversation_queue.get())
        elif self.question_object.conversation_queue.qsize() != 0:
            for i in range(self.question_object.conversation_queue.qsize()):
                logger.info(f'结束对话{i}')
                self.question_object.conversation_buffer_queue.put(self.question_object.conversation_queue.get())
            self.memory_manager.clear_temporary_memory()
            self.conversation_buffer_save()
            logger.info('对话已结束...')
            self.unity_controller.send_any_message('', EmotionEnum.IDLE.value)

    def conversation_quick_end(self):
        """
        对话快速结束，用于在程序结束的时候快速保存记忆
        :return:
        """
        print("快速保存")
        if self.question_object.conversation_queue.qsize() != 0:
            for i in range(self.question_object.conversation_queue.qsize()):
                logger.info(f'结束对话{i}')
                self.question_object.conversation_buffer_queue.put(self.question_object.conversation_queue.get())
            self.memory_manager.clear_temporary_memory()
            self.conversation_buffer_save()
            logger.info('对话已结束...')
