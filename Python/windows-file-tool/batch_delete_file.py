import os


def batch_delete_files(file_list_text):
    """
    批量删除文件

    Args:
        file_list_text (str): 包含文件路径的多行文本字符串
    """
    # 按行分割文本并去除每行前后的空格
    file_paths = [line.strip() for line in file_list_text.splitlines() if line.strip()]

    deleted_files = []
    failed_files = []

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"已删除: {file_path}")
            else:
                failed_files.append((file_path, "文件不存在"))
                print(f"文件不存在: {file_path}")
        except Exception as e:
            failed_files.append((file_path, str(e)))
            print(f"删除失败 {file_path}: {e}")

    # 输出统计信息
    print(f"\n总计: {len(file_paths)} 个文件")
    print(f"成功删除: {len(deleted_files)} 个文件")
    if failed_files:
        print(f"删除失败: {len(failed_files)} 个文件")

    return deleted_files, failed_files

def batch_delete_files_from_file(file_path):
    """
    从指定文件中读取文件路径列表并批量删除文件

    Args:
        file_path (str): 包含文件路径列表的文件路径
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_list_text = f.read()
        return batch_delete_files(file_list_text)
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return [], []
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return [], []

# 使用示例
if __name__ == "__main__":
    # 从指定文件读取文件路径列表
    file_list_path = "../local/file_list.txt"  # 指定包含文件路径的文件

    # 执行批量删除
    batch_delete_files_from_file(file_list_path)
