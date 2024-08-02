# pyrec.py 文件内容
import pyaudio

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
RECORD_SECONDS = 2


def rec():
    p_audio = pyaudio.PyAudio()

    stream = p_audio.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

    while True:
        print("开始录音,请说话......")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            print(i)
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束,请闭嘴!")


if __name__ == '__main__':
    rec()
