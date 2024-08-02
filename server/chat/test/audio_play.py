import requests

URL = 'http://127.0.0.1:23456/voice/vits'
proxies = {'http': 'http://127.0.0.1:23456'}
params = {
    "text": '你知道今天是什么天气吗',
    "id": "106",
    "lang": "zh",
    "format": 'wav'
}
response = requests.get(URL, params=params, proxies=proxies)

# 检查响应状态码
if response.status_code == 200:
    # 提取文件名
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        FILE_NAME = content_disposition.split("filename=")[1]
    else:
        FILE_NAME = "audio.wav"  # 如果未提供文件名，则默认为"audio.mp3"

    # 保存音频文件
    with open(FILE_NAME, "wb") as file:
        file.write(response.content)
    print("音频文件已下载:", FILE_NAME)
    print('slafdjsladfjlsdajf')
else:
    print("下载失败. 状态码:", response.status_code)
