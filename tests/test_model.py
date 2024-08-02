from lmdeploy import pipeline, GenerationConfig, TurbomindEngineConfig

gen_config = GenerationConfig(top_p=0.8,
                              top_k=40,
                              temperature=0.8,
                              max_new_tokens=512)
pipe = pipeline('/root/HealthGenie/internlm2_5-7b-chat')
# prompts = [[{
#     'role': 'user',
#     'content': '生成一段以狐狸，兔子为主角，关于追逐，机智，森林的300字的童话故事。'
# }]]
response = pipe(['孩子发烧老不好，怎么办？'],
                gen_config=gen_config)
# response = pipe(prompts)
print(response)