# coding=utf-8
import os


def write_file(file_path, *content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(''.join(content))
