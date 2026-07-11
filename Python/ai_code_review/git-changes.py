#!/usr/bin/env python3

import os
from typing import List, Dict
from ai_code_review.git_utils import run_git_command, check_under_git_dir
from ai_code_review.ai_chat import general_chat
from ai_code_review.git_diff_analyzer import (filter_git_changes_by_diff_type, get_file_content, GitFileChange,
                                              build_chat_context, print_single_file_changes, set_context_if_need)
from ai_code_review.obj_arr_split_algr import split_array_evenly

class Config:
    """配置类，用于存储所有配置项"""
    def __init__(self):
        self.git_input_length = 14000
        self.ai_enable_thinking = True
        self.ai_print_thinking = True
        self.enable_debug = True
        self.diff_type = 2
        self.operation_type = None
        self.commit_msg_generate_promt = None
        self.code_file_summary_prompt = None
        self.single_file_diff_modify_summary_prompt = None
        self.diff_modify_summary_prompt = None
        self.code_file_summary_max_lines = 200
        self.ignore_not_code_content = False  # 忽略非代码文件内容


def load_config_from_ini(config_path='default_prompts/commit_msg_generate.ini'):
    import configparser
    """加载配置文件"""
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')

    final_config = Config()
    # 从配置文件读取默认值并设置到final_config中
    if config.has_section('commit_msg_generate'):
        print(config['commit_msg_generate']['code_file_summary_prompt'])
        tmp = config['commit_msg_generate']
        if 'code_file_summary_prompt' in tmp:
            final_config.code_file_summary_prompt = tmp['code_file_summary_prompt']
        final_config.diff_modify_summary_prompt = tmp.get('diff_modify_summary_prompt', fallback=None)
        final_config.single_file_diff_modify_summary_prompt = tmp.get('single_file_diff_modify_summary_prompt', fallback=None)
        final_config.commit_msg_generate_promt = tmp.get('commit_msg_generate_promt', fallback=None)

    return final_config


def summary_modify_diff(file_changes: List[GitFileChange], config: Config) -> List[List[GitFileChange]]:
    """
    git diff内容裁剪、归并缩短算法：
    1、假设本次提交有100个文件改动，字符串总长度为1000k。
    2、如果某一个文件的改动就占了600k，其余99个文件共才400k，大文件只占1%的数量但是占了60%的长度，现在要把总token减少到100k以内，那该怎么办？
    3、把该裁剪那个大文件，还是裁剪小文件，他们裁剪的方式和比例怎么设计？
    4、我的想法是这样的，99个小文件裁不动、很难压缩（容易导致失真），但是大文件好压缩（有办法减少失真），所以大文件跟小文件的压缩方式是不一样的。
    5、上述假设只列举一个大文件的情况，实际情况可能比这个复杂
    我的算法是，如果本批次总长度超出限制，则找到里面最长的那个diff文件进行AI压缩，之后再重新计算总长度，递归操作。
    最终结果不改变原本文件顺序。
    """
    threshold_length = config.git_input_length
    total_length = sum([len(change.context)+50 for change in file_changes])
    if total_length <= threshold_length:
        return [file_changes]
    print(f"超过token数（{total_length} > {threshold_length}） 下面对最长的文件进行压缩...")
    max_len = 0
    max_len_change = None
    for change in file_changes:
        if len(change.context) > max_len:
            max_len = len(change.context)
            max_len_change = change

    if len(max_len_change.context) > 500:  # 精简成一小段
        print(f"\ta/{max_len_change.file1} b/{max_len_change.file2} diff内容太长({len(max_len_change.context)}>500)，正在精简...")
        chat_text = f"变动的文件: {max_len_change.file1}\n变动的文件内容:\n{max_len_change.context[:config.git_input_length]}"  # 不超过长度
        chat_result = general_chat(config.single_file_diff_modify_summary_prompt, chat_text,
                                   f"正在总结{os.path.basename(max_len_change.file1)}，请等待……", config.enable_debug)
        # f"## 文件: {max_len_change.file1}\n   状态: M-修改\n   文件改动点描述:\n{chat_result}"
        max_len_change.context = chat_result
        max_len_change.content_summarized = True
        print(f"\t精简后内容: {chat_result}")
    else:
        # 全都是短内容，无法再压缩了，此时必须对文件列表进行分段
        temp_arr = []
        for change in file_changes:
            temp_arr.append({"obj": change, "length": len(change.context)})
        temp_result = split_array_evenly(temp_arr, config.git_input_length)
        final_result = []
        for temp_arr2 in temp_result:
            final_result.append([temp_arr2[i]['obj'] for i in range(len(temp_arr2))])
        # 拆成多段直接返回
        return final_result

    return summary_modify_diff(file_changes, config)


def build_git_diff_context(config: Config):
    """
    构建用于chat的git diff内容
    """
    diff_type = config.diff_type
    max_lines = config.code_file_summary_max_lines
    print("正在分析Git变更...")
    file_changes = filter_git_changes_by_diff_type(diff_type)
    file_changes = set_context_if_need(file_changes, max_lines, config.ignore_not_code_content)

    # 处理新增和删除
    for i, change in enumerate(file_changes, 1):
        chat_result = None
        if change.status == 'A' and change.context:  # 新增
            if len(change.context) > 500: # 精简成一小段
                print(f"新增文件:{change.file1} 内容太长({len(change.context)}>500)，正在精简...")
                chat_result = general_chat(config.code_file_summary_prompt, change.context, f"正在总结{os.path.basename(change.file1)}，请等待……", config.enable_debug)

        elif change.status == 'D' and change.context:  # 删除
            if len(change.context) > 300: # 精简成一小段
                print(f"删除文件:{change.file1} 内容太长({len(change.context)}>300)，正在精简...")
                chat_result = general_chat(config.code_file_summary_prompt, change.context, f"正在总结{os.path.basename(change.file1)}，请等待……", config.enable_debug)

        print_single_file_changes(change, i, chat_result)
        if chat_result:
            change.context = chat_result
            change.content_summarized = True

    # 处理修改
    final_changes_arr = summary_modify_diff(file_changes, config)

    return final_changes_arr


def do_commit_msg_generate_chat(final_changes_arr: List[List[GitFileChange]], config: Config):
    final_chat_text = ""
    if len(final_changes_arr) > 1:
        final_chat_context = []
        for file_changes in final_changes_arr:
            chat_text = build_chat_context(file_changes)
            chat_result = general_chat(config.diff_modify_summary_prompt, chat_text, f"正在总结中，请等待……", config.enable_debug)
            final_chat_context.append(chat_result)
            print(f"\t第一次归纳内容: {chat_result}")
        final_chat_text = "\n\n\n".join(final_chat_context)
    else:
        final_chat_text = build_chat_context(final_changes_arr[0])

    print("-" * 80)
    print("-" * 80)
    print(f"最终结果:")
    chat_result = general_chat(config.commit_msg_generate_promt, final_chat_text, f"正在总结中，请等待……", config.enable_debug)
    print(chat_result)


def test_split_array_evenly():
    import random
    file_changes = filter_git_changes_by_diff_type(2)
    # 全都是短内容，无法再压缩了，此时必须对文件列表进行分段
    temp_arr = []
    idx = 0
    for _ in range(10):
        # 方法2：使用 random.sample() 创建随机排序的新列表
        shuffled_changes = random.sample(file_changes, len(file_changes))
        for change in shuffled_changes:
            print(idx, change.file1, len(change.context))
            temp_arr.append({"id": idx, "obj": change, "length": len(change.context)+50})
            idx += 1

    temp_result = split_array_evenly(temp_arr, 1000)
    final_result = []
    for temp_arr2 in temp_result:
        ids_and_lengths = [(item['id'], item['length']) for item in temp_arr2]
        print(ids_and_lengths)
        final_result.append([temp_arr2[i]['obj'] for i in range(len(temp_arr2))])


def test_prompts(config: Config):
    from ai_code_review.utils import load_text
    final_chat_text = ""
    def do_test(prompt: str, context_file_path: str):
        context = load_text(context_file_path)
        chat_result = general_chat(prompt, context, f"正在总结{os.path.basename(context_file_path)}，请等待……",  config.enable_debug)
        print("-" * 80)
        print(f"AI 输出结果为:")
        print(chat_result)
        return chat_result


    chat_result = do_test(config.single_file_diff_modify_summary_prompt,
            "test_resources/single_file_diff_modify_summary_prompt_test01.txt")
    final_chat_text += f"## 文件: org/hilo/boot/app/component/ShowConfig.java\n   状态: M-修改\n   文件改动点描述:\n{chat_result}"

    final_chat_text += "\n\n\n"
    chat_result = do_test(config.single_file_diff_modify_summary_prompt,
            "test_resources/single_file_diff_modify_summary_prompt_test02.txt")
    final_chat_text += f"## 文件: com/zollty/oa/pc/file/ShowDirSize.java\n   状态: M-修改\n   文件改动点描述:\n{chat_result}"

    final_chat_text += "\n\n\n"
    final_chat_text += do_test(config.diff_modify_summary_prompt,
            "test_resources/diff_modify_summary_prompt_test01.txt")

    final_chat_text += "\n\n\n"
    final_chat_text += load_text("test_resources/other_changes.txt")

    final_chat_text += "\n\n\n"
    chat_result = do_test(config.code_file_summary_prompt,
                          "test_resources/add_file.txt")
    final_chat_text += f"## 文件: org/hilo/boot/core/logback/FixedLogbackLoggingSystem.java\n   状态: A-新增\n   文件内容总结:\n{chat_result}"

    chat_result = general_chat(config.commit_msg_generate_promt, final_chat_text, f"正在总结中，请等待……",  config.enable_debug)
    print("-" * 80)
    print(f"最终结果为:{chat_result}")


if __name__ == "__main__":
    os.environ["OPENAI_API_KEY"] = "111111111111"
    git_repo_path = "D:/__SYNC2/android/i-music"
    config = load_config_from_ini()
    test_prompts(config)

    os.chdir(git_repo_path)
    check_under_git_dir()

    # test_split_array_evenly()


    # final_changes_arr = build_git_diff_context(config)
    # do_commit_msg_generate_chat(final_changes_arr, config)