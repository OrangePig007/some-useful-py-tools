import os
import re
from pydub import AudioSegment

def merge_ogg_files(character_name, input_directory, output_file):
    # 定义分类词列表（按照需要的顺序）
    categories = ['start', 'lead', 'hurt', 'kill', 'die', 'atk', 'ulti']
    category_pattern = '|'.join(categories)

    regex = rf'{re.escape(character_name)}(_cn)?_({category_pattern})(?:_vo)?_(\d+)\.ogg'

    # 用于存储每个分类的音频文件
    categorized_files = {cat: {'cn': [], 'non_cn': []} for cat in categories}
    
    # 跟踪未匹配的文件
    unmatched_files = []
    
  # 遍历目录中的所有文件
    for filename in os.listdir(input_directory):
        if filename.endswith('.ogg'):
            # 新的正则表达式：忽略分类词和数字之间的所有内容
            match = re.match(regex, filename, re.IGNORECASE)

            if match:
                cn_flag, category, number = match.groups()
                if category in categories:
                    file_path = os.path.join(input_directory, filename)
                    if cn_flag and 'cn' in cn_flag.lower():
                        categorized_files[category]['cn'].append((int(number), file_path))
                        print(f"已识别带CN的文件: {filename}")
                    else:
                        categorized_files[category]['non_cn'].append((int(number), file_path))
                        print(f"已识别不带CN的文件: {filename}")
                else:
                    unmatched_files.append(filename)
            else:
                unmatched_files.append(filename)
    
    # 输出未匹配的文件
    if unmatched_files:
        print("\n未匹配的文件:")
        for file in unmatched_files:
            print(f"  - {file}")
    
    # 对每个分类中的文件按序号排序
    for cat in categories:
        categorized_files[cat]['cn'].sort(key=lambda x: x[0])
        categorized_files[cat]['non_cn'].sort(key=lambda x: x[0])
    
    # 创建一个空的音频段用于存储最终合并后的音频
    final_audio = AudioSegment.empty()
    
    # 按照分类词顺序合并所有音频
    for cat in categories:
        cn_files = categorized_files[cat]['cn']
        non_cn_files = categorized_files[cat]['non_cn']
        
        print(f"\n处理分类: {cat}")
        print(f"  不带CN的文件数量: {len(non_cn_files)}")
        print(f"  带CN的文件数量: {len(cn_files)}")
        
        # 输出每个分类的文件列表
        if non_cn_files:
            print("  不带CN的文件:")
            for num, path in non_cn_files:
                print(f"    - {os.path.basename(path)}")
        if cn_files:
            print("  带CN的文件:")
            for num, path in cn_files:
                print(f"    - {os.path.basename(path)}")
        
        # 合并不带cn和带cn的文件
        max_len = max(len(cn_files), len(non_cn_files))
        for i in range(max_len):
            # 添加不带cn的文件（如果存在）
            if i < len(non_cn_files):
                try:
                    audio = AudioSegment.from_ogg(non_cn_files[i][1])
                    final_audio += audio + AudioSegment.silent(duration=400)  # 添加0.6秒静音
                    print(f"  添加文件: {os.path.basename(non_cn_files[i][1])}")
                except Exception as e:
                    print(f"  错误: 无法加载 {non_cn_files[i][1]}: {e}")
            
            # 添加带cn的文件（如果存在）
            if i < len(cn_files):
                try:
                    audio = AudioSegment.from_ogg(cn_files[i][1])
                    audio = audio + 3  # 增加3dB音量
                    final_audio += audio + AudioSegment.silent(duration=600)  # 添加0.6秒静音
                    print(f"  添加文件: {os.path.basename(cn_files[i][1])}")
                except Exception as e:
                    print(f"  错误: 无法加载 {cn_files[i][1]}: {e}")
    
    # 保存合并后的文件为MP3
    if len(final_audio) > 0:
        output_dir = os.path.dirname(output_file)
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        final_audio.export(output_file, format="mp3")
        print(f"\n合并完成! 输出文件: {output_file}")
        print(f"文件时长: {len(final_audio) / 1000:.2f} 秒")  # 修正为除以1000，显示正确的秒数
    else:
        print("没有找到有效的音频文件进行合并!")

if __name__ == "__main__":
#如果是中英混合记得改时长400 600，纯中文就是500左右
    character_name = 'pam'
    input_directory = r"G:\荒野乱斗\apk\v62\帕姆中文语音"
    output_file = fr"G:\荒野乱斗\apk\v62\{character_name}-cn1.mp3"
    
    merge_ogg_files(character_name, input_directory, output_file)