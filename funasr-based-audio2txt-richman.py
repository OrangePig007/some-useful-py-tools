from funasr import AutoModel
import os

# 要装环境ffmpeg 还有numpy降级pip install "numpy<2" --force-reinstall
# 第一次要下载2g左右模型文件。

AUDIO_DIR = r"D:\py中文转写\rm10AudioClip"
OUTPUT_FILE = r"D:\py中文转写\rm10-1021.txt"
BATCH_SIZE = 92  # 每处理92个文件写入分隔线

def init_model():
    print("加载模型中...")
    model = AutoModel(
        model="paraformer-zh",
        vad_model="fsmn-vad",
        punc_model="ct-punc",
        device="cpu"
    )
    print("模型加载完成")
    return model

def recognize_audio(model, audio_path):
    try:
        result = model.generate(input=audio_path)
        text = ""
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and "text" in item:
                    text += item["text"]
        elif isinstance(result, str):
            text = result
        return text
    except Exception as e:
        print(f"处理 {audio_path} 时出错: {e}")
        return None

def batch_recognize_to_single_file():
    if not os.path.exists(AUDIO_DIR):
        print("音频目录不存在")
        return
    
    model = init_model()
    supported_formats = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

    # 获取所有音频文件并按数字排序
    audio_files = [
        f for f in os.listdir(AUDIO_DIR)
        if os.path.splitext(f)[1].lower() in supported_formats
    ]
    audio_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for index, filename in enumerate(audio_files, 1):  # 从1开始计数
            audio_path = os.path.join(AUDIO_DIR, filename)
            text = recognize_audio(model, audio_path)
            if text:
                line = f"{text}\n"
                f_out.write(line)
                f_out.flush()
                print(f"{filename}: {text}\n")
            
            # 每处理92个文件写入分隔线（最后一批不足92个也不额外添加）
            if index % BATCH_SIZE == 0:
                f_out.write("==============\n")
                f_out.flush()
                print(f"已处理{index}个文件，写入分隔线\n")
    
    print("全部处理完成。")


if __name__ == "__main__":
    batch_recognize_to_single_file()