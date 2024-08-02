import openai
base_url = "http://127.0.0.1:10001/v1"
data = {
    "model": "genie_chat",
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好，我是人工智能大模型"},
        {"role": "user", "content": "请用100字左右的文字介绍自己"},
    ],
    "stream": False,
    "temperature": 0.7,
}

client = openai.Client(base_url=base_url, api_key="EMPTY")
resp = client.chat.completions.create(**data)
for r in resp:
    print(r)