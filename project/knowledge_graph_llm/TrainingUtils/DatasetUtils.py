import os
import re
import glob
import json
import jsonlines
import config
from tqdm import tqdm


class GeneralUtils:
    def convert_jsonl_to_json(self, jsonl_file_path, json_file_path):
        data = []
        # 读取jsonl文件
        with open(jsonl_file_path, 'r', encoding='utf-8') as jsonl_file:
            for line in jsonl_file:
                data.append(json.loads(line))

        # 写入json文件
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False)

    def DuIE_raw_process(self, input_path, keyword=None):
        # Check if the input is a directory or a file
        if os.path.isdir(input_path):
            # Get the list of all files in the directory
            file_list = [os.path.join(input_path, filename) for filename in os.listdir(input_path) if
                         (keyword in filename if keyword else True)]
        elif os.path.isfile(input_path):
            file_list = [input_path]
        else:
            print(f"Error: {input_path} is not a valid directory or file.")
            return
        # Create the output directory if it does not exist
        if not os.path.exists('input_dir'):
            os.makedirs('input_dir')
        # Process each file
        for input_file in file_list:
            output_file = os.path.join('input_dir', os.path.basename(input_file))
            with open(input_file, 'r', encoding='utf-8') as f_in, open(output_file, 'w', encoding='utf-8') as f_out:
                for line in tqdm(f_in, desc='Filtering'):
                    data = json.loads(line)
                    if '[KG]' in data['sentence'] and '[/KG]' in data['sentence']:
                        data['sentence'] = re.sub('\[KG\].*?\[/KG\]', '', data['sentence'])
                        data['sentence'] = data['sentence'].strip()
                        f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
                    if data['label'] == 1:
                        f_out.write(json.dumps(data, ensure_ascii=False) + '\n')

    def get_size(self, obj):
        return len(json.dumps(obj, ensure_ascii=False).encode('utf8'))

    def split_json(self, file_path, max_size):
        # 获取源文件名
        base_name = os.path.basename(file_path).split('.')[0]
        # 创建新的文件夹
        output_dir = f"{base_name}_parts/"
        os.makedirs(output_dir, exist_ok=True)

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        size = 0
        new_data = []
        file_count = 1

        for item in tqdm(data, desc='Splitting JSON'):
            item_size = self.get_size(item)
            if size + item_size > max_size:
                with open(os.path.join(output_dir, f'{base_name}_part{file_count}.json'), 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=4)
                    print(f'\'/root/ChatKG/ft-T2KG/{base_name}_part{file_count}.json\', ')
                size = 0
                new_data = []
                file_count += 1
            size += item_size
            new_data.append(item)

        if new_data:
            with open(os.path.join(output_dir, f'{base_name}_part{file_count}.json'), 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=4)

    def jsonl_to_json_array(self, jsonl_file_path, json_file_path):
        data = []
        with jsonlines.open(jsonl_file_path, 'r') as reader:
            for obj in reader:
                data.append(obj)

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def del_dup(self, origin, del_aim, out='output_del.json'):
        # 读取第一个文件
        with open(origin, 'r', encoding='utf-8') as f:
            data1 = json.load(f)

        # 读取第二个文件
        with open(del_aim, 'r', encoding='utf-8') as f:
            data2 = json.load(f)

        # 创建一个新的列表来存储剔除后的数据
        new_data = [item for item in data1 if item not in data2]

        # 将新的数据写入到一个新的文件中，并设置indent参数为4，使输出的JSON字符串有缩进
        with open(out, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)


class XtunerDataset:

    def check_json_file(self, file_path):
        # Load the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Iterate over each element in the data
        for i, element in enumerate(data):
            # Check if the element has exactly one key-value pair with the key "conversation"
            if list(element.keys()) != ['conversation']:
                print(f"Element {i} does not have exactly one key-value pair with the key 'conversation': {element}")
                continue
            # Check if the value of "conversation" is a list with exactly one element
            conversation = element['conversation']
            if not isinstance(conversation, list) or len(conversation) != 1:
                print(
                    f"Element {i} does not have a 'conversation' value that is a list with exactly one element: {element}")
                continue
            # Check if the first element of "conversation" is a dictionary with exactly three keys, and all values are strings
            conversation_element = conversation[0]
            if not isinstance(conversation_element, dict) or len(conversation_element) != 3 or not all(
                    isinstance(value, str) for value in conversation_element.values()):
                print(
                    f"Element {i} does not have a first 'conversation' element that is a dictionary with exactly three keys, and all values are strings: {element}")

    def count_token(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        element_count = len(data)
        max_token_count = max(
            sum(len(str(key)) + len(str(value)) for key, value in element.items()) for element in data)

        print(f"Number of elements: {element_count}")
        print(f"Max total count: {max_token_count}")

    def _amend_conversation(self, conversation):
        conversation['conversation'][0]['input'] = '```' + conversation['conversation'][0]['input'] + '```'
        conversation['conversation'][0]['output'] = json.dumps(
            conversation['conversation'][0]['output'], ensure_ascii=False, indent=2)
        return conversation

    def convert_format(self, input_jsonl, output_jsonl):
        if not os.path.exists('output_dir'):
            os.makedirs('output_dir')
        with jsonlines.open(input_jsonl, mode='r') as f_in, jsonlines.open(output_jsonl, mode='w') as f_out:
            last_sentence = None
            conversation = None
            for line in tqdm(f_in, desc="Processing lines"):
                sentence_b_parts = line['sentence_b'].split(',')
                if line['sentence'] != last_sentence:
                    if conversation is not None:
                        f_out.write(self._amend_conversation(conversation))
                    conversation = {
                        'conversation': [
                            {
                                'system': config.SYS_PROMPT,
                                'input': line['sentence'],
                                'output': []
                            }
                        ]
                    }
                output_obj = {
                    'node_1': sentence_b_parts[0],
                    'edge': sentence_b_parts[1],
                    'node_2': sentence_b_parts[2] if len(sentence_b_parts) > 2 else ''
                }
                if output_obj not in conversation['conversation'][0]['output']:
                    conversation['conversation'][0]['output'].append(output_obj)
                last_sentence = line['sentence']
            if conversation is not None:
                f_out.write(self._amend_conversation(conversation))

    def find_files(self, directory, pattern):
        return glob.glob(os.path.join(directory, pattern))

    def merge_files(self, input_path, keyword=None):
        # Check if the input is a directory or a file
        if os.path.isdir(input_path):
            # Get the list of all files in the directory
            file_list = [os.path.join(input_path, filename) for filename in os.listdir(input_path) if
                         (keyword in filename if keyword else True) and filename.endswith('.jsonl')]
        elif os.path.isfile(input_path):
            file_list = [input_path]
        else:
            print(f"Error: {input_path} is not a valid directory or file.")
            return
        # Create an empty list to store all objects
        data = []
        # Iterate over each file
        for file_path in tqdm(file_list, desc="Merging files"):
            # Open the file
            with jsonlines.open(file_path, mode='r') as f_in:
                # Add each object in the file to the list
                for obj in f_in:
                    data.append(obj)
        # Define the output file name
        merge_file_name = os.path.join(os.path.dirname(input_path), "merged_file.json")
        # Write the list to a new JSON file
        with open(merge_file_name, 'w', encoding='utf-8') as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=4)

    def process_files(self, path):
        if os.path.isfile(path):
            self.process_file(path)
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                self.process_file(file_path)
        else:
            print(f"Error: {path} is not a valid file or directory.")

    def process_file(self, input_file_name):
        output_file = os.path.join('output_dir', os.path.basename(input_file_name).replace('input', 'output'))
        self.convert_format(input_file_name, output_file)

    def toGLM(self, origin, dest):
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


# import jieba
# class statistic():
#     def count_tokens_in_file(self, file_path):
#         with open(file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#
#         max_user_tokens = 0
#         max_assistant_tokens = 0
#
#         for item in data:
#             for conversation in item['conversations']:
#                 if conversation['role'] == 'user':
#                     tokens = len(list(jieba.cut(conversation['content'])))
#                     max_user_tokens = max(max_user_tokens, tokens)
#                 elif conversation['role'] == 'assistant':
#                     tokens = len(list(jieba.cut(conversation['content'])))
#                     max_assistant_tokens = max(max_assistant_tokens, tokens)
#
#         return max_user_tokens, max_assistant_tokens
#
#     def count_tokens_in_all_files(self, directory):
#         max_user_tokens = 0
#         max_assistant_tokens = 0
#
#         for filename in tqdm(os.listdir(directory), desc='Processing Files'):
#             if filename.startswith('hf') and filename.endswith('.json'):
#                 file_path = os.path.join(directory, filename)
#                 user_tokens, assistant_tokens = self.count_tokens_in_file(file_path)
#                 max_user_tokens = max(max_user_tokens, user_tokens)
#                 max_assistant_tokens = max(max_assistant_tokens, assistant_tokens)
#
#         return max_user_tokens, max_assistant_tokens


util = GeneralUtils()
# util.DuIE_raw_process('raw_dir', 'dev')

# xtuner_util = XtunerDataset()
# xtuner_util.process_files('input_dir')
# xtuner_util.merge_files('output_dir', 'dev')
# xtuner_util.check_json_file('val.json')
# xtuner_util.toGLM('train.json', 'train.jsonl')
# xtuner_util.count_token('T2KG_XTuner/T2KG_XTuner_train.json')

# 使用函数
util.convert_jsonl_to_json('T2KG_ChatGLM3/T2KG_ChatGLM3_test.jsonl', 'T2KG_ChatGLM3/T2KG_ChatGLM3_test.json')
util.convert_jsonl_to_json('T2KG_ChatGLM3/T2KG_ChatGLM3_train.jsonl', 'T2KG_ChatGLM3/T2KG_ChatGLM3_train.json')
util.convert_jsonl_to_json('T2KG_ChatGLM3/T2KG_ChatGLM3_val.jsonl', 'T2KG_ChatGLM3/T2KG_ChatGLM3_val.json')