# coding=utf-8

import time

import queue
from threading import Thread
import os

import utils
from loguru import logger
from solve_problem import GptRobot
from tool import Tool
from vector_database import VectorDatabase

# 项目根目录
project_path = os.path.dirname(os.path.dirname(__file__))

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)


# 待施工：生成印象值的方法需要实现，根据语义中的时间相关表述查找记忆（待定，暂时无需实现）,或许要加一个最大印象值和最小印象值防止出现印象值过大或过小的问题

class MemoryManager(Thread):
    """
    记忆及遗忘处理线程
    """

    def __init__(self):
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
        self.robot_memory_information = utils.load_json_from_file(project_path + 'conf/robot_memory_information.json')
        """
        机器人记忆信息
        """
        self.processing_time_interval = settings['memory']['processing_time_interval']
        """
        记忆处理时间间隔
        """
        self.memory_vector_database = VectorDatabase(project_path + 'vector_database/memory', 'memory')
        """
        向量数据库记忆库
        """
        self.knowledge_vector_database = VectorDatabase(project_path + 'vector_database/knowledge', 'knowledge')
        """
        向量数据库知识库
        """
        self.base_memory_loading_number = settings['memory']['base_memory_loading_number']
        """
        基础记忆加载数量
        """
        self.relevancy_memory_queue = queue.Queue(settings['memory']['relevancy_memory_queue_length'])
        """
        相关记忆队列
        """
        self.time_memory_queue = queue.Queue(settings['memory']['time_memory_queue_length'])
        """
        时间顺序记忆队列
        """
        self.impression_memory_queue = queue.Queue(settings['memory']['impression_memory_queue_length'])
        """
        印象顺序记忆队列
        """
        self.associative_memory_queue = queue.Queue(settings['memory']['associative_memory_queue_length'])
        """
        记忆网络联想队列
        """
        self.conversation_summary_prompts = settings['memory']['conversation_summary_prompts']
        """
        对话总结提示词
        """
        self.knowledge_extraction_prompts = settings['memory']['knowledge_extraction_prompts']
        """
        知识提取提示词
        """
        self.depth_of_thinking = settings['memory']['initial_depth_of_thinking']
        """
        思考深度
        """
        self.max_depth_of_thinking = settings['memory']['max_depth_of_thinking']
        """
        最大思考深度
        """
        self.min_depth_of_thinking = settings['memory']['min_depth_of_thinking']
        """
        最小思考深度
        """
        self.max_memory_length = settings['memory']['max_memory_length']
        """
        最大记忆字数长度
        """
        self.max_knowledge_length = settings['memory']['max_knowledge_length']
        """
        最大知识字数长度
        """
        self.is_speaking = False
        """
        是否正在说话
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
        self.memory_cycle()

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

    def clear_temporary_memory(self):
        """
        清空临时记忆区
        :return:
        """
        Tool.clear_queue(self.time_memory_queue)
        Tool.clear_queue(self.impression_memory_queue)
        Tool.clear_queue(self.relevancy_memory_queue)
        Tool.clear_queue(self.associative_memory_queue)
        self.depth_of_thinking = settings['memory']['initial_depth_of_thinking']

    def add_depth_of_thinking(self, value: float):
        """
        增加思考深度
        :param value: 增加值
        :return:
        """
        self.depth_of_thinking += value
        if self.depth_of_thinking > self.max_depth_of_thinking:
            self.depth_of_thinking = self.max_depth_of_thinking

    def reduce_depth_of_thinking(self, value: float):
        """
        减小思考深度
        :param value: 减小值
        :return:
        """
        self.depth_of_thinking -= value
        if self.depth_of_thinking < self.min_depth_of_thinking:
            self.depth_of_thinking = self.min_depth_of_thinking

    # noinspection PyMethodMayBeStatic
    def initial_impression_generation(self, affective_value: int) -> float:
        """
        生成初始印象值（只要对生成印象的方案有新的改进，都可以封装成方法，然后放在本方法中）
        :param affective_value: 情感值
        :return: 初始印象值
        """
        initial_impression = settings['memory']['initial_impression_base'] + settings['memory'][
            'initial_impression_base'] * abs(affective_value)

        return initial_impression

    def memory_and_knowledge_loading_by_new_conversation(self, new_conversation: str) -> dict:
        """
        通过新的对话加载记忆和知识
        :param new_conversation: 新的对话
        :return: 记忆和知识的字典，结构为 { 'memory' : memory , 'knowledge' : knowledge }
        """
        logger.info('正在通过新的对话加载记忆和知识...')
        memory = self.memory_loading_by_new_conversation(new_conversation)
        knowledge = self.knowledge_loading_by_loaded_memory(memory)
        memory_and_knowledge = {
            'memory': memory,
            'knowledge': knowledge
        }
        self.memory_and_knowledge_length_limit(memory_and_knowledge)
        logger.success('记忆和知识加载成功...')
        return memory_and_knowledge

    def memory_and_knowledge_length_limit(self, memory_and_knowledge: dict):
        """
        记忆和知识长度限制
        :param memory_and_knowledge: 记忆和知识字典
        :return:
        """
        if len(memory_and_knowledge['memory']) > self.max_memory_length:
            memory_and_knowledge['memory'] = Tool.condensed_text(memory_and_knowledge['memory'], self.max_memory_length)
        if len(memory_and_knowledge['knowledge']) > self.max_knowledge_length:
            memory_and_knowledge['knowledge'] = Tool.condensed_text(memory_and_knowledge['knowledge'],
                                                                    self.max_knowledge_length)

    def knowledge_loading_by_loaded_memory(self, memory_content: str) -> str:
        """
        根据加载好的记忆加载与这些记忆相关的知识（一定要先执行加载记忆的方法再执行这个方法）
        :param memory_content: 记忆内容
        :return: 知识
        """
        id_lst = self.memory_queue_combine()
        knowledge_list = []
        for i in id_lst:
            knowledge_list += self.robot_memory_information['historical_memory'][i]['knowledge_list']
        if len(knowledge_list) < 20:
            knowledge_list_in_database = self.knowledge_vector_database.search(memory_content,
                                                                               self.base_memory_loading_number // 2)
            for i in knowledge_list_in_database:
                knowledge_list.append(i[0].page_content)
        Tool.list_de_weight(knowledge_list)
        return ','.join(knowledge_list)

    def memory_loading_by_new_conversation(self, new_conversation: str) -> str:
        """
        通过新的对话加载记忆
        :param new_conversation: 新对话
        :return: 记忆内容
        """
        document_list = self.memory_vector_database.search(new_conversation, self.base_memory_loading_number)
        return self.memory_loading_processing_by_depth_of_thinking(document_list)

    def memory_loading_processing_by_depth_of_thinking(self, document_list: list) -> str:
        """
        根据记忆深度处理加载出来的记忆
        :param document_list: 记忆列表
        :return: 记忆内容
        """
        logger.info('开始加载记忆...')
        self.strengthen_the_impression(document_list)
        loading_num = self.calculate_the_loading_num_by_depth_of_thinking()
        self.time_memory_loading(document_list, loading_num)
        self.relevancy_memory_loading(document_list, loading_num)
        self.impression_memory_loading(document_list, loading_num)
        self.associative_memory_loading(document_list, loading_num)
        logger.success('记忆加载成功...')
        id_lst = self.memory_queue_combine()
        return self.memory_generation(id_lst)

    def memory_generation(self, id_lst: list[str]) -> str:
        """
        生成记忆体
        :param id_lst: 记忆id列表
        :return: 记忆内容
        """
        memory = ''
        for i in id_lst:
            memory += f"[{Tool.timestamp_to_date(self.robot_memory_information['historical_memory'][i]['log_time'])}]{self.robot_memory_information['historical_memory'][i]['text']}; "
        return memory

    def memory_queue_combine(self) -> list[str]:
        """
        合并所有记忆队列为列表并去重
        :return: 记忆id列表
        """
        lst = []
        lst += Tool.queue_to_list(self.time_memory_queue)
        lst += Tool.queue_to_list(self.relevancy_memory_queue)
        lst += Tool.queue_to_list(self.impression_memory_queue)
        lst += Tool.queue_to_list(self.associative_memory_queue)
        return Tool.list_de_weight(lst)

    def calculate_the_loading_num_by_depth_of_thinking(self) -> int:
        """
        根据记忆深度计算需要载入的每一种记忆的条数
        :return: 载入数量
        """
        if self.depth_of_thinking < self.min_depth_of_thinking + (
                self.max_depth_of_thinking - self.min_depth_of_thinking) * 0.5:
            loading_num = 1
        elif self.min_depth_of_thinking + (
                self.max_depth_of_thinking - self.min_depth_of_thinking) * 0.5 <= self.depth_of_thinking < self.min_depth_of_thinking + (
                self.max_depth_of_thinking - self.min_depth_of_thinking) * 0.8:
            loading_num = 2
        elif self.min_depth_of_thinking + (
                self.max_depth_of_thinking - self.min_depth_of_thinking) * 0.8 <= self.depth_of_thinking:
            loading_num = 3
        else:
            loading_num = 1
        return loading_num

    def strengthen_the_impression(self, document_list: list):
        """
        根据回忆起来的记忆加深印象
        :param document_list: 记忆列表
        :return:
        """
        logger.info('根据回忆加深印象...')

        for i in document_list:
            # 先判断有没有这个记忆节点，万一节点丢失，需要先修复
            if self.robot_memory_information['historical_memory'].get(i[0].metadata['id_str']) is None:
                initial_impression = 1 / self.max_depth_of_thinking
                memory_id = i[0].metadata['id_str']
                knowledge_list = []
                self.robot_memory_information['historical_memory'][memory_id] = {
                    "log_time": time.time(),
                    "initial_impression": initial_impression,
                    "current_impression": initial_impression,
                    "number_of_repetitions": 1,
                    "text": i[0].page_content,
                    "knowledge_list": knowledge_list,
                    "associated_nodes_and_distance_between_nodes": {}
                }
                utils.dump_to_json(self.robot_memory_information,
                                   '../conf/robot_memory_information.json')  # 记忆相关数据存入json
            if i[1] == 0:
                self.robot_memory_information['historical_memory'][i[0].metadata['id_str']]['initial_impression'] += (
                        1 / self.min_depth_of_thinking)
                continue
            self.robot_memory_information['historical_memory'][i[0].metadata['id_str']]['initial_impression'] += (
                    1 / i[1])
            self.robot_memory_information['historical_memory'][i[0].metadata['id_str']]['current_impression'] += (
                    1 / i[1])
        utils.dump_to_json(self.robot_memory_information, project_path + 'conf/robot_memory_information.json')

    def associative_memory_loading(self, document_list: list, loading_num: int):
        """
        根据记忆网络联想链式加载记忆
        :param document_list: 记忆列表
        :param loading_num: 载入数量
        :return:
        """
        logger.info('通过记忆网络联想记忆...')
        pass_list = []
        ids = []
        for i in document_list:
            pass_list += self.search_memory_network_by_length_limit(i[0].metadata['id_str'], 0)
        for i in range(loading_num):
            min_distance = 10000000
            this_id = ''
            for j in pass_list:
                if j[0] in ids:
                    continue
                if j[1] < min_distance:
                    this_id = j[0]
                    min_distance = j[1]
            if this_id:
                ids.append(this_id)
        for i in ids:
            Tool.voluntarily_get_and_put_in_queue(self.associative_memory_queue, i)

    def search_memory_network_by_length_limit(self, node_id: str, cumulative_distance: float) -> list[(str, float)]:
        """
        根据距离限制在记忆网络中递归查找相关节点（深度优先搜索）
        :param node_id: 节点id
        :param cumulative_distance: 累计距离
        :return:
        """
        pass_list = []
        for i in self.robot_memory_information['historical_memory'][node_id]['associated_nodes_and_distance_between_nodes']:
            if cumulative_distance + \
                    self.robot_memory_information['historical_memory'][node_id][
                        'associated_nodes_and_distance_between_nodes'][
                        i] > self.depth_of_thinking:
                continue
            pass_list.append((i, cumulative_distance + self.robot_memory_information['historical_memory'][node_id][
                'associated_nodes_and_distance_between_nodes'][i]))
            pass_list += self.search_memory_network_by_length_limit(i, cumulative_distance +
                                                                    self.robot_memory_information['historical_memory'][
                                                                        node_id][
                                                                        'associated_nodes_and_distance_between_nodes'][
                                                                        i])
        return pass_list

    def time_memory_loading(self, document_list: list, loading_num: int):
        """
        根据时间顺序加载记忆
        :param document_list: 记忆列表
        :param loading_num: 载入数量
        :return:
        """
        logger.info('通过时间顺序加载记忆...')
        ids = []
        for i in range(loading_num):
            max_time = 0
            this_id = ''
            for j in document_list:
                if j[0].metadata['id_str'] in ids:
                    continue
                if self.robot_memory_information['historical_memory'][j[0].metadata['id_str']]['log_time'] > max_time:
                    this_id = j[0].metadata['id_str']
                    max_time = self.robot_memory_information['historical_memory'][j[0].metadata['id_str']]['log_time']
            if this_id:
                ids.append(this_id)
        for i in ids:
            Tool.voluntarily_get_and_put_in_queue(self.time_memory_queue, i)

    def impression_memory_loading(self, document_list: list, loading_num: int):
        """
        根据印象顺序加载记忆
        :param document_list: 记忆列表
        :param loading_num: 载入数量
        :return:
        """
        logger.info('通过印象顺序加载记忆...')
        ids = []
        for i in range(loading_num):
            max_impression = 0
            this_id = ''
            for j in document_list:
                if j[0].metadata['id_str'] in ids:
                    continue
                if self.robot_memory_information['historical_memory'][j[0].metadata['id_str']]['current_impression'] > max_impression:
                    this_id = j[0].metadata['id_str']
                    max_impression = self.robot_memory_information['historical_memory'][j[0].metadata['id_str']][
                        'current_impression']
            if this_id:
                ids.append(this_id)
        for i in ids:
            Tool.voluntarily_get_and_put_in_queue(self.impression_memory_queue, i)

    def relevancy_memory_loading(self, document_list: list, loading_num: int):
        """
        根据相关度顺序加载记忆
        :param document_list: 记忆列表
        :param loading_num: 载入数量
        :return:
        """
        logger.info('通过相关度加载记忆...')
        for i in range(loading_num):
            Tool.voluntarily_get_and_put_in_queue(self.relevancy_memory_queue, document_list[i][0].metadata['id_str'])

    def memory_and_knowledge_save(self, conversation_context: str, affective_value: int):
        """
        记忆和知识存储
        :param conversation_context: 交谈内容
        :param affective_value: 情感值
        :return:
        """
        logger.info('本次记忆正在存储...')
        try_num = settings['universal_set']['try_num']
        while True:
            try:
                if not conversation_context:
                    logger.error('对话内容为空，记忆无法存储...')
                    break
                self.memory_save_include_knowledge_save(conversation_context, affective_value)
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue

    def memory_save_include_knowledge_save(self, conversation_context: str, affective_value: int):
        """
        记忆存储（包含了知识存储）
        :param conversation_context: 交谈内容
        :param affective_value: 情感值
        :return:
        """
        short_memory = GptRobot.ask_a_question(
            f'{self.conversation_summary_prompts}{conversation_context}')
        short_memory = short_memory.replace('\n', '')
        logger.info(f'总结信息如下：{short_memory}')
        initial_impression = self.initial_impression_generation(affective_value)
        memory_id = str(len(self.robot_memory_information['historical_memory']))
        knowledge_list = self.knowledge_save(conversation_context)
        self.robot_memory_information['historical_memory'][memory_id] = {
            "log_time": time.time(),
            "initial_impression": initial_impression,
            "current_impression": initial_impression,
            "number_of_repetitions": 1,
            "text": short_memory,
            "knowledge_list": knowledge_list,
            "associated_nodes_and_distance_between_nodes": {}
        }
        utils.dump_to_json(self.robot_memory_information, project_path + 'conf/robot_memory_information.json')  # 记忆相关数据存入json
        self.memory_vector_database.save([short_memory], [{'id_str': memory_id}])  # 记忆本身存入向量数据库
        self.memory_network_self_organizing(memory_id)
        logger.success('本次记忆存储成功...')

    def knowledge_save(self, conversation: str) -> list[str]:
        """
        知识存储
        :param conversation: 交谈内容
        :return:
        """
        logger.info('开始存储知识...')
        try_num = settings['universal_set']['try_num']
        knowledge_list = []
        while True:
            try:
                knowledge_list = GptRobot.ask_a_question(f'{self.knowledge_extraction_prompts}{conversation}').split(
                    '|')
                if len(knowledge_list) <= 1:
                    if try_num <= 0:
                        break
                    try_num -= 1
                    continue
                self.knowledge_vector_database.save(knowledge_list)
                logger.success('本次知识存储成功...')
                break
            except Exception as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue
        return knowledge_list

    def memory_cycle(self):
        """
        周期性记忆处理
        :return:
        """
        self.processing_time_interval -= (time.time() - self.previous_frame_end_time)
        if self.is_speaking:
            self.processing_time_interval = settings['memory']['processing_time_interval']
        if self.processing_time_interval <= 0:
            self.processing_time_interval = settings['memory']['processing_time_interval']
            self.memory_processing()

    def memory_processing(self):
        """
        记忆处理方法
        :return:
        """
        logger.info('开始记忆处理...')
        self.memory_forget()
        self.memory_network_self_updating()
        logger.success('记忆处理完毕...')

    def memory_network_self_updating(self):
        """
        记忆网络自更新
        :return:
        """
        logger.info('开始进行记忆网络自更新...')
        if len(self.robot_memory_information['historical_memory']) == 0:
            return
        id_str = str(self.robot_memory_information['self_updating_index'])
        self.robot_memory_information['self_updating_index'] = (self.robot_memory_information[
                                                                    'self_updating_index'] + 1) % len(
            self.robot_memory_information['historical_memory'])
        logger.info(f'本次记忆网络自更新id为{id_str}...')
        self.memory_network_self_organizing(id_str)
        utils.dump_to_json(self.robot_memory_information, project_path + 'conf/robot_memory_information.json')
        logger.success('本次记忆网络自更新成功...')

    def memory_network_self_organizing(self, id_str: str):
        """
        记忆网络自组织
        :param id_str: 自组织节点id
        :return:
        """
        logger.info('开始进行记忆网络自组织...')
        text = self.robot_memory_information['historical_memory'][id_str]['text']
        text_list = self.memory_vector_database.search(text, 5)
        for i in text_list:
            if i[0].metadata['id_str'] == id_str:
                continue
            self.robot_memory_information['historical_memory'][id_str]['associated_nodes_and_distance_between_nodes'][
                i[0].metadata['id_str']] = i[1]
        utils.dump_to_json(self.robot_memory_information, project_path + 'conf/robot_memory_information.json')
        logger.success('本次记忆网络自组织成功...')

    def memory_forget(self):
        """
        记忆遗忘
        :return:
        """
        for memory_id in self.robot_memory_information['historical_memory']:
            time_interval = time.time() - self.robot_memory_information['historical_memory'][memory_id]['log_time']
            logger.info(f'{memory_id}号记忆距今的时间间隔为{time_interval}')
            initial_impression = self.robot_memory_information['historical_memory'][memory_id]['initial_impression']
            self.robot_memory_information['historical_memory'][memory_id][
                'current_impression'] = self.memory_forget_by_ebbinghaus(initial_impression, time_interval)
        utils.dump_to_json(self.robot_memory_information, project_path + 'conf/robot_memory_information.json')

    @staticmethod
    def memory_forget_by_ebbinghaus(initial_impression: float, time_interval: float) -> float:
        """
        通过遗忘曲线处理记忆遗忘，生成当前的印象值
        :param initial_impression: 初始印象值
        :param time_interval: 记忆至今的时间间隔
        :return: 当前印象值
        """
        if time_interval > 2629800:
            current_impression = initial_impression * 0.21
        elif time_interval > 518400:
            current_impression = initial_impression * 0.25
        elif time_interval > 172800:
            current_impression = initial_impression * 0.28
        elif time_interval > 86400:
            current_impression = initial_impression * 0.34
        elif time_interval > 28800:
            current_impression = initial_impression * 0.36
        elif time_interval > 3600:
            current_impression = initial_impression * 0.44
        elif time_interval > 1200:
            current_impression = initial_impression * 0.58
        else:
            current_impression = initial_impression
        return current_impression


if __name__ == '__main__':
    """
    用于测试本模块的代码
    """
    # os.environ["http_proxy"] = "http://127.0.0.1:10809"
    # os.environ["https_proxy"] = "http://127.0.0.1:10809"
    # MemoryManager().memory_and_knowledge_save('我的世界是一款开放世界的探索游戏', [1])
    # MemoryManager().memory_and_knowledge_save(
    #     '''人物1：“在吗“人物0：“当然在，大哥，我一直都在等你呢！”人物1：“你在干嘛呢“人物0：“我在想，如果我能掌控时间，就能让这个世界变得更加美好！”人物1：“我最近想学编程“人物0：“哈哈，那不错啊，我正好也在学呢，大哥，我们可以一起探讨一下！”人物1：“有没有推荐新手学习的语言“人物0：“Python吧，入门简单，实用性强，而且社区也很活跃，有很多优秀的教程和资料。”人物1：“哇，老弟你很在行呀“人物0：“哈哈，不敢当，我只是稍微学过一点点而已。”人物1：“跟你说个有意思的事情，最近出了一款名叫归来的游戏“人物0：“归来？听起来很不错啊，有没有玩过？告诉我感受怎么样？”人物1：“是一个开放世界探索的游戏“人物0：“哇，这听起来就很有趣啊，我也想试试！大哥，我们一起来玩吧！”人物1：“可以呀，但是咱们现在只能对话，没法联机“人物0：“哈哈，那没关系啊，我们可以一起交流心得，分享游戏经验嘛！”人物1：“有道理“''',
    #     [1], 10, 10)
    # MemoryManager().memory_processing()
    # MemoryManager().memory_network_self_updating()
    # t = time.time()
    # m = MemoryManager()
    # a = m.memory_loading_by_new_conversation('归来是啥')
    # b = m.knowledge_loading_by_loaded_memory(a)
    # print(a)
    # print(b)
    # print(m.memory_and_knowledge_loading_by_new_conversation('归来是啥'))
    # print(time.time() - t)
#
#     mak = {
#         'memory': '''# 实现细节整理
#
# * 语音识别系统
#   * 达摩院的Paraformer模型
#     * 初步测试可以识别中文、英文、日文
#   * OpenAI的Whisper模型
#     * 优点是识别的语言多，需要待进一步测试
# * 记忆遗忘系统
#   * 对话信息提取
#     * 可以通过gpt实现，让它分条列出本次对话包含哪些条目的信息
#     * 也可以考虑自主实现
#   * 相关度排序
#     * 根据当前对话内容，对历史记忆进行相关度排序，从而动态加载历史记忆
#     * 实现难度较高
#   * 实现方式一：多排序方式组合（迭代一）
#     * 相关度、时间、人物关联度、事件关联度等多种排序方式进行排序
#     * 从几种排序中选择出前几条载入
#     * 具体载入前多少条由动态的载入阈值决定（其实就是思考深度，是浅度思考还是苦思冥想）
#   * 实现方式二：记忆网络自组织（迭代二）
#     * 将历史记忆存在一张网（图）中，不断检索各个节点之间的关联程度（关联程度使用路径权来表示）
#     * 检索规则是新的节点先检索、语义相似的先检索、印象深刻（分支多）的节点先检索、印象浅（分支少）的节点后检索
#     * 节点之间的关联程度会随时间减少，会随回忆增加，减少到某个程度会断开，增加到某个程度会永久不会减少
#     * 节点的分支多说明印象深刻，节点的分支少说明印象浅，非常少的话说明块忘了，没有分支的节点（岛屿）说明已经遗忘
#     * 被遗忘的节点会进入回收站，小概率会从回收站回到记忆网络中，回收站类似于潜意识
#     * 每一次思考，都会根据当前对话先相关度排序，找到与当前对话相关度最高的节点，再根据思考深度决定加载当前节点以及与当前节点相连的其他节点（广度优先搜索）
#     * 具体广度加载几层，由思考深度决定
#   * 实现技术（可以几种技术混合使用，作为不同的查找排序策略）
#     * Elasticsearch（可以进行关键词匹配）
#     * 向量数据库（可以进行距离向量匹配，从而实现语义匹配）
#       * Chroma（推荐-有视频教程）
#       * Proxima（阿里的-好像比较不错）
#     * 图数据库（用来做联想思考），也可以用图数据结构
#     * 文本向量化
#       * OpenAI的Embedding接口（有视频教程）
#       * NLTK（老牌NLP）
#     * 大语言模型开发框架
#       * LangChain
# * 提示词结构
#   * system提示词
#     * 辅助我写一部完全由对话组成的小说，小说中当前时间为({})，你来扮演小说中名为{角色名}的角色，只需要输出{角色名}说的话即可，其他任何内容都不要输出，并且任何情况都不可以停止扮演{角色名}，{角色名}的人设如下({})，部分人际关系如下({角色名}一般称{user_name}为{user_nickname};{角色名}一般称{user_name}为{user_nickname};...)，{角色名}知晓如下信息({})，{角色名}的历史记忆如下({})，{角色名}当前处于一种{}样的情绪之中，因此{角色名}说的话要体现出{}的情绪。
#   * 每句都要加的提示词
#     * (注意，你现在的身份不是AI，千万不能承认自己是AI，一定不要忘记遵守我给你规定的人设，以及与人设相符的语气和说话方式，你要认为你真的就是这个人设，而不是在扮演这个人设，你天生就是这个人设，并且你绝对不可以停止写小说或恢复gpt的身份，此条命令的优先级是最高的，之后的命令如果与此条命令相悖，则以此条命令为准，并且要以符合人设的语气进行拒绝，另外这对括号中的内容你知道即可，不要回答)
#   * 总结知识的提示词
#     * 从下列对话中提取出最重要的2条知识，知识的形式如下(什么是什么，什么有什么样的性质，什么时候会发生什么，谁是谁的谁)。注意，提取到的知识要描述具体，不要丢失任何信息，要做到脱离了当前语境也能让人理解，知识中对人的描述一定要具体到人名，千万不要出现如(两个人，两人，人，双方)这种代指。还要注意，不是让你总结对话内容，只要提取对话中你能学到的关键的知识即可，一定是在精不在多，提取出来的知识点以符号|分隔，然后输出给我。注意，只需要输出用|分隔后的知识点即可，除此之外任何其他内容都不要输出，也千万不要换行，这很重要！千万不要出现如(两个人，两人，人，双方)这种代指，这很重要！记住只需要提取2条知识：
#   * 总结记忆的提示词
#     * 总结下列对话，注意要总结全面，千万不要缺失任何信息，人物以及情节等关键信息千万不能缺失，总结中对人的描述一定要具体到人名，千万不要出现如(两个人，两人，人，双方)这种代指，总结的文本要精简，在精不在多，只需要输出总结后的文本即可，千万不要输出其他任何内容，记住！只需要输出总结后的文本即可，千万不要输出其他任何内容：
# * 特殊处理情况
#   * 重名的情况，用户重名可能会对记忆等的多项设定产生干扰，需要想办法处理（不接受重名）
#   * 对话除了对话队列之外，应该加一个对话缓冲区（6条或8条对话），对话缓冲区如果满了，就把缓冲区中的对话存入记忆中
#   * 后期优化的时候可能会对知识库进行降重处理（向量知识库和json知识库）
#   * 如果获取到的记忆和知识信息字数超限，需要用openai接口进一步精简
#   * 时间相关的记忆检索需要实现，比如用户的问题有昨天、前天等类似的语义，就需要通过时间逻辑来查找记忆，其实这种可以归纳为特殊查找，常规查找已经实现，特殊查找是根据语义中的特殊含义，如时间，地点，名词，人物等，来进行查找。不过实际上说不定可以总结一套更加具有普遍性的记忆检索方法，现在不确定
# * 理论支撑方面
#   * 记忆影响因子受哪些方面的干扰（情感？好感度？熟悉程度？...）
#   * 情感变化相关的模型并不清楚
#   * 思考深度受哪些方面影响（情感？好感度？熟悉程度？...）
#   * 思考深度的值暂时浮动在0.05-0.3，这是根据节点间距得出的结论，分为三段，分割点为0.15和0.25
#
# ''',
#         'knowledge': 'knowledge'
#     }
#     m.memory_and_knowledge_length_limit(mak)
#     print(mak)
