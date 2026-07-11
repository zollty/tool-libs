#!/usr/bin/env python3

import subprocess
import os
from ai_code_review.git_utils import run_git_command, check_under_git_dir
from typing import List, Dict


# @Deprecated
def filter_git_changes(all_files: List[str], diff_type: int = 2):
    """
    @Deprecated
    有个麻烦问题是，通过git status或者git diff识别的新增或者删除类型的文件，它不一定真的是新增或者删除，有可能是重命名的文件
    所以对于状态为“A ”或者“D ”或者“ D”（格式为“XY”，XY可以为空）的变更文件，它有可能是重命名，不能单纯根据状态“R ”来判断。
    而且重命名后的文件可能状态为“??”（未跟踪）所以即便是使用git diff都无法识别（只有git add该文件后git diff才能识别）

    所以本方法就是专门解决这个问题的。
    """
    try:
        # 获取git状态信息
        cmd = ['git', 'status', '--porcelain']
        result = run_git_command(cmd)
        lines = result.split('\n')

        final_files = []

        for line in lines:
            if not line.strip():
                continue

            # git status --porcelain 格式:
            # XY filename
            # X: 暂存区状态, Y: 工作区状态
            status = line[:2]
            filename = line[3:].strip()

            if status[0] == 'R':
                if status[1] == ' ':  # 跳过重命名文件
                    continue
                elif status[1] == 'M':
                    final_files.append(filename)

            elif status[0] == 'A':  # 新增文件，看是不是通过重命名而来
                rename_file = False
                for git_file in all_files:
                    # 如果有被重命名的文件与它相同，说明该文件是由git_file.file1重命名而来
                    if git_file.file2 == filename:
                        rename_file = True
                        break
                if rename_file:
                    continue
                final_files.append(filename)

            elif status[0] == 'D':  # 删除文件， 看是不是此文件已经重命名为别的文件了
                rename_file = False
                for git_file in all_files:
                    # 如果有旧文件与它相同，说明该文件不是被删除，而是重命名为了git_file.file2
                    if git_file.file2 and git_file.file1 == filename:
                        rename_file = True
                        break
                if rename_file:
                    continue
                final_files.append(filename)

            elif status[0] in ['M', 'D']:  # 新增和删除的文件
                final_files.append(filename)

            elif status[0] == ' ':  # 未暂存的文件，只剩下状态为" D"和" M"的
                if status[1] == 'M':
                    final_files.append(filename)
                elif status[1] == 'D': # 对删除文件要判断是否为重命名文件
                    rename_file = False
                    for git_file in all_files:
                        # 如果有旧文件与它相同，说明该文件不是被删除，而是重命名为了git_file.file2
                        if git_file.file2 and git_file.file1 == filename:
                            rename_file = True
                            break
                    if rename_file:
                        continue
                    final_files.append(filename)


            if diff_type == 1:
                # 已暂存的文件 (绿色)
                if status[0] in ['A', 'M', 'D', 'R']:
                    if status[0] == 'R':
                        filename = filename.split(' -> ')[1]
                    if status[0] == 'A': # 新增，查找unstaged区是否有删除文件与之相同，为方便起见，反向从已删除的文件中去查找
                        final_files.append(filename)
                    if status[0] == 'D': # 删除，查找cached或untracked区是否有新增文件与之相同
                        final_files.append(filename)

                    final_files.append(filename)

    except subprocess.CalledProcessError as e:
        print(f"执行git命令时出错: {e}")


def get_git_file_status(split_rename: bool = False):
    """
    使用git命令获取文件状态并返回已暂存和未暂存文件列表
    返回: (staged_files, unstaged_files, untracked_files)
    注意，该方法可能与‘git diff xxx’的结果不一致，当本地重命名文件后，可能会识别为删除了该文件又新增了一个文件，而不是重命名。
    如果想要和‘git diff xxx’结果一致，则推荐使用get_git_files_advanced函数
    """

    staged_files = []  # 已暂存文件
    unstaged_files = []  # 未暂存文件（已修改但未暂存）
    untracked_files = []  # 未追踪文件

    try:
        # 获取git状态信息
        cmd = ['git', 'status', '--porcelain']
        result = run_git_command(cmd)
        lines = result.split('\n')

        for line in lines:
            if not line.strip():
                continue

            # git status --porcelain 格式:
            # XY filename
            # X: 暂存区状态, Y: 工作区状态
            status = line[:2]
            filename = line[3:].strip()

            # 已暂存的文件 (绿色)
            # 状态包括: A(新增), M(修改), D(删除) 在暂存区
            if status[0] in ['A', 'M', 'D', 'R']:
                if split_rename and status[0] == 'R':
                    filename = filename.split(' -> ')[1]
                staged_files.append(filename)

            # 未暂存的文件 (红色)
            # 状态包括: 工作区有修改但未暂存
            if status[1] in ['M', 'D']:
                unstaged_files.append(filename)

            if status == '??':
                untracked_files.append(filename)

    except subprocess.CalledProcessError as e:
        print(f"执行git命令时出错: {e}")

    return staged_files, unstaged_files, untracked_files


def print_colored_files(method, staged_files, unstaged_files, untracked_files=[]):
    """
    使用颜色打印文件列表
    """
    print(f"\n{'=' * 50}")
    print(f"Git文件状态 (方法: {method})")
    print(f"{'=' * 50}")

    print(f"\n数组内容:")
    print(f"staged_files: {staged_files}")
    print(f"unstaged_files: {unstaged_files}")
    print(f"untracked_files: {untracked_files}")

    # ANSI颜色代码
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'

    print(f"\n{GREEN}📁 已暂存文件 ({len(staged_files)}个) :{RESET}")
    if staged_files:
        for i, file in enumerate(staged_files, 1):
            print(f"  {i}. {file}")
    else:
        print("  暂无已暂存文件")

    print(f"\n{RED}📝 未暂存文件 ({len(unstaged_files)}个) :{RESET}")
    if unstaged_files:
        for i, file in enumerate(unstaged_files, 1):
            print(f"  {i}. {file}")
    else:
        print("  暂无未暂存文件")

    print(f"\n{YELLOW}❓ 未追踪文件 ({len(untracked_files)}个) :{RESET}")
    if untracked_files:
        for i, file in enumerate(untracked_files, 1):
            print(f"  {i}. {file}")
    else:
        print("  暂无未跟踪文件")


# 更精确的版本，使用git diff命令
def get_git_files_advanced():
    """
    使用更详细的git命令分别获取不同类型的文件
    """
    staged_files = []
    unstaged_files = []
    untracked_files = []
    try:
        # 获取已暂存文件 (staged)
        cmd = ['git', 'diff', '--name-only', '--cached']
        result = run_git_command(cmd)
        if result.strip():
            staged_files = result.strip().split('\n')

        # 获取未暂存文件 (unstaged)
        cmd = ['git', 'diff', '--name-only']
        result = run_git_command(cmd)
        if result.strip():
            unstaged_files = result.strip().split('\n')

        # 获取未追踪文件 (git ls-files --others --exclude-standard)
        cmd = ['git', 'ls-files', '--others', '--exclude-standard']
        result = run_git_command(cmd)
        if result.strip():
            untracked_files = [f.strip() for f in result.split('\n') if f.strip()]

    except subprocess.CalledProcessError as e:
        print(f"执行git命令时出错: {e}")

    return staged_files, unstaged_files, untracked_files


def test():
    """
    测试函数
    """
    print("Git文件状态检测程序")
    print("正在分析当前git仓库...")

    # 方法1: 使用git status --porcelain
    staged1, unstaged1, untracked1 = get_git_file_status()
    print_colored_files("git status --porcelain", staged1, unstaged1, untracked1)

    # 方法2: 使用多个git命令分别获取
    staged2, unstaged2, untracked2 = get_git_files_advanced()
    print_colored_files("多个git命令", staged2, unstaged2, untracked2)

    # 比较两种方法的结果
    print(f"\n{'=' * 50}")
    print("结果比较:")
    print(f"{'=' * 50}")
    print(f"方法1 - 暂存: {len(staged1)}, 未暂存: {len(unstaged1)}, 未追踪: {len(untracked1)}")
    print(f"方法2 - 暂存: {len(staged2)}, 未暂存: {len(unstaged2)}, 未追踪: {len(untracked2)}")


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    os.chdir(git_repo_path)
    check_under_git_dir()

    test()
