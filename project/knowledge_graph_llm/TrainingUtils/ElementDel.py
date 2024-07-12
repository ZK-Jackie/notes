import json

# 读取第一个文件
with open('new_file.json', 'r', encoding='utf-8') as f:
    data1 = json.load(f)

# 读取第二个文件
with open('D:\Projects\PycharmProjects\BigData\\res\knowledge_graph_llm\TrainingUtils\\xtuner_train\\2\merged_output_part6_part12_part3_part2.json', 'r', encoding='utf-8') as f:
    data2 = json.load(f)

# 创建一个新的列表来存储剔除后的数据
new_data = [item for item in data1 if item not in data2]

# 将新的数据写入到一个新的文件中，并设置indent参数为4，使输出的JSON字符串有缩进
with open('new_file_1.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)