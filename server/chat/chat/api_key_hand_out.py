# coding=utf-8

"""
api_key分发模块
"""
import os
import utils
from loguru import logger

settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

openai_key_list = settings['gpt_set']['api_key_list']


class ApiKeyHandOut:
    index = 0

    @staticmethod
    def get_api_key():
        logger.info(f'正在获取api_key，索引为{ApiKeyHandOut.index}...')
        ApiKeyHandOut.index = (ApiKeyHandOut.index + 1) % len(openai_key_list)
        return openai_key_list[ApiKeyHandOut.index]
