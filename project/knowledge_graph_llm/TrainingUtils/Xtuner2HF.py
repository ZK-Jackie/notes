import json
from tqdm import tqdm

def toGLM(origin, dest):
    # 读取原始的JSON文件
    with open(origin, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 创建一个新的列表来存储转换后的数据
    new_data = []

    # 遍历原始数据中的每个元素
    for item in tqdm(data, desc='Transforming'):
        # 创建一个新的字典来存储转换后的对话
        new_item = {"conversations": []}
        # 遍历每个对话
        for conversation in item["conversation"]:
            # 将"system", "input", "output"转换为"role"，并将对应的内容转换为"content"
            new_item["conversations"].append({"role": "system", "content": conversation["system"]})
            new_item["conversations"].append({"role": "user", "content": conversation["input"]})
            new_item["conversations"].append({"role": "assistant", "content": conversation["output"]})
        # 将转换后的对话添加到新的数据列表中
        new_data.append(new_item)

    # 将转换后的数据写入新的JSONL文件
    with open(dest, 'w', encoding='utf-8') as f:
        for item in new_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')