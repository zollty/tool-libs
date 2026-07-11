import subprocess
import os
from typing import List, Dict


def check_under_git_dir():
    # 检查当前目录是否是git仓库
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'],
                       check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("错误：当前目录不是Git仓库")
        raise e


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


STATUS_DICT = {
        'A': '新增',
        'D': '删除',
        'M': '修改',
        'R': '重命名',
        'C': '复制',
        'RM': '重命名且修改',
    }


CODE_FILES = [
    '.java',
    '.py',
    '.js',
    '.kt',
    '.ts',
    '.cjs',
    '.vue',
    '.cpp',
    '.c',
    '.h',
    '.html',
    '.css',
    '.xml',
    '.bat',
    '.sh'
]


def is_code_file(file_name: str) -> bool:
    return file_name.endswith(tuple(CODE_FILES))


def is_text_file(file_path: str) -> bool:
    """
    判断文件是否为文本文件
    通过读取文件的前几KB内容来判断是否包含大量不可打印字符
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)  # 读取前1024字节

        if not chunk:
            return True  # 空文件视为文本文件

        # 统计可打印字符和常见文本字符
        text_chars = sum(1 for byte in chunk
                         if byte == 9 or byte == 10 or byte == 13 or
                         (32 <= byte <= 126))  # TAB, LF, CR, 和可打印ASCII字符

        # 如果可打印字符比例超过70%，则认为是文本文件
        return (text_chars / len(chunk)) > 0.7
    except:
        # 出现异常时，默认视为文本文件处理
        return True


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
        '.kt': 'Kotlin source',
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


def git_diff_with_local_file(git_file_path, local_file_path, numstat=False, ref='HEAD'):
    """
    使用git diff对比Git中的文件与本地文件

    Args:
        git_file_path: Git中文件的路径（已删除的文件）
        local_file_path: 本地文件的路径
        ref: Git引用，默认为HEAD

    return:
        None: 代表报错
        "": 代表无差异
        str: 代表有差异
    """
    if not os.path.exists(local_file_path):
        print(f"本地文件 {local_file_path} 不存在")
        return None

    if numstat:
        cmd = ['git', 'diff', '--numstat', f'{ref}:{git_file_path}', local_file_path]
    else:
        cmd = ['git', 'diff', f'{ref}:{git_file_path}', local_file_path]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    # 如果stdout不为空，则返回stdout
    if result.stdout:
        return result.stdout
    # 如果stdout为空，检查stderr
    elif result.stderr:
        # 忽略warning信息，只处理真正的错误
        stderr_lines = result.stderr.strip().split('\n')
        error_lines = [line for line in stderr_lines if not line.startswith('warning:')]

        if error_lines:
            print(f"Error: {result.stderr}")
            return None
        else:
            print(f"Warning: {result.stderr}")
            # 只有warning，视为无差异
            return ""
    else:
        # 没有输出，没有错误，表示没有差异
        return ""


def get_file_status() -> List[str]:
    """
    获取git状态信息
    """
    try:
        # 获取git状态信息
        cmd = ['git', 'status', '--porcelain']
        result = run_git_command(cmd)
        return result.split('\n')
    except Exception as e:
        print(f"Error: {e}")
        return []


def test_git_diff_with_local_file():
    # 使用示例
    print("========================================gradlew.bat")
    diff_output = git_diff_with_local_file('gradlew.bat', 'gradlew2.bat')
    if diff_output is not None:
        if diff_output == "":
            print("No differences found.")
        else:
            print(diff_output)
    else:
        print("An error occurred.")
    print("========================================changelog.md")
    diff_output = git_diff_with_local_file('changelog.md', 'changelog2.md')
    if diff_output is not None:
        if diff_output == "":
            print("No differences found.")
        else:
            print(diff_output)
    else:
        print("An error occurred.")


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    os.chdir(git_repo_path)
    check_under_git_dir()

    test_git_diff_with_local_file()
