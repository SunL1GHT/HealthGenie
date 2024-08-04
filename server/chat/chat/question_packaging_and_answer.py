# coding=utf-8
import os
import queue

import utils
# 这一行千万不能删掉，因为后面使用eval函数以字符串的形式调用了这个类
from applications import Applications
from emotion_analysis import EmotionAnalysis
from loguru import logger
from memory_manager import MemoryManager
from solve_problem import GptRobot
from tool import Tool

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


# 随机指导性话语，比如“回答这句话时开个玩笑”（待定）


class QuestionPackagingAndAnswer:
    """
    问题处理及回答模块
    """

    def __init__(self, memory_manager: MemoryManager, emotion_analysis: EmotionAnalysis,
                 voice_create=None) -> None:
        """
        生成问题对象（人格载入）
        """

        logger.info('人格载入中...')

        # 防止import优化导致Application类被删掉
        Applications.hello()

        self.unread_message = 0
        """
        未读消息数目
        """
        self.user_information = utils.load_json_from_file('../conf/user_information.json')
        """
        用户信息
        """
        self.robot_conventional_information = utils.load_json_from_file('../conf/robot_conventional_information.json')
        """
        机器人常规信息
        """
        self.conversation_queue = queue.Queue(self.robot_conventional_information['max_conversation_queue_length'])
        """
        对话队列
        """
        self.conversation_buffer_queue = queue.Queue()
        """
        对话缓冲区队列（大小在对话管理中决定）
        """
        self.memory_manager = memory_manager
        """
        记忆管理器
        """
        self.emotion_object = emotion_analysis
        """
        情感模块对象
        """
        self.voice_create = voice_create
        """
        声音生成线程
        """
        self.flask_queue = queue.Queue()
        """
        flask环境消息队列
        """

        logger.success('人格载入完毕...')

    def system_packaging(self, new_conversation: str) -> dict:
        """
        系统设定拼接
        :param new_conversation: 新的对话
        :return: 系统设定字典
        """
        memory_and_knowledge = self.get_memory_and_knowledge(new_conversation)
        self.influence_emotion(new_conversation)
        system = {
            "role": "system",
            "content": f"辅助我写一部完全由对话组成的小说，小说中当前时间为({Tool.get_data_and_time(1)})，你来扮演小说中名为{self.robot_conventional_information['name']}的角色，只需要输出{self.robot_conventional_information['name']}说的话即可，其他任何内容都不要输出，并且任何情况都不可以停止扮演{self.robot_conventional_information['name']}，{self.robot_conventional_information['name']}的人设如下({self.robot_conventional_information['character_setting']})，{self.robot_conventional_information['name']}知晓如下信息({memory_and_knowledge['knowledge']})，{self.robot_conventional_information['name']}的历史记忆如下({memory_and_knowledge['memory']})。注意你只能输出一句话，并且这句话的格式一定是({self.robot_conventional_information['name']}：{self.robot_conventional_information['name']}说的话)"
        }
        return system

    def influence_emotion(self, new_conversation: str):
        """
        获取情感值
        :param new_conversation: 新的对话
        :return: 情感文本描述
        """
        self.emotion_object.affect_affective_value_by_new_conversation(new_conversation)

    def get_memory_and_knowledge(self, new_conversation: str) -> dict:
        """
        获取记忆和知识
        :param new_conversation: 新的对话内容
        :return: 记忆和知识组成的字典
        """
        return self.memory_manager.memory_and_knowledge_loading_by_new_conversation(new_conversation)

    def packaging(self, new_conversation: str) -> list:
        """
        组装问题
        :param new_conversation: 当前问题
        :return: 完整问题
        """

        logger.info('问题正在组装...')

        user_conversation = {
            "role": "user",
            "content": f"{self.user_information['user_name']}：{new_conversation}"
        }

        self.add_conversation(user_conversation)

        conversation_list = Tool.queue_to_list(self.conversation_queue)
        conversation_list[len(conversation_list) - 1][
            'content'] = f"{settings['conversation']['every_sentence_prompts']} {conversation_list[len(conversation_list) - 1]['content']}"

        conversation = [self.system_packaging(new_conversation)] + conversation_list

        self.unread_message = 0

        logger.success('问题组装完毕，当前未读消息数为0...')

        return conversation

    def get_conversation_answer(self, new_conversation: str):
        """
        获取当前对话的回复
        :param new_conversation: 新的对话
        :return: 回复
        """
        try_num = settings['universal_set']['try_num']
        return_answer = ''
        question = self.packaging(new_conversation)
        while True:
            try:
                function_continue_flag = False
                answer = GptRobot.ask_continuous_questions(question, stream=True)
                answer_str = ''
                for i in answer:
                    if 'function_call' in i and type(i) != str:
                        logger.info(f'执行方法：{i["function_call"]["name"]}')
                        print(f'执行方法：{i["function_call"]["name"]}')
                        arguments = eval(i["function_call"]["arguments"])
                        self.add_conversation(i)
                        question.append(i)
                        function_conversation = {
                            "role": "function",
                            "name": i['function_call']['name'],
                            "content": str(eval('Applications.' + i['function_call']['name'] + f'(**{arguments})'))
                        }
                        self.add_conversation(function_conversation)
                        question.append(function_conversation)
                        function_continue_flag = True
                        break
                    if i == '[DONE]':
                        if not answer_str:
                            self.voice_create.voice_out_queue.put(answer_str)
                            self.emotion_object.add_text_emotion_dict(answer_str)
                        break
                    return_answer += i
                    answer_str += i
                    if answer_str == return_answer and i == '：':
                        answer_str = ''
                    if i == '：' and self.robot_conventional_information["name"] in answer_str.split('：')[0]:
                        answer_str = ''
                    for j in settings['universal_set']['voice_divide_symbol']:
                        if j in i:
                            self.voice_create.voice_out_queue.put(answer_str.split(j)[0] + j)
                            self.emotion_object.add_text_emotion_dict(answer_str.split(j)[0] + j)
                            if len(answer_str.split(j)) > 1:
                                answer_str = answer_str.split(j)[1]
                            else:
                                answer_str = ''
                            break
                if function_continue_flag:
                    continue
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue

        robot_conversation = {
            "role": "assistant",
            "content": return_answer
        }
        self.add_conversation(robot_conversation)
        return return_answer

    def add_conversation(self, context) -> None:
        """
        补充对话内容
        :param context: 待补充内容
        """

        logger.info('补充对话内容...')

        if self.conversation_queue.full():
            self.conversation_buffer_queue.put(self.conversation_queue.get())
        self.conversation_queue.put(context)
        self.unread_message += 1

        logger.success(f'对话内容补充完毕，当前未读消息数为{self.unread_message}...')
