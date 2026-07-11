
def get_gitlogs(date: str):
    import subprocess
    cmd = f'git log --since="{date}" --no-merges  --pretty=format:"%h - %an, %ad : %s" --date=short'

    # 执行git命令并获取结果，指定编码为utf-8
    ret = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    # 检查命令执行是否成功
    if ret.returncode != 0:
        print(f"{cmd}\nGit命令执行失败: {ret.stderr}")
        return []

    # 按行分割输出，并提取每行的第一个元素（commit hash）
    result_data = []
    for line in ret.stdout.strip().split('\n'):
        if line and len(line.split(' - ')) > 0:
            result_data.append(line)

    return result_data


def get_gitdiffshow(commit_id: str):
    import subprocess
    cmd = f'git show {commit_id}'

    # 执行git命令并获取结果，指定编码为utf-8
    ret = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    # 检查命令执行是否成功
    if ret.returncode != 0:
        print(f"Git命令执行失败: {ret.stderr}")
        return []

    result_data = ret.stdout

    # 去掉第一个diff之前的信息
    idx = result_data.find("diff --git")
    result_data = result_data[idx:]

    return result_data


def get_local_commit_diff(diff_type: int = 2):
    """
    获取本地git diff信息

    git status会显示3类文件
    1、已暂存文件（已add的文件）：绿色
    2、未暂存文件（Changes not staged for commit）：红色
    3、未追踪文件（Untracked files）：红色
    例如：
    $ git status
On branch master
Your branch is up to date with 'origin/master'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        renamed:    changelog.md -> changelog2.md
        renamed:    generate-pngs.sh -> generate-pngs2.sh
        new file:   generate-themes2.pl
        new file:   gradlew2.bat

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   app/src/main/AndroidManifest.xml
        modified:   app/src/main/java/ch/blinkenlights/android/vanilla/PlaybackService.java
        modified:   app/src/main/java/ch/blinkenlights/android/vanilla/SeriesParser.java
        modified:   changelog2.md
        deleted:    generate-themes.pl
        deleted:    gradlew
        deleted:    gradlew.bat

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        aaa.sh
        bbb.sh
        ccc.sh
        ddd.sh

    Args:
        diff_type (int): diff类型，默认2
            - 0: 只diff未暂存的文件 (git diff) - 对应status看到的绿色文件
            - 1: 只diff已暂存的文件 (git diff --cached) - 对应status看到的红色Changes文件
            - 2: diff所有文件 (git diff HEAD) - 工作区与HEAD的差异（包括已暂存和未暂存）
    注意，无论哪种diff，都不包含Untracked（未追踪的，即新增但未add的）文件
    """
    import subprocess
    cmd = ''
    if diff_type == 0:
        cmd = 'git diff'
    elif diff_type == 1:
        cmd = 'git diff --cached'
    elif diff_type == 2:
        cmd = 'git diff HEAD'
    else:
        print(f"only_added参数错误: {diff_type}")
        return []
    # 执行git命令并获取结果，指定编码为utf-8
    ret = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
    # 检查命令执行是否成功
    if ret.returncode != 0:
        print(f"Git命令执行失败: {ret.stderr}")
        return []

    result_data = ret.stdout

    # 去掉第一个diff之前的信息
    idx = result_data.find("diff --git")
    result_data = result_data[idx:]

    return result_data