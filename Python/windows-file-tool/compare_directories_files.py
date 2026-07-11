import os
from pathlib import Path
import time


def get_file_info(file_path):
    """
    获取文件信息：文件名和修改时间

    Args:
        file_path (Path): 文件路径

    Returns:
        dict: 包含文件名和修改时间的字典
    """
    stat = file_path.stat()
    return {
        'name': file_path.name,
        'mtime': stat.st_mtime,
        'size': stat.st_size,
        'path': file_path
    }


def format_mtime(mtime):
    """
    格式化修改时间

    Args:
        mtime (float): 时间戳

    Returns:
        str: 格式化的时间字符串
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))


def find_files_by_name_and_time(dir_a, dir_b):
    """
    查找目录A下的每个文件在目录B中是否存在（基于文件名和修改时间）

    Args:
        dir_a (str): 目录A的路径
        dir_b (str): 目录B的路径

    Returns:
        tuple: (匹配的文件列表, 未匹配的文件列表)
    """

    # 存储结果
    matching_files = []  # 在两个目录中文件名和修改时间都匹配的文件
    unmatched_files = []  # 只在目录A中存在的文件

    # 获取目录A中的所有文件信息
    dir_a_path = Path(dir_a)
    dir_b_path = Path(dir_b)

    # 收集目录A中的所有文件
    files_a = []
    for file_path in dir_a_path.rglob('*'):
        if file_path.is_file():
            files_a.append(get_file_info(file_path))

    # 收集目录B中的所有文件信息，按文件名分组
    files_b_dict = {}
    for file_path in dir_b_path.rglob('*'):
        if file_path.is_file():
            file_info = get_file_info(file_path)
            filename = file_info['name']
            if filename not in files_b_dict:
                files_b_dict[filename] = []
            files_b_dict[filename].append(file_info)

    # 比较目录A中的每个文件
    for file_a in files_a:
        filename = file_a['name']
        mtime_a = file_a['mtime']
        size_a = file_a['size']

        # 在目录B中查找同名文件
        if filename in files_b_dict:
            found_match = False
            for file_b in files_b_dict[filename]:
                # 检查修改时间和文件大小是否相同
                if abs(file_b['mtime'] - mtime_a) < 1 and file_b['size'] == size_a:
                    matching_files.append({
                        'name': filename,
                        'path_a': file_a['path'],
                        'path_b': file_b['path'],
                        'mtime': mtime_a,
                        'size': size_a
                    })
                    found_match = True
                    break

            if not found_match:
                unmatched_files.append({
                    'name': filename,
                    'path_a': file_a['path'],
                    'mtime': mtime_a,
                    'size': size_a
                })
        else:
            # 目录B中不存在同名文件
            unmatched_files.append({
                'name': filename,
                'path_a': file_a['path'],
                'mtime': mtime_a,
                'size': size_a
            })

    return matching_files, unmatched_files


def print_results_by_name_and_time(matching_files, unmatched_files):
    """
    打印基于文件名和修改时间的查找结果

    Args:
        matching_files (list): 匹配的文件列表
        unmatched_files (list): 未匹配的文件列表
    """
    print("=" * 70)
    print("文件对比结果（基于文件名和修改时间）")
    print("=" * 70)

    # 打印匹配的文件
    if matching_files:
        print(f"\n✓ 文件名和修改时间都匹配的文件 ({len(matching_files)} 个):")
        print("-" * 50)
        for item in matching_files:
            print(f"文件名: {item['name']}")
            print(f"  大小: {item['size']} 字节")
            print(f"  修改时间: {format_mtime(item['mtime'])}")
            print(f"  目录A路径: {item['path_a']}")
            print(f"  目录B路径: {item['path_b']}")
            print()
    else:
        print("\n✓ 没有文件名和修改时间都匹配的文件")

    # 打印未匹配的文件
    if unmatched_files:
        print(f"\n✗ 只在目录A中存在的文件 ({len(unmatched_files)} 个):")
        print("-" * 50)
        for item in unmatched_files:
            print(f"文件名: {item['name']}")
            print(f"  大小: {item['size']} 字节")
            print(f"  修改时间: {format_mtime(item['mtime'])}")
            print(f"  目录A路径: {item['path_a']}")
            print()
    else:
        print("\n✓ 所有目录A中的文件在目录B中都能找到匹配项")


def compare_directories_by_name_and_time(dir_a, dir_b):
    """
    比较两个目录中的文件（基于文件名和修改时间）

    Args:
        dir_a (str): 目录A路径
        dir_b (str): 目录B路径
    """
    matching_files, unmatched_files = find_files_by_name_and_time(dir_a, dir_b)
    print_results_by_name_and_time(matching_files, unmatched_files)
    return matching_files, unmatched_files


# 修改主函数以使用新的比较逻辑
def main():
    """
    主函数
    """
    # 获取用户输入的目录路径
    dir_a = input("请输入目录A的路径: ").strip()
    dir_b = input("请输入目录B的路径: ").strip()

    # 检查目录是否存在
    if not os.path.exists(dir_a):
        print(f"错误: 目录A '{dir_a}' 不存在")
        return

    if not os.path.exists(dir_b):
        print(f"错误: 目录B '{dir_b}' 不存在")
        return

    if not os.path.isdir(dir_a):
        print(f"错误: '{dir_a}' 不是一个目录")
        return

    if not os.path.isdir(dir_b):
        print(f"错误: '{dir_b}' 不是一个目录")
        return

    print(f"\n正在比较目录:")
    print(f"目录A: {os.path.abspath(dir_a)}")
    print(f"目录B: {os.path.abspath(dir_b)}")
    print(f"比较标准: 文件名和修改时间")

    # 查找文件
    try:
        matching_files, unmatched_files = compare_directories_by_name_and_time(dir_a, dir_b)
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    # compare_directories_by_name_and_time("J:/60-BAK/30-SOFT111", "G:/30-SOFT")
    main()
