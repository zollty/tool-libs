import os
from ai_code_review.get_git_context import get_gitlogs, get_gitdiffshow
from ai_code_review.git_diff_splitter import GitDiffSplitter
from ai_code_review.ai_chat import chat
from ai_code_review.utils import load_text

# prompt1 = """你是一个Java技术专家及项目经理，需要你对开发人员提交的代码进行评审，
# 代码变更信息已使用git命令获取如下所示，重点识别新增的行是否符合代码规范，如果没有严重问题就在第一行回答‘通过’2个字符后面不需要再解释，如果有严重问题，在第一行回答‘不通过’3个字，然后换行指出那些存在问题的代码、问题原因及建议解决方案："""

prompt = """你是一个Java技术专家及项目经理，需要你对开发人员提交的代码进行评审，
代码规范如下：
{}

现在请你准备接收用户给你的代码信息，并依据上述规范进行评审，需要你重点识别git新增的行是否符合上述规范，如果没有严重问题就在第一行回复‘通过’2个字符，后面不要再跟其他解释；如果有严重问题，在第一行回复‘不通过’3个字，然后换行指出那些存在问题的代码行、问题严重性（轻微/一般/中/高/阻塞）、问题原因及建议解决方案。"""

# 使用文件内容替换占位符
java_standards_file = "java_dev_standards.txt"  # 替换为实际的文件路径
standards_content = load_text(java_standards_file)
prompt = prompt.format(standards_content)
print(prompt)

def main():
    """
        主函数，用于执行代码审查流程

        参数:
            git_repo_path (str): Git仓库的本地路径，用于切换工作目录和执行git命令
            git_commit_since_time (str): 起始时间，用于筛选此时间之后的git提交记录
            input_length (int): 输入长度阈值，用于控制git diff内容的分割长度
    """
    # 切换工作目录
    os.chdir(git_repo_path)

    commit_logs = get_gitlogs(git_commit_since_time)
    commit_logs = commit_logs[5:]
    print("\n".join(commit_logs))
    # print(chat(get_gitdiffshow(git_repo_path, '2ad5edd52d')))

    for line in commit_logs:
        commit_id = line.split(' - ')[0]
        text = get_gitdiffshow(commit_id)
        # 将超过长度threshold_k的内容分割成多块，分割算法参见GitDiffSplitter
        splitter = GitDiffSplitter(text, threshold_k=input_length)
        # 执行分割
        segments = splitter.split_git_diff()
        idx = 1
        for segment in segments:
            result = chat(prompt, line+"\n"+segment)
            print(f'\n\n---------------------------------------------\n{line} {idx}\n{result}')
            idx += 1


if __name__ == "__main__":
    git_repo_path = "D:/__SYNC2/git-dms/dms-server-next"
    git_commit_since_time = "2025/08/19"
    input_length = 7000
    # test_cases()
    main()