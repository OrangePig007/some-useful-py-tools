import os
import re
import shutil
from pydub import AudioSegment

# 条件映射字典（包含单数和复数形式）
CONDITION_MAPPING = {
    "start": {"order": 1, "chinese": "登场时", "script": ""},
    "starts": {"order": 1, "chinese": "登场时", "script": ""},
    "lead": {"order": 2, "chinese": "局势领先时", "script": ""},
    "leads": {"order": 2, "chinese": "局势领先时", "script": ""},
    "hurt": {"order": 3, "chinese": "遭受攻击时", "script": ""},
    "hurts": {"order": 3, "chinese": "遭受攻击时", "script": ""},
    "kill": {"order": 4, "chinese": "击杀敌人时", "script": ""},
    "kills": {"order": 4, "chinese": "击杀敌人时", "script": ""},
    "die": {"order": 5, "chinese": "死亡时", "script": ""},
    "dies": {"order": 5, "chinese": "死亡时", "script": ""},
    "ulti": {"order": 6, "chinese": "使用超级技能时", "script": ""},
    "ultis": {"order": 6, "chinese": "使用超级技能时", "script": ""}
}

# 其他音效类型映射
OTHER_SFX_MAPPING = {
    "atk_sfx": {"script": "Atk SFX", "translation": "普攻音效"},
    "atk_hit": {"script": "Atk Hit", "translation": "普攻命中"},
    "reload_sfx": {"script": "Reload SFX", "translation": "填弹音效"},
    "dryfire_sfx": {"script": "Dryfire SFX", "translation": "子弹用尽"},
    "ulti_sfx": {"script": "Ulti SFX", "translation": "大招音效"},
    # 可以添加更多音效类型映射
}

def normalize_condition(condition):
    """将复数条件词转换为单数形式"""
    if condition.endswith('s'):
        singular = condition[:-1]
        if singular in CONDITION_MAPPING:
            return singular
    return condition

def main():
    # 获取输入文件夹路径
    input_folder = input("请输入包含OGG文件的文件夹路径: ").strip()
    
    # 检查文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 文件夹 '{input_folder}' 不存在。")
        return
    
    # 创建输出文件夹
    output_folder = os.path.join(input_folder, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    # 创建MP3输出文件夹
    mp3_folder = os.path.join(output_folder, "mp3")
    os.makedirs(mp3_folder, exist_ok=True)
    
    # 初始化数据结构来存储文件信息
    # 格式: {name: {condition: [file_info]}}
    files_data = {}
    
    # 正则表达式模式
    # 匹配标准语音文件（支持名字中包含下划线）
    voice_pattern = re.compile(r'^(?P<name>.+?)_(?P<condition>start|starts|lead|leads|hurt|hurts|kill|kills|die|dies|ulti|ultis)_vo_(?P<number>\d+)\.ogg$', re.IGNORECASE)
    # 匹配其他音效文件（支持名字中包含下划线）
    other_pattern = re.compile(r'^(?P<name>.+?)_(?P<type>atk_sfx|atk_hit|atk_flyback_sfx|reload_sfx|dryfire_sfx|ulti_sfx|.+?)_(?P<number>\d+)\.ogg$', re.IGNORECASE)
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.ogg'):
            name = None
            file_info = None
            
            # 首先尝试匹配标准语音文件
            match = voice_pattern.match(filename)
            if match:
                name = match.group('name')
                condition = match.group('condition').lower()
                number = int(match.group('number'))
                
                # 规范化条件词
                normalized_condition = normalize_condition(condition)
                
                file_info = {
                    'filename': filename,
                    'number': number,
                    'type': 'voice',
                    'condition': normalized_condition
                }
            
            # 如果不是标准语音文件，尝试匹配其他音效
            else:
                match = other_pattern.match(filename)
                if match:
                    name = match.group('name')
                    sound_type = match.group('type').lower()
                    number = int(match.group('number'))
                    
                    # 查找音效类型映射，如果没有找到则使用通用描述
                    if sound_type in OTHER_SFX_MAPPING:
                        script = OTHER_SFX_MAPPING[sound_type]['script']
                        translation = OTHER_SFX_MAPPING[sound_type]['translation']
                    else:
                        script = sound_type.replace('_', ' ').title()
                        translation = f"{script}音效"
                    
                    file_info = {
                        'filename': filename,
                        'number': number,
                        'type': 'other',
                        'sound_type': sound_type,
                        'script': script,
                        'translation': translation
                    }
            
            # 如果成功匹配任何一种模式，则添加到数据结构中
            if name and file_info:
                if name not in files_data:
                    files_data[name] = {}
                
                file_type = file_info['type']
                if file_type not in files_data[name]:
                    files_data[name][file_type] = []
                
                files_data[name][file_type].append(file_info)
            else:
                print(f"警告: 文件 '{filename}' 不符合命名模式，已跳过。")
    
    # 处理并生成输出
    for name, types in files_data.items():
        # 为每个名字创建一个TXT文件
        txt_filename = os.path.join(output_folder, f"{name}.txt")
        
        with open(txt_filename, 'w', encoding='utf-8') as txt_file:
            # 处理标准语音文件
            if 'voice' in types:
                # 按条件排序
                conditions_dict = {}
                for file_info in types['voice']:
                    condition = file_info['condition']
                    if condition not in conditions_dict:
                        conditions_dict[condition] = []
                    conditions_dict[condition].append(file_info)
                
                sorted_conditions = sorted(
                    conditions_dict.items(), 
                    key=lambda x: CONDITION_MAPPING[x[0]]['order']
                )
                
                # 处理每个条件
                for condition, files in sorted_conditions:
                    # 写入条件标题
                    chinese_name = CONDITION_MAPPING[condition]['chinese']
                    txt_file.write(f"=={chinese_name}==\n")
                    
                    # 按编号排序文件
                    sorted_files = sorted(files, key=lambda x: x['number'])
                    
                    # 处理每个文件
                    for file_info in sorted_files:
                        ogg_filename = file_info['filename']
                        number_str = f"{file_info['number']:02d}"  # 两位数字格式
                        
                        # 构建MP3文件名
                        mp3_filename = f"BS_{name}_{condition}_vo_{number_str}.mp3"
                        mp3_path = os.path.join(mp3_folder, mp3_filename)
                        
                        # 转换OGG到MP3
                        try:
                            ogg_path = os.path.join(input_folder, ogg_filename)
                            audio = AudioSegment.from_file(ogg_path, format="ogg")
                            audio.export(mp3_path, format="mp3")
                            print(f"已转换: {ogg_filename} -> {mp3_filename}")
                        except Exception as e:
                            print(f"错误: 无法转换文件 '{ogg_filename}': {str(e)}")
                            continue
                        
                        # 写入TXT文件
                        txt_file.write(f"{{{{BSAudio|File = {mp3_filename}|Script = |Translation = }}}}\n")
                    
                    # 在每个条件后添加空行
                    txt_file.write("\n")
            
            # 处理其他音效文件
            if 'other' in types:
                # 写入其他音效标题
                txt_file.write(f"== 其他音效 ==\n")
                
                # 按音效类型和编号排序
                sorted_files = sorted(
                    types['other'], 
                    key=lambda x: (x['sound_type'], x['number'])
                )
                
                # 处理每个文件
                for file_info in sorted_files:
                    ogg_filename = file_info['filename']
                    sound_type = file_info['sound_type']
                    number_str = f"{file_info['number']:02d}"  # 两位数字格式
                    
                    # 构建MP3文件名
                    mp3_filename = f"BS_{name}_{sound_type}_{number_str}.mp3"
                    mp3_path = os.path.join(mp3_folder, mp3_filename)
                    
                    # 转换OGG到MP3
                    try:
                        ogg_path = os.path.join(input_folder, ogg_filename)
                        audio = AudioSegment.from_file(ogg_path, format="ogg")
                        audio.export(mp3_path, format="mp3")
                        print(f"已转换: {ogg_filename} -> {mp3_filename}")
                    except Exception as e:
                        print(f"错误: 无法转换文件 '{ogg_filename}': {str(e)}")
                        continue
                    
                    # 写入TXT文件
                    script = file_info['script']
                    translation = file_info['translation']
                    txt_file.write(f"{{{{BSAudio|File = {mp3_filename}|Script = {script}|Translation = {translation}}}}}\n")
                
                # 在其他音效后添加空行
                txt_file.write("\n")
        
        print(f"已生成: {txt_filename}")
    
    print("处理完成!")
    print(f"MP3文件保存在: {mp3_folder}")
    print(f"TXT文件保存在: {output_folder}")

if __name__ == "__main__":
    main()    