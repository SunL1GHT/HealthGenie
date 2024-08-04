from openai import OpenAI
import os

# 项目根目录
project_path = os.path.dirname(os.path.dirname(__file__))

client = OpenAI(base_url="http://127.0.0.1:18080/v1", 
                api_key="EMPTY")

audio_file= open(os.path.join(project_path, "server/GptTest/files/input.wav"), "rb")
transcription = client.audio.transcriptions.create(
    model="Belle-whisper-large-v3-zh", 
    file=audio_file
)
print(transcription.text)