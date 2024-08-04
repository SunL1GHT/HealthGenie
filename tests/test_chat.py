from openai import OpenAI

"""
curl --location 'http://localhost:10809/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Accept: application/json' \
--data '{
    "model": "genie_chat",
    "messages": [
        {
            "role": "user",
            "content": "你是谁？"
        }
    ],
    "temperature": 1,
    "top_p": 1,
    "n": 1,
    "stream": false,
    "max_tokens": 250,
    "presence_penalty": 0,
    "frequency_penalty": 0
}'
"""
client = OpenAI(
    api_key="sk-xxx',",
    base_url="http://localhost:10002/v1"
)
model_name = client.models.list().data[0].id
print(model_name)
response = client.chat.completions.create(
  model=model_name,
  messages=[
    {"role": "system", "content": "你是一位专业的、经验丰富的医学教授。你需要根据患者的提问，提供准确、全面且详尽的答复。"},
    {"role": "user", "content": " 孩子发烧老不好怎么办？"},
  ],
    temperature=0.8,
    top_p=0.8,
    max_tokens=512
)
print(response)