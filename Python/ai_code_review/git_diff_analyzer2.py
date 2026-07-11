#!/usr/bin/env python3
"""
智能 Git Diff 分析工具
保留重要上下文，过滤无用元数据，优化 AI 分析
"""

import subprocess
import os
import sys
from typing import List, Tuple, Optional
from ai_code_review.ai_chat import general_chat

def run_git_command(cmd: List[str]) -> str:
    """运行 git 命令并返回输出"""
    try:
        # 显式指定编码为 utf-8，并添加错误处理
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='ignore'  # 或使用 'replace' 来替换无法解码的字符
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"错误执行命令 {' '.join(cmd)}: {e}")
        return ""


def get_file_type(file_path: str) -> str:
    """获取文件基本信息"""
    if not os.path.exists(file_path):
        return "文件不存在"
    # 尝试获取文件类型
    # try:
    #     import magic
    #     file_type = magic.from_file(file_path)
    # except (ImportError, Exception):
    # 回退方案：根据扩展名判断
    ext = os.path.splitext(file_path)[1].lower()
    file_types = {
        '.java': 'Java source',
        '.py': 'Python source',
        '.js': 'JavaScript source',
        '.ts': 'TypeScript source',
        '.cjs': 'JavaScript source',
        '.vue': 'VUE source',
        '.cpp': 'C++ source',
        '.c': 'C source',
        '.h': 'C header',
        '.html': 'HTML',
        '.css': 'CSS',
        '.md': 'Markdown',
        '.json': 'JSON',
        '.xml': 'XML',
        '.bat': 'Windows BAT',
        '.sh': 'Linux SHELL'
    }
    file_type = file_types.get(ext, 'source code')

    return file_type
    #
    # else:
    #     return f"unknown file type"


def get_file_lines(file_path: str) -> str:
    try:
        # 获取文件行数
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            line_count = sum(1 for _ in f)

        return line_count
    except Exception as e:
        print(f"无法获取文件行数: {e}")
        return -1


def filter_diff_lines(diff_output: str) -> str:
    """
    过滤 diff 输出，保留重要信息：
    - 保留 hunk headers (@@ ... @@)
    - 保留代码上下文（空格开头的行）
    - 保留实际变更（+/- 开头的行）
    - 删除纯元数据行
    """
    filtered_lines = []

    for line in diff_output.split('\n'):
        # 保留 hunk headers
        if line.startswith('@@'):
            filtered_lines.append(line)
        # 保留代码上下文和实际变更
        elif (line.startswith(' ') or
              line.startswith('+') or
              line.startswith('-')):
            # 过滤掉纯元数据行
            if not (line.startswith('+++') or
                    line.startswith('---') or
                    line.startswith('index')):
                filtered_lines.append(line)

    return '\n'.join(filtered_lines)


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


def get_old_file_content(file_path: str, max_lines: int = 200) -> str:
    """获取删除文件的旧内容（从 Git 历史中）"""
    try:
        splited = False
        # 使用 git show 获取文件在最后一次提交中的内容
        stdout = run_git_command(['git', 'show', f'HEAD:{file_path}'])
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
        print(f"无法从 Git 历史中获取文件内容: {file_path}")
        return ""
    except Exception as e:
        print(f"错误: {e}")
        return ""


def process_file_diff(file_path: str, status: str) -> str:
    """处理单个文件的 diff 输出"""
    output = []

    if status == 'A':
        output.append(f"🆕 新增文件: {file_path}")
        file_type = get_file_type(file_path)
        file_line = ''
        if file_type:
            file_line += str(get_file_lines(file_path))
        output.append(f"   文件信息: type:{file_type} len:{file_line}")
        output.append("   文件内容总结:")
        # 获取新增文件的完整内容
        # content = get_file_content(file_path)
        # result = general_chat(config.code_file_summary_prompt, f"🆕 新增文件: {file_path} 文件内容如下:\n{content}")
        # output.append(result)

    elif status == 'D':
        output.append(f"❌ 删除文件: {file_path}")
        output.append("   原文件内容总结:")
        # 使用 git show 获取文件在最后一次提交中的内容
        # content = get_old_file_content(file_path)
        # result = general_chat(config.code_file_summary_prompt, f"❌ 删除文件: {file_path} 原文件内容如下:\n{content}")
        # output.append(result)

    elif status in ['M', 'R']:
        if status == 'R':
            output.append(f"🔄 重命名文件: {file_path}")
        else:
            output.append(f"📝 修改文件: {file_path}")

        # 获取文件的 diff
        diff_output = run_git_command(['git', 'diff', 'HEAD', '--no-color', '--', file_path])
        if diff_output:
            filtered_diff = filter_diff_lines(diff_output)
            if filtered_diff.strip():
                output.append(filtered_diff)

    return '\n'.join(output)


def main():
    os.chdir(git_repo_path)
    """主函数"""
    print("代码变更分析（保留完整上下文）")
    print("=" * 50)

    # 获取文件状态
    status_output = run_git_command(['git', 'diff', 'HEAD', '--name-status'])
    if not status_output:
        print("没有检测到代码变更")
        return

    all_output = []

    # 处理每个文件
    for line in status_output.strip().split('\n'):
        if not line.strip():
            continue

        parts = line.split('\t')
        if len(parts) < 2:
            continue

        status = parts[0][0]
        file1 = parts[1]
        file2 = parts[2] if len(parts) > 2 else None
        print(f"{status}\t{file1}\t{file2}")

        if status == 'R' and file2:
            # 处理重命名
            all_output.append(f"🔄 重命名: {file1} → {file2}")
            all_output.append(process_file_diff(file2, 'M'))  # 显示新文件内容变更
        else:
            # 处理其他状态
            all_output.append(process_file_diff(file1, status))

        all_output.append("---\n\n")

    # 获取统计信息
    stat_output = run_git_command(['git', 'diff', 'HEAD', '--shortstat'])
    if stat_output:
        all_output.append("📊 变更统计:")
        all_output.append(stat_output.strip())

    # 输出所有内容
    final_output = '\n'.join(all_output)

    # 可选：限制总输出行数
    max_lines = 1000
    lines = final_output.split('\n')
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines.append(f"\n... (输出限制为 {max_lines} 行)")

    print('\n'.join(lines))

class Config:
    """配置类，用于存储所有配置项"""
    def __init__(self):
        self.git_input_length = 14000
        self.ai_enable_thinking = True
        self.ai_print_thinking = True
        self.enable_debug = False
        self.diff_type = 1
        self.operation_type = None
        self.code_file_summary_prompt = None


def load_config_from_ini(config_path='default_prompts/commit_msg_generate.ini'):
    import configparser
    """加载配置文件"""
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')

    final_config = Config()
    # 从配置文件读取默认值并设置到final_config中
    if config.has_section('commit_msg_generate'):
        if 'code_file_summary_prompt' in config['commit_msg_generate']:
            final_config.code_file_summary_prompt = config['commit_msg_generate']['code_file_summary_prompt']

    return final_config

if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    config = load_config_from_ini()
    print(config.code_file_summary_prompt)
    main()
