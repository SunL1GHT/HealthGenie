# coding=utf-8
import os
import time

import openai
from loguru import logger

import utils
from api_key_hand_out import ApiKeyHandOut

# 配置信息
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/settings.json')
settings = utils.load_json_from_file(settings_path)

# 应用列表信息
applications_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'conf/applications.json')
applications = utils.load_json_from_file(applications_path)


class GptRobot:
    """
    生成型预训练变换模型
    """

    @staticmethod
    def ask_a_question(question: str, stream=False):
        """
        向模型发起会话（只问独立的问题，无上下文）
        :param stream: 是否流式输出
        :param question: 问题
        :return: 答复
        """

        logger.info('最终问题：' + str(question))

        logger.info('向语言模型发起会话...')

        data = {
            "messages": [{"role": "user", "content": question}],
            "model": settings['gpt_set']['model_engine'],
            "temperature": 1.3,
            "top_p": 0.9,
            "n": 1
        }

        answer = GptRobot.request_gpt(data, stream)

        if stream:
            return answer
        else:
            return next(answer)

    @staticmethod
    def ask_continuous_questions(question: list, stream=True):
        """
        向模型发起会话 (连续的问题，存在上下文)
        :param stream: 是否流式输出
        :param question: 问题
        :return: 答复（如果存在键 function_call ，则说明有需要执行的方法，如果不存在，则直接读取内容即可，内容的键为 content）
        """

        logger.info('最终问题：' + str(question))

        logger.info('向语言模型发起会话...')

        data = {
            "messages": question,
            "model": settings['gpt_set']['model_engine'],
            "functions": applications['application_list'],
            "temperature": 1.3,
            "top_p": 0.9,
            "n": 1
        }

        answer = GptRobot.request_gpt(data, True)
        for a in answer:
            print(a.model_dump_json())

        if stream:
            return answer
        else:
            return next(answer)

    @staticmethod
    def request_gpt(data: dict, stream=False):
        """
        调用gpt请求
        :param data: 请求数据
        :param stream: 是否流式请求
        :return: 如果配置了方法调用并且存在方法调用的情况，则返回内容上一层级，否则将返回文本内容
        """
        try_num = settings['universal_set']['try_num']
        while True:
            response = None
            try:
                logger.info('正在获取问题答案')
                client = openai.Client(api_key="EMPTY", base_url = settings['universal_set']['openai_api_proxy_url'])

                response = client.chat.completions.create(stream=stream, **data)
                if stream:
                    for line in response:
                        if line.choices[0].delta.function_call is not None:
                            yield client.chat.completions.create(**data)['choices'][0]['message']
                            # 如果存在方法调用，则返回delta层级
                        if line.choices[0].finish_reason is not None:
                            resp = '[DONE]'
                        else:
                            resp = line.choices[0].delta.content
                        yield resp
                logger.success('成功获取到模型响应...')
                logger.info(f'响应数据为：{response}')
                if 'error' in response:
                    logger.error('出现问题...')
                break
            except openai.APIConnectionError as err:
                if try_num <= 0:
                    logger.error('错误次数过多，请联系开发者...')
                    break
                logger.error(f'发生如下错误，正在重新尝试({try_num})：{err}')
                try_num -= 1
                continue
            except Exception as err:
                logger.error(f'发生如下错误：{err}')
                continue
        if 'function_call' in response.choices[0].message:
            resp = response.choices[0].message
            # 如果存在方法调用，则返回message层级
        else:
            resp = response.choices[0].message.content
        yield resp


if __name__ == '__main__':
    """
    用于测试本模块的代码
    """
    t = time.time()
    # s = GptRobot.ask_a_question(
    #     '从下列对话中提取出最重要的2条知识，知识的形式如下(什么是什么，什么有什么样的性质，什么时候会发生什么，谁是谁的谁)。注意，提取到的知识要描述具体，不要丢失任何信息，要做到脱离了当前语境也能让人理解，知识中对人的描述一定要具体到人名，千万不要出现如(两个人，两人，人，双方)这种代指。还要注意，不是让你总结对话内容，只要提取对话中你能学到的关键的知识即可，一定是在精不在多，提取出来的知识点以符号|分隔，然后输出给我。注意，只需要输出用|分隔后的知识点即可，除此之外任何其他内容都不要输出，也千万不要换行，这很重要！千万不要出现如(两个人，两人，人，双方)这种代指，这很重要！记住只需要提取2条知识：人物1：“在吗“人物0：“当然在，大哥，我一直都在等你呢！”人物1：“你在干嘛呢“人物0：“我在想，如果我能掌控时间，就能让这个世界变得更加美好！”人物1：“我最近想学编程“人物0：“哈哈，那不错啊，我正好也在学呢，大哥，我们可以一起探讨一下！”人物1：“有没有推荐新手学习的语言“人物0：“Python吧，入门简单，实用性强，而且社区也很活跃，有很多优秀的教程和资料。”人物1：“哇，老弟你很在行呀“人物0：“哈哈，不敢当，我只是稍微学过一点点而已。”人物1：“跟你说个有意思的事情，最近出了一款名叫归来的游戏“人物0：“归来？听起来很不错啊，有没有玩过？告诉我感受怎么样？”人物1：“是一个开放世界探索的游戏“人物0：“哇，这听起来就很有趣啊，我也想试试！大哥，我们一起来玩吧！”人物1：“可以呀，但是咱们现在只能对话，没法联机“人物0：“哈哈，那没关系啊，我们可以一起交流心得，分享游戏经验嘛！”人物1：“有道理“',
    #     True)
    s = GptRobot.ask_a_question('现在几点了？', False)
    for i in s:
        if i == '[DONE]':
            break
        # print(i)
    print("推理时间为：", time.time() - t)
