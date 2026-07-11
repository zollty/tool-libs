import os
from ai_code_review.git_utils import run_git_command, git_diff_with_local_file

# 我通过git_diff_with_local_file()实现了将一个本地未跟踪的文件与已删除但未暂存的一个文件两者进行对比，但是还不够，
# 我现在还需要知道它们的相似度，我想知道已删除的这个文件是否与一个本地未跟踪的文件存在高度相似的情况，
# 相似度高于一定值，我就可以认定为该文件不是删除、而是重命名。
def git_diff_similarity(git_file_path, local_file_path, ref='HEAD', threshold=70):
    """
    使用git diff --numstat计算文件相似度

    Args:
        git_file_path: Git中文件的路径（已删除的文件）
        local_file_path: 本地文件的路径
        ref: Git引用，默认为HEAD
        threshold: 相似度阈值
    """
    try:
        # 使用git diff --numstat获取文件差异统计
        # result = subprocess.run(
        #     ['git', 'diff', '--numstat', f'{ref}:{git_file_path}', local_file_path],
        #     capture_output=True,
        #     text=True,
        #     encoding='utf-8',
        #     check=False  # 不检查返回码，因为diff有差异时返回非0
        # )
        #
        # if result.returncode not in [0, 1]:
        #     # 如果是其他错误代码
        #     print(f"Git命令执行错误: {result.stderr}")
        #     return None
        #
        # # 解析numstat输出
        # # 格式: <插入行数> <删除行数> <文件路径>
        # output_lines = result.stdout.strip().split('\n')
        # if not output_lines or not output_lines[0]:
        #     print("无法解析git diff输出")
        #     return None
        result = git_diff_with_local_file(git_file_path, local_file_path, True, ref)
        if result is not None:
            if len(result) == 0:
                return {
                    'similarity': 100,
                    'is_renamed': True,
                    'insertions': 0,
                    'deletions': 0,
                    'git_line_count': 0,
                    'local_line_count': 0
                }
        else:
            return {
                    'similarity': 0,
                    'is_renamed': False,
                    'insertions': 0,
                    'deletions': 0,
                    'git_line_count': 0,
                    'local_line_count': 0
                }
        output_lines = result.strip().split('\n')
        # 解析数字统计
        parts = output_lines[0].split('\t')
        if len(parts) < 2:
            print(f"输出格式异常: {result.stdout}")
            return None

        insertions = int(parts[0]) if parts[0] != '-' else 0
        deletions = int(parts[1]) if parts[1] != '-' else 0

        # 获取两个文件的总行数来计算相似度
        git_line_count = get_file_line_count(git_file_path, ref)
        local_line_count = get_local_file_line_count(local_file_path)

        if git_line_count is None or local_line_count is None:
            return None

        # 计算相似度
        total_changes = insertions + deletions
        total_lines = git_line_count + local_line_count

        if total_lines == 0:
            similarity = 1.0  # 两个空文件
        else:
            # 相似度 = 1 - (变化行数 / 总行数)
            similarity = 1.0 - (total_changes / total_lines)
            similarity = max(0.0, min(1.0, similarity))  # 确保在0-1范围内

        # 转换为0-100范围的整数
        if similarity == 1.0:
            similarity_percent = 100
        else:
            similarity_percent = min(99, round(similarity * 100))  # 四舍五入但最大为99
        return {
            'similarity': similarity_percent,
            'is_renamed': similarity_percent >= threshold,
            'insertions': insertions,
            'deletions': deletions,
            'git_line_count': git_line_count,
            'local_line_count': local_line_count
        }

    except Exception as e:
        print(f"计算相似度时出错: {e}")
        return None


def get_file_line_count(file_path, ref='HEAD'):
    """获取Git中文件的行数"""
    result = run_git_command(['git', 'show', f'{ref}:{file_path}'])
    if not result:
        return None
    return len(result.splitlines())

def get_local_file_line_count(file_path):
    """获取本地文件的行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"无法读取本地文件 {file_path}: {e}")
        return None


# 批量对比，找到最高相似度
def find_renamed_files(deleted_file, untracked_files, ref='HEAD', threshold=70):
    """
    在已删除文件和未跟踪文件之间寻找重命名关系
    """
    best_match = None
    best_similarity = 0

    for untracked_file in untracked_files:
        result = git_diff_similarity(deleted_file, untracked_file, ref, threshold)

        if result and result['similarity'] > best_similarity:
            best_similarity = result['similarity']
            best_match = {
                'deleted_file': deleted_file,
                'untracked_file': untracked_file,
                'similarity': result['similarity'],
                'details': result
            }

    if best_match and best_similarity >= threshold:
        return best_match

    return None


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    os.chdir(git_repo_path)
    # 使用示例
    print("==========================================================================================gradlew.bat")
    result = git_diff_similarity('gradlew.bat', 'changelog2.md')
    if result:
        print(f"相似度分析结果:")
        print(f"  相似度: {result['similarity']}%")
        print(f"  是否可能是重命名: {result['is_renamed']}")
        print(f"  插入行数: {result['insertions']}")
        print(f"  删除行数: {result['deletions']}")
        print(f"  Git文件行数: {result['git_line_count']}")
        print(f"  本地文件行数: {result['local_line_count']}")
    else:
        print("分析失败")

    print("==========================================================================================changelog.md")
    result = git_diff_similarity('changelog.md', 'changelog2.md')
    if result:
        print(f"相似度分析结果:")
        print(f"  相似度: {result['similarity']}%")
        print(f"  是否可能是重命名: {result['is_renamed']}")
        print(f"  插入行数: {result['insertions']}")
        print(f"  删除行数: {result['deletions']}")
        print(f"  Git文件行数: {result['git_line_count']}")
        print(f"  本地文件行数: {result['local_line_count']}")
    else:
        print("分析失败")