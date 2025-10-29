import os
import torch
import soundfile as sf
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# ---------- 配置 ----------
AUDIO_DIR = r"D:\py中文转写\提取\AudioClip\jp"
OUTPUT_FILE = r"D:\py中文转写\recognition_1020_jp.txt"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 使用台湾闽南语模型
# MODEL_NAME = "TSukiLen/whisper-small-chinese-tw-minnan-hanzi"
MODEL_NAME = "openai/whisper-small"

# ---------- 初始化模型 ----------
def init_model():
    print(f"加载模型 {MODEL_NAME} 中...")
    processor = WhisperProcessor.from_pretrained(MODEL_NAME)
    model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME).to(DEVICE)
    print("模型加载完成")
    return processor, model

# ---------- 音频加载 ----------
def load_audio(audio_path, target_sample_rate=16000):
    try:
        waveform, sr = sf.read(audio_path)
        # 如果是立体声，取平均变成单声道
        if len(waveform.shape) > 1:
            waveform = waveform.mean(axis=1)
        # 重采样
        if sr != target_sample_rate:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=target_sample_rate)
        # 转成 torch.Tensor
        return torch.from_numpy(waveform).float()
    except Exception as e:
        print(f"加载音频 {audio_path} 失败: {e}")
        return None

# ---------- 音频识别 ----------
def recognize_audio(processor, model, audio_path):
    waveform = load_audio(audio_path)
    if waveform is None:
        return None
    try:
        # 台湾闽南语模型已经是专门训练的，不需要额外指定 language
        input_features = processor(waveform, sampling_rate=16000, return_tensors="pt").input_features.to(DEVICE)
        predicted_ids = model.generate(input_features)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        return transcription
    except Exception as e:
        print(f"处理 {audio_path} 时出错: {e}")
        return None

# ---------- 批量识别 ----------
def batch_recognize_to_single_file():
    if not os.path.exists(AUDIO_DIR):
        print("音频目录不存在")
        return

    processor, model = init_model()
    supported_formats = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}

    # 获取所有音频文件并按数字排序
    audio_files = [
        f for f in os.listdir(AUDIO_DIR)
        if os.path.splitext(f)[1].lower() in supported_formats
    ]
    audio_files.sort(key=lambda x: int(os.path.splitext(x)[0]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for filename in audio_files:
            audio_path = os.path.join(AUDIO_DIR, filename)
            text = recognize_audio(processor, model, audio_path)
            if text:
                f_out.write(text + "\n")
                f_out.flush()
                print(f"{filename}: {text}\n")
    print("全部处理完成。")

# ---------- 主程序 ----------
if __name__ == "__main__":
    batch_recognize_to_single_file()
