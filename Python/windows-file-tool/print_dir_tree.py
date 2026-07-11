import os
from pathlib import Path
import fnmatch


def print_filtered_tree(path, prefix="", is_last=True,
                        ignore_patterns=None, max_depth=None, current_depth=0,
                        folders_only=False):
    """
    可过滤的目录树打印，支持模糊匹配和仅显示文件夹选项

    Args:
        path: 目录路径
        prefix: 前缀字符串
        is_last: 是否为最后一个节点
        ignore_patterns: 忽略的模式列表（支持模糊匹配，如 ['*.pyc', 'test_*']）
        max_depth: 最大深度
        current_depth: 当前深度
        folders_only: 是否只显示文件夹
    """
    if ignore_patterns is None:
        ignore_patterns = []

    path = Path(path)
    name = path.name if path.name else str(path)

    # 检查是否应该忽略
    should_ignore = False
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(name, pattern) or (path.is_file() and fnmatch.fnmatch(path.name, pattern)):
            should_ignore = True
            break

    if should_ignore:
        return

    # 如果只显示文件夹且当前路径是文件，则忽略
    if folders_only and path.is_file():
        return

    # 检查深度限制
    if max_depth is not None and current_depth > max_depth:
        return

    # 打印当前节点
    if prefix:
        connector = "└── " if is_last else "├── "
        print(prefix + connector + name)
    else:
        print(name)

    # 递归处理子目录
    if path.is_dir() and (max_depth is None or current_depth < max_depth):
        try:
            items = list(path.iterdir())
            # 排序：目录在前，文件在后，同类型按名称排序
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))

            # 过滤项目
            filtered_items = []
            for item in items:
                # 如果只显示文件夹，跳过文件
                if folders_only and item.is_file():
                    continue

                # 检查是否匹配忽略模式
                should_ignore_item = False
                for pattern in ignore_patterns:
                    if fnmatch.fnmatch(item.name, pattern):
                        should_ignore_item = True
                        break

                if not should_ignore_item:
                    filtered_items.append(item)

            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension

            for i, item in enumerate(filtered_items):
                is_last_item = (i == len(filtered_items) - 1)
                print_filtered_tree(
                    item, new_prefix, is_last_item,
                    ignore_patterns, max_depth, current_depth + 1,
                    folders_only
                )
        except PermissionError:
            extension = "    " if is_last else "│   "
            new_prefix = prefix + extension
            print(new_prefix + "├── [权限不足]")

# 使用示例
if __name__ == "__main__":
    print("过滤版本的目录树 (忽略 .git 和 __pycache__):")
    print_filtered_tree(
        "D:/__SYNC2/git-dms/dms-web-next/tests",
        folders_only=True,
        ignore_patterns=['P*', 'utils', 'fixtures', 'W*'],
        max_depth=5
    )
