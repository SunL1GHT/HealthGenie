# coding=utf-8

"""
Embedding模块
"""
import os
import utils
from loguru import logger

from api_key_hand_out import ApiKeyHandOut

settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

embedding_type = settings['embedding_set']['type']

class EmbeddingHandOut:

    @staticmethod
    def get_embeddings():
        """根据配置获取对应的embedding类"""
        logger.info(f'正在处理Embedding...')
        if embedding_type == 'openai':
            from langchain.embeddings.openai import OpenAIEmbeddings
            return OpenAIEmbeddings(openai_api_key=ApiKeyHandOut.get_api_key())
        elif embedding_type == 'jinaai':
            from langchain_community.embeddings import JinaEmbeddings
            embeddings = JinaEmbeddings(
                jina_api_key=settings['embedding_set']['api_key'],
                model_name=settings['embedding_set']['model_engine']
            )
            return embeddings
        else:
            logger.info(f'无法解析Embedding配置')
            raise ValueError("Unsupported embedding type")


if __name__=="__main__":
    text = "测试一下"
    query_result = EmbeddingHandOut.get_embeddings().embed_query(text)
    print(query_result)



