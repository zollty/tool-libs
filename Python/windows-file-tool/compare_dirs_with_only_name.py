import os
from pathlib import Path


def compare_directories(dir1, dir2):
    """
    对比两个目录的差异，以dir1为标准

    Args:
        dir1: 左侧目录路径
        dir2: 右侧目录路径
    """

    def get_dir_structure(directory):
        """获取目录结构"""
        structure = {}
        path = Path(directory)
        if not path.exists():
            return structure

        for item in path.rglob('*'):
            relative_path = item.relative_to(path)
            parts = relative_path.parts
            current = structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            if item.is_dir():
                current[parts[-1]] = {}
            else:
                current[parts[-1]] = None  # 文件用None表示
        return structure

    def compare_structures(struct1, struct2, path=""):
        """
        递归对比两个目录结构

        Returns:
            tuple: (added_items, removed_items)
        """
        added = []
        removed = []

        # 检查struct1中有的但struct2中没有的（减少的）
        for key in struct1:
            current_path = f"{path}/{key}" if path else key
            if key not in struct2:
                removed.append(current_path)
            else:
                # 递归比较子目录
                if isinstance(struct1[key], dict) or isinstance(struct2[key], dict):
                    sub_added, sub_removed = compare_structures(
                        struct1[key] if isinstance(struct1[key], dict) else {},
                        struct2[key] if isinstance(struct2[key], dict) else {},
                        current_path
                    )
                    added.extend(sub_added)
                    removed.extend(sub_removed)

        # 检查struct2中有的但struct1中没有的（增加的）
        for key in struct2:
            current_path = f"{path}/{key}" if path else key
            if key not in struct1:
                added.append(current_path)
            # 注意：如果两个都是文件或两个都是目录，我们不递归比较

        return added, removed

    # 获取两个目录的结构
    structure1 = get_dir_structure(dir1)
    structure2 = get_dir_structure(dir2)

    # 对比结构
    added, removed = compare_structures(structure1, structure2)

    return added, removed


def print_tree_diff(dir1, dir2):
    """
    以树形结构打印目录差异

    Args:
        dir1: 左侧目录路径
        dir2: 右侧目录路径
    """
    added, removed = compare_directories(dir1, dir2)

    print(f"目录对比: {dir1} (标准) vs {dir2}")
    print("=" * 50)

    if not added and not removed:
        print("两个目录结构完全相同")
        return

    # 打印减少的项目（在dir1中存在但在dir2中不存在）
    if removed:
        print("减少的文件/文件夹 (在左侧目录中存在，右侧目录中不存在):")
        for item in sorted(removed):
            print(f"  - {item}")
        print()

    # 打印增加的项目（在dir2中存在但在dir1中不存在）
    if added:
        print("增加的文件/文件夹 (在右侧目录中存在，左侧目录中不存在):")
        for item in sorted(added):
            print(f"  + {item}")
        print()


# 使用示例
if __name__ == "__main__":
    # 可以直接调用函数进行比较
    left_directory = "G:\\__SYNC1\\Softwares\\Android\\Sdk"
    right_directory = "D:\\__SYNC0\\soft-portable-big\\AndroidStudioSdk"

    print_tree_diff(left_directory, right_directory)

