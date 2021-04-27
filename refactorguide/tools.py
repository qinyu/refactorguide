# coding=utf-8
import os


def write_file(dir, file, *content):
    os.makedirs(dir, exist_ok=True)
    with open(dir + "/" + file, 'w', encoding='utf-8') as f:
        f.write(''.join(content))
