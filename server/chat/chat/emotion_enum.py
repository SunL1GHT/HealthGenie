from enum import Enum


class EmotionEnum(Enum):
    """
    情绪行为分类
    """
    WAIT = '等待'  # 1
    IDLE = '待机'  # 2
    THINK = '思考'  # 3
    FEAR = '恐惧'  # 4
    ANGRY = '愤怒'  # 5
    HEAT = '厌恶'  # 6
    LIKE = '喜好'  # 7
    SAD = '悲伤'  # 8
    HAPPY = '高兴'  # 9
    AMAZED = '惊讶'  # 10
    SPEAK = '说话'  # 11
    STRUGGLE = '挣扎'  # 12

    # 0作为无状态
