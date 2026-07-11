import os
from typing import List, Dict, Set
from pathlib import Path


def find_folders_recursive(search_paths: List[str], target_folders: List[str],
                           recursive: bool = False, max_depth: int = None) -> Dict[str, List[Dict]]:
    """
    在指定目录下查找特定文件夹名称（支持递归搜索）

    Args:
        search_paths: 要搜索的目录路径列表
        target_folders: 要查找的目标文件夹名称列表
        recursive: 是否递归搜索子目录
        max_depth: 最大搜索深度（None表示无限制）

    Returns:
        字典，键为搜索路径，值为找到的文件夹信息列表
    """
    results = {}
    target_set = set(target_folders)  # 使用集合提高查找效率

    for path in search_paths:
        if not os.path.exists(path):
            print(f"警告: 路径 {path} 不存在")
            results[path] = []
            continue

        if not os.path.isdir(path):
            print(f"警告: {path} 不是一个目录")
            results[path] = []
            continue

        try:
            found_folders = []
            if recursive:
                found_folders = _search_recursive(path, target_set, max_depth)
            else:
                found_folders = _search_single_level(path, target_set)

            results[path] = found_folders
        except PermissionError:
            print(f"错误: 没有权限访问 {path}")
            results[path] = []
        except Exception as e:
            print(f"错误: 访问 {path} 时发生异常: {e}")
            results[path] = []

    return results


def _search_single_level(directory: str, target_folders: Set[str]) -> List[Dict]:
    """在单层目录中搜索"""
    found = []
    try:
        items = os.listdir(directory)
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and item in target_folders:
                found.append({
                    'name': item,
                    'path': item_path,
                    'depth': 0
                })
    except Exception:
        pass
    return found


def _search_recursive(directory: str, target_folders: Set[str], max_depth: int = None,
                      current_depth: int = 0) -> List[Dict]:
    """递归搜索目录 - 优化版本：找到匹配目录后不再深入搜索其子目录"""
    found = []

    # 检查深度限制
    if max_depth is not None and current_depth > max_depth:
        return found

    try:
        items = os.listdir(directory)
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                # 检查是否为目标文件夹
                if item in target_folders:
                    found.append({
                        'name': item,
                        'path': item_path,
                        'depth': current_depth
                    })
                    # 找到匹配的目录后，不再递归搜索该目录的子目录
                    continue

                # 只有当目录不是目标目录时，才继续递归搜索
                if max_depth is None or current_depth < max_depth:
                    found.extend(_search_recursive(item_path, target_folders, max_depth, current_depth + 1))
    except Exception:
        pass

    return found


def print_results(results: Dict[str, List[Dict]], show_details: bool = True):
    """打印搜索结果"""
    print("文件夹查找结果:")
    print("=" * 60)

    for directory, found_folders in results.items():
        print(f"\n搜索目录: {directory}")
        if found_folders:
            print(f"  找到 {len(found_folders)} 个目标文件夹:")
            for folder_info in found_folders:
                if show_details and 'depth' in folder_info:
                    print(f"    - {folder_info['name']} (路径: {folder_info['path']}, 深度: {folder_info['depth']})")
                else:
                    print(f"    - {folder_info['name']} (路径: {folder_info['path']})")
        else:
            print("  未找到目标文件夹")


# 使用示例
if __name__ == "__main__":
    # 定义要搜索的目录
    search_directories = [
        "G:\\__SYNC2\\git",
        "G:\\__SYNC2\\git-bak",
        "G:\\__SYNC2\\git111",
        "G:\\__SYNC2\\git-tmp"
    ]

    dirs = """backup
  clariway
  eigen
  faster-whisper-server
  IdeaProjects
  pytest
  QsmyServer
  ragflow
  sglang
  speech-to-text
    """

    # 定义要查找的文件夹名称
    target_folder_names = [dir_name.strip() for dir_name in dirs.split('\n') if dir_name.strip()]

    # 执行非递归搜索
    # print("=== 非递归搜索 ===")
    # results_simple = find_folders_recursive(search_directories, target_folder_names, recursive=False)
    # print_results(results_simple)

    # 执行递归搜索
    max_depth = 10
    print(f"\n\n=== 递归搜索（最大深度{max_depth}） ===")
    results_recursive = find_folders_recursive(search_directories, target_folder_names,
                                               recursive=True, max_depth=max_depth)
    print_results(results_recursive)
