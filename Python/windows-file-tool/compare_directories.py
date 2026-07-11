import os


def find_missing_folders(dir_a, dir_b):
    """
    查找目录A中的所有子文件夹在目录B中是否存在
    如果父目录不存在，则不列出其子目录

    Args:
        dir_a (str): 目录A的路径
        dir_b (str): 目录B的路径

    Returns:
        list: 在目录B中不存在的文件夹路径列表
    """
    missing_folders = []
    checked_paths = {}  # 缓存已检查的路径结果

    # 检查目录是否存在
    if not os.path.exists(dir_a):
        print(f"目录 {dir_a} 不存在")
        return missing_folders

    if not os.path.exists(dir_b):
        print(f"目录 {dir_b} 不存在")
        return missing_folders

    # 按层级顺序遍历目录A中的所有子文件夹
    for root, dirs, files in os.walk(dir_a):
        # 计算相对于dir_a的路径
        relative_root = os.path.relpath(root, dir_a)
        if relative_root == '.':
            relative_root = ''

        for dir_name in dirs:
            # 构造当前目录的相对路径
            if relative_root:
                relative_path = os.path.join(relative_root, dir_name)
            else:
                relative_path = dir_name

            # 构造在目录B中的对应路径
            target_path = os.path.join(dir_b, relative_path)

            # 检查父目录是否已知不存在
            parent_relative_path = os.path.dirname(relative_path)
            parent_exists_in_b = True

            if parent_relative_path and parent_relative_path != '.':
                parent_target_path = os.path.join(dir_b, parent_relative_path)
                # 检查父目录在B中是否存在
                parent_exists_in_b = os.path.exists(parent_target_path) and os.path.isdir(parent_target_path)

            # 只有当父目录存在时，才检查当前目录
            if parent_exists_in_b:
                current_path_in_a = os.path.join(dir_a, relative_path)
                exists_in_b = os.path.exists(target_path) and os.path.isdir(target_path)

                if not exists_in_b:
                    missing_folders.append(current_path_in_a)
            elif not parent_relative_path:  # 根目录下的直接子目录
                current_path_in_a = os.path.join(dir_a, relative_path)
                exists_in_b = os.path.exists(target_path) and os.path.isdir(target_path)

                if not exists_in_b:
                    missing_folders.append(current_path_in_a)

    return missing_folders


def find_missing_folders_optimized(dir_a, dir_b):
    """
    优化版本：按层级深度优先检查，避免报告父目录不存在时的子目录
    """
    missing_folders = []

    # 检查根目录是否存在
    if not os.path.exists(dir_a):
        print(f"目录 {dir_a} 不存在")
        return missing_folders

    if not os.path.exists(dir_b):
        print(f"目录 {dir_b} 不存在")
        return missing_folders

    # 收集所有目录并按深度排序
    all_dirs = []
    for root, dirs, files in os.walk(dir_a):
        for dir_name in dirs:
            full_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(full_path, dir_a)
            depth = relative_path.count(os.sep)  # 计算深度
            all_dirs.append((depth, full_path, relative_path))

    # 按深度排序，确保父目录先于子目录被处理
    all_dirs.sort(key=lambda x: x[0])

    missing_dirs_set = set()  # 记录已知缺失的目录

    for depth, full_path, relative_path in all_dirs:
        # 构造在目录B中的对应路径
        target_path = os.path.join(dir_b, relative_path)

        # 检查父目录是否缺失
        parent_dir = os.path.dirname(relative_path)
        parent_missing = False

        if parent_dir and parent_dir != '':
            parent_target_path = os.path.join(dir_b, parent_dir)
            # 如果父目录已知缺失，或者父目录在B中不存在
            if parent_dir in missing_dirs_set or not (
                    os.path.exists(parent_target_path) and os.path.isdir(parent_target_path)):
                parent_missing = True

        # 如果父目录缺失，则当前目录也视为缺失但不单独报告
        if parent_missing:
            relative_path_normalized = relative_path.replace(os.sep, '/')
            missing_dirs_set.add(relative_path_normalized)
            continue

        # 检查当前目录在B中是否存在
        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            missing_folders.append(full_path)
            relative_path_normalized = relative_path.replace(os.sep, '/')
            missing_dirs_set.add(relative_path_normalized)

    return missing_folders


def main():
    # 示例使用
    dir_a = input("请输入目录A的路径: ").strip()
    dir_b = input("请输入目录B的路径: ").strip()

    missing_folders = find_missing_folders_optimized(dir_a, dir_b)

    if missing_folders:
        print(f"\n在目录B中不存在的文件夹有 {len(missing_folders)} 个:")
        for folder in missing_folders:
            # 计算相对路径以便更清晰地显示
            relative_path = os.path.relpath(folder, dir_a)
            print(f"  {relative_path}")
    else:
        print("目录A中的所有子文件夹在目录B中都存在")


if __name__ == "__main__":
    # main()
    dir_a, dir_b = "D:\\__SYNC2\\git", "G:\\__SYNC2\\git"
    missing_folders = find_missing_folders(dir_a, dir_b)

    if missing_folders:
        print(f"\n在目录B中不存在的文件夹有 {len(missing_folders)} 个:")
        for folder in missing_folders:
            # 计算相对路径以便更清晰地显示
            relative_path = os.path.relpath(folder, dir_a)
            print(f"  {relative_path}")
    else:
        print("目录A中的所有子文件夹在目录B中都存在")
