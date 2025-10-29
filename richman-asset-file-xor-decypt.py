import os

# 固定配置
INPUT_DIR = r"D:\py中文转写\asset"  # 这里改成你的目录

KEY_BYTE = 0x01                    # 密钥
GROUP_SIZE = 4                     # 每 4 个字节一组
OVERWRITE = True                 # True 则直接覆盖原文件
def decrypt_file(in_path, out_path):
    with open(in_path, "rb") as f:
        data = bytearray(f.read())

    for i in range(0, len(data), GROUP_SIZE):
        data[i] ^= KEY_BYTE  # 每组第一个字节 XOR

    with open(out_path, "wb") as f:
        f.write(data)
    print(f"解密完成: {in_path} -> {out_path}")

def process_directory(directory):
    directory = os.path.abspath(directory)
    for root, _, files in os.walk(directory):
        for fname in files:
            in_path = os.path.join(root, fname)
            if OVERWRITE:
                out_path = in_path
            else:
                out_fname = fname + "_decrypted"
                out_path = os.path.join(root, out_fname)
            try:
                decrypt_file(in_path, out_path)
            except Exception as e:
                print(f"处理失败: {in_path} -> {e}")

if __name__ == "__main__":
    if not os.path.isdir(INPUT_DIR):
        print(f"目录不存在: {INPUT_DIR}")
    else:
        process_directory(INPUT_DIR)
        print("所有文件解密完成！")