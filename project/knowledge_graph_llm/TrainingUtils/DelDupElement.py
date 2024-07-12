import json
import os


def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    return data


import ast

def remove_duplicates_in_output(data):
    for item in data:
        output_str = item['conversation'][0]['output']
        output_str = output_str.replace('\n', '').replace('\t', '').replace('\\n', '').replace('\\t', '')  # remove all newline and tab characters
        output_list = json.loads(output_str)  # parse the string to list
        output_list = list(set(json.dumps(obj) for obj in output_list))  # remove duplicates
        output_list = [json.loads(obj_str) for obj_str in output_list]  # convert each string back to dictionary
        output_str = json.dumps(output_list)  # dump the list to string
        item['conversation'][0]['output'] = output_str
    return data


def process_file(filename):
    data = load_json_file(filename)
    data = remove_duplicates_in_output(data)
    save_json_file(filename, data)


def main():
    for filename in ['train.json']:
        process_file(filename)


if __name__ == "__main__":
    main()
