import os
import json
import jieba
from tqdm import tqdm

def count_tokens_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    max_user_tokens = 0
    max_assistant_tokens = 0

    for item in data:
        for conversation in item['conversations']:
            if conversation['role'] == 'user':
                tokens = len(list(jieba.cut(conversation['content'])))
                max_user_tokens = max(max_user_tokens, tokens)
            elif conversation['role'] == 'assistant':
                tokens = len(list(jieba.cut(conversation['content'])))
                max_assistant_tokens = max(max_assistant_tokens, tokens)

    return max_user_tokens, max_assistant_tokens

def count_tokens_in_all_files(directory):
    max_user_tokens = 0
    max_assistant_tokens = 0

    for filename in tqdm(os.listdir(directory), desc='Processing Files'):
        if filename.startswith('hf') and filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            user_tokens, assistant_tokens = count_tokens_in_file(file_path)
            max_user_tokens = max(max_user_tokens, user_tokens)
            max_assistant_tokens = max(max_assistant_tokens, assistant_tokens)

    return max_user_tokens, max_assistant_tokens

# Replace 'your_directory' with your actual directory path
max_user_tokens, max_assistant_tokens = count_tokens_in_all_files('T2KG/t2kg_train_parts/')

print(f'Maximum number of tokens in user content: {max_user_tokens}')
print(f'Maximum number of tokens in assistant content: {max_assistant_tokens}')