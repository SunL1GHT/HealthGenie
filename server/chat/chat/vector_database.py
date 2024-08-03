# coding=utf-8
import os
import time

from embeddings_hand_out import EmbeddingHandOut
from langchain_community.vectorstores import Chroma
from loguru import logger

import utils

# 项目根目录
project_path = os.path.dirname(os.path.dirname(__file__))

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

# 向量数据库路径
vecdb_path = os.path.join(project_path, "vector_database")
memory_vecdb_path = os.path.join(vecdb_path, "memory")
knowledge_vecdb_path = os.path.join(vecdb_path, "knowledge")

class VectorDatabase:
    """
    向量数据库相关操作模块(该向量数据库存在一些问题，如不稳定，查询效率低下等，尽量不要修改本模块的代码，日后可以考虑使用更好的向量数据库)
    """

    def __init__(self, persist_directory: str, collection_name: str):
        """
        初始化向量数据库配置
        :param persist_directory: 文件存储位置
        :param collection_name: 集合名称
        """
        logger.info('正在初始化向量数据库相关信息...')
        self.embeddings = EmbeddingHandOut.get_embeddings()
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.vectordb = None
        logger.success('初始化成功...')

    def save(self, text_list: list[str], metadatas: list[dict] = None):
        """
        将数据保存至集合
        :param text_list: 文本列表
        :param metadatas: 相关数据列表
        :return:
        """

        logger.info(f'在({self.collection_name})集合中保存数据({text_list})...')
        self.embeddings = EmbeddingHandOut.get_embeddings()
        time_log = time.time()

        vectordb = Chroma.from_texts(text_list, self.embeddings, persist_directory=self.persist_directory,
                                     collection_name=self.collection_name, metadatas=metadatas)
        vectordb.persist()

        self.embeddings = EmbeddingHandOut.get_embeddings()

        self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings,
                               collection_name=self.collection_name)
        logger.success(f'保存成功，耗时{time.time() - time_log}秒...')

    def search(self, query: str, num: int) -> list:
        """
        在集合中查找相似数据
        :param query: 问题
        :param num: 相似数据条数
        :return: chromadb相似数据列表
        """

        logger.info(f'在({self.collection_name})集合中查询({query})的相关数据...')

        self.embeddings = EmbeddingHandOut.get_embeddings()

        time_log = time.time()

        if not self.vectordb:
            self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings,
                                   collection_name=self.collection_name)

        data_list = self.vectordb.similarity_search_with_score(query, num)
        logger.info(f'查到的数据：{data_list}')
        logger.success(f'查询完毕，耗时{time.time() - time_log}秒...')
        return data_list

    @staticmethod
    def self_inspection():
        """
        向量数据库自检
        :return:
        """
        if not os.path.exists(vecdb_path):
            vd1 = VectorDatabase(memory_vecdb_path, 'memory')
            vd2 = VectorDatabase(knowledge_vecdb_path, 'knowledge')
            vd1.save([''], [{'id_str': '0'}])
            vd2.save([''])
            robot_memory_information_init = {
                "self_updating_index": 0,
                "historical_memory": {
                    "0": {
                        "log_time": 0,
                        "initial_impression": 0,
                        "current_impression": 0,
                        "number_of_repetitions": 0,
                        "text": "，",
                        "knowledge_list": [],
                        "associated_nodes_and_distance_between_nodes": {
                        }
                    }
                }
            }
            utils.dump_to_json(robot_memory_information_init, os.path.join(project_path, "conf/robot_memory_information.json"))


if __name__ == '__main__':
    """
    用于测试本模块的代码
    """
    VectorDatabase.self_inspection()
    vd1 = VectorDatabase(memory_vecdb_path, 'memory')
    vd2 = VectorDatabase(knowledge_vecdb_path, 'knowledge')
    # vd1.save([''], [{'id_str': '0'}])
    # vd2.save([''])
    vd2.save(['章节测试请大家观看完视频后手动打开。', '请大家仔细打开视频上方的”学前必读“，查看成绩分布。',
             '每天定时半小时可获得一分习惯分', '每天都要锻炼30分钟身体', '5月14号', '5月13号', '5月12号', '5月15号',
             '5月11号'],
            [{'a': '1', '111': '222'}, {'b': '2'}, {'c': '3'}, {'d': '4'}, {'d': '4'}, {'d': '4'}, {'d': '4'},
             {'d': '4'}, {'d': '4'}]
            )
    print(vd2.search('试题没法自动开启', 3))
    # print(vd2.search('今天是5月13号，昨天是几号', 3))
    # print(vd2.search('最近有什么好玩的游戏吗', 8)[0][0].metadata)
