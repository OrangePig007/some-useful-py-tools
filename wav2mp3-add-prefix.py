import os
from pydub import AudioSegment

# 要处理的文件夹路径
INPUT_DIR = r"D:\py中文转写\rm10AudioClip"

# mp3输出目录（可以与输入相同）
OUTPUT_DIR = INPUT_DIR

# 前缀
PREFIX = "Richman10_vo_"

def convert_wav_to_mp3():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file_name in os.listdir(INPUT_DIR):
        if file_name.lower().endswith(".wav"):
            wav_path = os.path.join(INPUT_DIR, file_name)
            mp3_name = PREFIX + os.path.splitext(file_name)[0] + ".mp3"
            mp3_path = os.path.join(OUTPUT_DIR, mp3_name)

            # 转换
            print(f"正在转换：{file_name} -> {mp3_name}")
            sound = AudioSegment.from_wav(wav_path)
            sound.export(mp3_path, format="mp3", bitrate="192k")

    print("✅ 全部转换完成！")

if __name__ == "__main__":
    convert_wav_to_mp3()
