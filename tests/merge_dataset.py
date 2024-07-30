import os.path
import json
    
if __name__== "__main__":
    # base_path="/root/shibing624/medical/finetune/"
    # 初始化一个空列表，用于存储所有文件的内容
    combined_text_lines = []

    data_files = [
        '/root/shibing624/medical/finetune/train_zh_0.json', 
        '/root/shibing624/medical/finetune/train_en_1.json', 
        '/root/shibing624/medical/finetune/valid_zh_0.json', 
        '/root/shibing624/medical/finetune/valid_en_1.json', 
        '/root/shibing624/medical/finetune/test_zh_0.json', 
        '/root/shibing624/medical/finetune/test_en_1.json'
    ]
    for filename in data_files:
        # 检查文件扩展名是否为.json
        if filename.endswith('.json'):
            # 打开并读取文件内容
            with open(filename, 'r', encoding='utf-8') as file:
                lines = (line for line in file if line.strip())
                combined_text_lines.extend(lines)

    # 将所有内容合并为一个单一的字符串，每个文件的内容之间可以加一个分隔符
    combined_text = ''.join(line for line in combined_text_lines if line.strip())

    # 将合并后的内容写入到新文件中
    with open('./datasets/combined_data.json', 'w', encoding='utf-8') as output_file:
        output_file.write(combined_text)

    print('文本文件已合并完毕。')