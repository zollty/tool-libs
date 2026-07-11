import hashlib
import os
import sys


def calculate_md5(file_path):
    """
    计算文件的MD5值

    Args:
        file_path (str): 文件路径

    Returns:
        str: 文件的MD5值，如果文件不存在或无法读取则返回None
    """
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            # 分块读取文件以避免大文件占用过多内存
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def print_files_md5(file_paths):
    """
    打印指定文件的MD5值

    Args:
        file_paths (list): 文件路径列表
    """
    for file_path in file_paths:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"{file_path} - 文件不存在")
            continue

        # 检查是否为文件（而非目录）
        if not os.path.isfile(file_path):
            print(f"{file_path} - 不是一个文件")
            continue

        md5_value = calculate_md5(file_path)
        if md5_value:
            print(f"{file_path} - {md5_value}")
        else:
            print(f"{file_path} - 计算MD5失败")


# 示例用法
if __name__ == "__main__":
    # 方式1: 通过命令行参数指定文件
    if len(sys.argv) > 1:
        file_list = sys.argv[1:]
        print_files_md5(file_list)
    else:
        # 方式2: 在代码中直接指定文件路径
        files_to_check = [
               "D:/__SYNC0-P/Desktop/New2/海外营销/Team_2505/2025年4月上双周报.docx",
               "D:/__SYNC0-P/Desktop/New2/海外营销/Team_2505/2025年4月月报.docx",
               "D:/__SYNC0-P/Desktop/New2/海外营销/Team_2505/4~6/海外营销服.docx"
        ]
        print_files_md5(files_to_check)
