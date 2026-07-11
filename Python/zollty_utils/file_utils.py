import os

def read_text(filepath, encoding='utf-8'):
    """读取文本文件内容"""
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()
