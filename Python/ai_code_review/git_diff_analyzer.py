#!/usr/bin/env python3
"""
智能 Git Diff 分析工具
保留重要上下文，过滤无用元数据，优化 AI 分析
"""

import subprocess
import os
import re
import math
from typing import List, Dict
from ai_code_review.git_utils import (run_git_command, check_under_git_dir, is_code_file, is_text_file,
                                      git_diff_with_local_file, get_file_status, STATUS_DICT)
from ai_code_review.git_file_similarity import find_renamed_files


def get_file_content(file_path: str, max_lines: int = 200) -> str:
    """获取文件内容，限制最大行数"""
    try:
        splited = False
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    if not splited:
                        lines.append(f"... (文件超过{max_lines}行，已截断，下面是注释信息)")
                        splited = True
                    elif line.lstrip().startswith('#') or line.lstrip().startswith('//'):
                        lines.append(line.rstrip())
                else:
                    lines.append(line.rstrip())
            return '\n'.join(lines)
    except Exception as e:
        print(f"无法读取文件: {e}")
        return ""


def get_old_file_content(git_file_path: str, max_lines: int = 200) -> str:
    """获取删除文件的旧内容（从 Git 历史中）"""
    try:
        splited = False
        # 使用 git show 获取文件在最后一次提交中的内容
        stdout = run_git_command(['git', 'show', f'HEAD:{git_file_path}'])
        flines = stdout.split('\n')
        # 限制行数
        lines = []
        for i, line in enumerate(flines):
            if i >= max_lines:
                if not splited:
                    lines.append(f"... (文件超过{max_lines}行，已截断，下面是注释信息)")
                    splited = True
                elif line.lstrip().startswith('#') or line.lstrip().startswith('//'):
                    lines.append(line.rstrip())
            else:
                lines.append(line.rstrip())

        return '\n'.join(lines)
    except subprocess.CalledProcessError:
        print(f"无法从 Git 历史中获取文件内容: {git_file_path}")
        return ""
    except Exception as e:
        print(f"错误: {e}")
        return ""


class GitFileChange:
    """表示一个文件的变更信息"""

    def __init__(self, status: str, similarity: int, file1: str, source1: str, file2: str = "", source2: str = "", context: str = ""):
        self.status = status
        self.similarity = similarity
        self.file1 = file1
        self.file2 = file2
        self.source1 = source1
        self.source2 = source2
        self.context = context
        self.total_lines = -1
        self.per_line_length = -1
        self.content_summarized = False

    def set_lines(self, context: str = None):
        use_context = context if context else self.context
        if use_context:
            self.total_lines = len(use_context.split('\n'))
            self.per_line_length = int(len(use_context) / self.total_lines)

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "status": self.status,
            "similarity": self.similarity,
            "file1": self.file1,
            "file2": self.file2,
            "source1": self.source1,
            "source2": self.source2,
            "context": self.context,
            "content_summarized": self.content_summarized
        }


def find_file_source(files_status: List[str], file_path1: str, file_path2) -> List[str]:
    result = []
    for line in files_status:
        if line.find(file_path1) != -1:
            # git status --porcelain 格式:
            # XY filename
            # X: 暂存区状态, Y: 工作区状态
            status = line[:2]
            # filename = line[3:].strip()
            if status[0] in ['A', 'M', 'D', 'R']:
                result.append("cached")
            elif status[0] == ' ':
                result.append("not_staged")
            break
    if file_path2:
        for line in files_status:
            if line.find(file_path2) != -1:
                # git status --porcelain 格式:
                # XY filename
                # X: 暂存区状态, Y: 工作区状态
                status = line[:2]
                # filename = line[3:].strip()
                if status[0] in ['A', 'M', 'D', 'R']:
                    result.append("cached")
                elif status[0] == ' ':
                    result.append("not_staged")
                elif status[0] == '?':
                    result.append("untracked")
                break
    else:
        result.append("")
    return result


def parse_git_diff_output(diff_output: str) -> List[GitFileChange]:
    """解析git diff输出并返回文件变更对象数组"""
    untracked_changes = get_untracked_files()
    changes = []+untracked_changes

    # 按文件分割diff输出
    file_diffs = re.split(r'^diff --git ', diff_output.strip(), flags=re.MULTILINE)
    all_file_status = get_file_status()

    for file_diff in file_diffs:
        if not file_diff.strip():
            continue

        lines = file_diff.split('\n')
        if not lines:
            continue

        # 解析文件路径
        file_line = lines[0]
        file_match = re.match(r'^a/(.+) b/(.+)$', file_line)
        if not file_match:
            continue

        file1 = file_match.group(1)
        file2 = file_match.group(2)

        # 初始化变量
        status = "M"  # 默认为修改
        similarity = 0
        context_lines = []

        i = 1
        while i < len(lines):
            line = lines[i]

            # 检查重命名和相似度
            if line.startswith('similarity index'):
                similarity_match = re.search(r'(\d+)%', line)
                if similarity_match:
                    similarity = int(similarity_match.group(1))

                # 检查是否是重命名
                has_rename_from = False
                has_rename_to = False
                for j in range(i + 1, min(i + 3, len(lines))):
                    if lines[j].startswith('rename from'):
                        has_rename_from = True
                    elif lines[j].startswith('rename to'):
                        has_rename_to = True

                if has_rename_from and has_rename_to:
                    status = "R" if similarity == 100 else "RM"
                    # 跳过重命名相关的行
                    i += 3  # similarity + rename from + rename to
                    continue

            # 检查文件删除
            elif line.startswith('deleted file mode'):
                # 特别处理，此处的删除文件，不一定是真的删除了，有可能是在本地重命名了，但是重命名后的文件没有add导致git diff不识别
                # 所以，我们需要与本地untracked_files进行对比，排除重命名的可能性
                untracked_files = [untracked_file.file1 for untracked_file in untracked_changes]
                result = find_renamed_files(file1, untracked_files)
                if result is None:
                    status = "D"
                    # 对于删除的文件，file2应该是空
                    file2 = ""
                else:
                    # 对于删除的文件，file2应该是空
                    file2 = result['untracked_file']  # + " (untracked_files)"
                    similarity = result['similarity']
                    if similarity == 100:
                        status = "R"
                    else:
                        status = "RM"
                        diff_txt = git_diff_with_local_file(file1, file2)
                        if diff_txt is None:
                            print(f"Error: {file1} -> {file2}  similarity={similarity} but diff wrong!")
                        elif diff_txt != "":
                            context_lines = [diff_txt]

            # 检查文件新增
            elif line.startswith('new file mode'):
                status = "A"
                # 对于新增的文件，file1应该是空，但git diff中file1是/dev/null
                # 我们调整一下，让file1为空
                if file1 == '/dev/null':
                    file1 = ""

            # 检查index行（文件内容变更）
            elif line.startswith('index '):
                # 如果之前没有设置状态，且不是重命名，那么就是修改
                if status == "M" and similarity == 0:
                    # 检查是否真的是修改（有---和+++行）
                    has_minus = False
                    has_plus = False
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if lines[j].startswith('--- '):
                            has_minus = True
                        elif lines[j].startswith('+++ '):
                            has_plus = True

                    if has_minus and has_plus:
                        status = "M"

            # 收集差异内容（从---开始）
            elif line.startswith('--- '):
                # 开始收集差异内容
                context_lines = lines[i+2:]
                break

            i += 1

        # 构建上下文（对于M或RM状态）
        context = ""
        if status in ['M', 'RM'] and context_lines:
            context = '\n'.join(context_lines)

        file2 = file2 if status in ['R', 'RM'] else ""
        source = find_file_source(all_file_status, file1, file2)
        # 创建变更对象
        change = GitFileChange(
            status=status,
            similarity=similarity,
            file1=file1,
            file2=file2,
            source1=source[0],
            source2=source[1],
            context=context
        )
        change.set_lines()
        changes.append(change)

    return changes


def get_untracked_files() -> List[GitFileChange]:
    """获取未跟踪的文件"""
    untracked_changes = []
    cmd = ["git", "ls-files", "--others", "--exclude-standard"]
    result = run_git_command(cmd)
    for file_path in result.strip().split('\n'):
        if file_path.strip():
            change = GitFileChange(
                status="??",
                similarity=0,
                file1=file_path.strip(),
                file2="",
                source1="untracked",
                source2="",
                context=""
            )
            untracked_changes.append(change)

    return untracked_changes


def get_all_git_changes() -> List[GitFileChange]:
    """处理git变更并返回文件变更对象数组"""

    # 获取git diff输出
    cmd = ["git", "diff", "--find-renames", "HEAD", "-M"]
    diff_output = run_git_command(cmd)
    # 解析diff输出
    return parse_git_diff_output(diff_output)


def filter_git_changes_by_diff_type(diff_type: int = 2) -> List[GitFileChange]:
    """
    根据diff_type过滤变更文件
    有个麻烦问题是，通过git status或者git diff识别的新增或者删除类型的文件，它不一定真的是新增或者删除，有可能是重命名的文件
    所以对于状态为“A ”或者“D ”或者“ D”（格式为“XY”，XY可以为空）的变更文件，它有可能是重命名，不能单纯根据状态“R ”来判断。
    而且重命名后的文件可能状态为“??”（未跟踪）所以即便是使用git diff都无法识别（只有git add该文件后git diff才能识别）

    所以本方法就是专门解决这个问题的。
    """
    all_changes = get_all_git_changes()
    file_changes = []
    for change in all_changes:
        if change.status == 'R':  # 过滤掉重命名的
            continue

        if diff_type >= 3:  # 所有文件（包括新增未跟踪的文件）
            file_changes.append(change)
        elif diff_type == 2:  # 所有已跟踪文件（包括已暂存文件和未暂存文件）
            if change.source1 != 'untracked':
                file_changes.append(change)
        elif diff_type == 1:  # 已暂存文件（已add的）
            if "cached" in [change.source1, change.source2]:
                file_changes.append(change)
        elif diff_type <= 0:  # not staged文件（未add的）
            if change.source1 == 'not_staged':
                file_changes.append(change)
    return file_changes


def set_context_if_need(file_changes: List[GitFileChange], max_lines: int = 200,
                        ignore_not_code_content: bool = True) -> List[GitFileChange]:
    """
    :param file_changes:变更文件清单
    """
    new_changes = []
    for i, change in enumerate(file_changes, 1):
        # 首先设置 新增、删除文件内容。
        if change.status == 'A' and not change.context:  # 新增
            if is_text_file(change.file1):
                change.context = get_file_content(change.file1, max_lines)
                change.set_lines(change.context)
            else:
                change.context = ""

        elif change.status == 'D' and not change.context:  # 删除
            change.context = get_old_file_content(change.file1, max_lines)
            change.set_lines(change.context)

        if ignore_not_code_content and not is_code_file(change.file1):
            # 非代码文件，去掉context内容
            if change.status == 'M':
                if change.context:
                    print(f"{change.file1} is not code file, ignore it's diff context!")
                    change.context = ""
            elif change.context: # 去掉原本有的context内容
                change.context = ""

        new_changes.append(change)
    return new_changes


def ignore_not_code_file_content(file_changes: List[GitFileChange]) -> List[GitFileChange]:
    all_changes = get_all_git_changes()
    file_changes = []
    for change in all_changes:
        if not is_code_file(change.file1):
            if change.status == 'M':
                if change.context:
                    print(f"{change.file1} is not code file, ignore it's diff context!")
                    change.context = "<略>"
            else:
                change.context = "<略>"

        file_changes.append(change)
    return file_changes


def print_single_file_changes(change: GitFileChange, i: int = 0, context: str = None):
    print(f"{i}. 文件: {change.file1} ({change.source1})")
    print(f"   状态: {change.status}-{STATUS_DICT[change.status]}")
    if change.similarity > 0:
        print(f"   相似度: {change.similarity}%")
    if change.file2:
        print(f"   重命名为: {change.file2} ({change.source2})")
    if change.total_lines > 0:
        print(f"   内容行数: {change.total_lines}行")
        print(f"   每行均长: {change.per_line_length}字符")
    use_context = context if context else change.context
    if use_context:
        if change.status == 'M':
            print(f"   变更内容（前500字符）: \n{use_context[:500]}")
        else:
            print(f"   文件内容（前500字符）: \n{use_context[:500]}")
    print()


def build_chat_context(file_changes: List[GitFileChange]):
    result = []
    for change in file_changes:
        result.append(f"## 文件: {change.file1}")
        result.append(f"   状态: {change.status}-{STATUS_DICT[change.status]}")
        if change.context:
            if change.status == 'M':
                if change.content_summarized:
                    result.append(f"   文件改动点描述: \n{change.context}")
                else:
                    result.append(f"   文件变更信息: \n{change.context}")
            else:
                if change.content_summarized:
                    result.append(f"   文件内容总结: \n{change.context}")
                else:
                    result.append(f"   文件内容: \n{change.context}")

        result.append("\n\n\n")

    return "\n".join(result)

def print_git_changes(file_changes: List[GitFileChange]):
    if not file_changes:
        print("没有检测到文件变更")
        return []

    # 输出结果
    print(f"\n检测到 {len(file_changes)} 个文件变更:")
    print("-" * 80)

    for i, change in enumerate(file_changes, 1):
        print_single_file_changes(change, i)


def test():
    print("正在分析Git变更...")
    file_changes = get_all_git_changes()
    print_git_changes(file_changes)


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    os.chdir(git_repo_path)
    check_under_git_dir()

    test()
