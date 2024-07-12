import os
import json
import random


def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    return data


def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def remove_duplicates(val_data, test_data):
    test_inputs = {item['conversation'][0]['input'] for item in test_data}
    val_data = [item for item in val_data if item['conversation'][0]['input'] not in test_inputs]
    return val_data


def split_data(data, ratio):
    random.shuffle(data)
    split_index = int(len(data) * ratio)
    return data[:split_index], data[split_index:]


def main():
    train_data = load_json_file('train.json')
    val_data = load_json_file('val.json')
    test_data = load_json_file('test.json')

    val_data = remove_duplicates(val_data, test_data)
    train_data = remove_duplicates(train_data, val_data)

    all_data = train_data + val_data + test_data
    random.shuffle(all_data)

    train_ratio = 0.8
    val_ratio = 0.1
    test_ratio = 0.1

    train_index = int(len(all_data) * train_ratio)
    val_index = int(len(all_data) * (train_ratio + val_ratio))

    train_data = all_data[:train_index]
    val_data = all_data[train_index:val_index]
    test_data = all_data[val_index:]

    save_json_file('train.json', train_data)
    save_json_file('val.json', val_data)
    save_json_file('test.json', test_data)


if __name__ == "__main__":
    main()
