from openai import OpenAI
import re, os, csv, time

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key="sk-78944c3f22b84cbea80eae4c70bf53c3", # 如何获取API Key：https://help.aliyun.com/zh/model-studio/developer-reference/get-api-key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

prompt1 = ('你是一个资深音乐人，请仔细理解下面的歌词，分析歌词的情感特点，并且给出它的愉悦度评分（参考'
          'Spotify的愉悦度，它是一个0到1之间的数值，表示歌曲的积极程度：0.0代表极度悲伤/消极，1.0代表极度快乐/喜悦，数值越高，歌曲听起来越愉悦）。'
          '评分基于歌词整体内容推断，如果大部分都是悲伤的，即使夹杂了一些积极情绪，仍然是愉悦度偏低的；'
          '但是你得审视一下，有写诗意的描述、美好的爱情、浪漫的回忆的歌词，虽然是淡淡的悲伤，但整体配合较轻快押韵的旋律后愉悦度也不算低，'
          '特别是有大量或者重复积极元素的歌词，可能是欢快或者有舞蹈性的，如果符合这个条件，其愉悦度不得低于0.5。'
          '另外，积极情绪并不意味着愉悦度高，例如我要飞得更高，只代表积极、有能量，但谈不上愉悦，愉悦更多是放松、快乐、愉快、喜悦的情绪。'
          '注意：请你在回复时第一行首先给出建议的愉悦度分数（一个准确的数字），然后换行再做简单分析。')

prompt = ('你是一个资深音乐人，请仔细理解下面的歌词，分析歌词的情感特点，并且给出它的愉悦度评分（参考'
          'Spotify的愉悦度，它是一个0到1之间的数值，表示歌曲的积极程度：0.0代表极度悲伤/消极，1.0代表极度快乐/喜悦，数值越高，歌曲听起来越愉悦）。'
          '评分基于歌词整体内容推断，如果大部分都是悲伤的，即使夹杂了一些积极情绪，仍然是愉悦度偏低的；'
          '另外，积极情绪并不意味着愉悦度高，例如我要飞得更高，只代表积极、有能量，但谈不上愉悦，愉悦更多是放松、快乐、愉快、喜悦的情绪。'
          '请你先想好一个初始分数。'
          '评完分，你再审视一下，有写诗意的描述、美好的爱情、浪漫的回忆、温柔感情的歌词，即使是淡淡的悲伤，但整体配合较轻快押韵的旋律后愉悦度也不算低，'
          '特别是有大量或者重复积极元素的歌词，可能是欢快或者有舞蹈性的，如果符合这个条件，要大幅提高其愉悦度分数。'
          '相反，如果确实大篇幅都是伤感的，不能因为夹杂了少量积极元素就加分。请根据审视结果修正分数。'
          '注意：请你在回复时第一行首先给出修正分数（一个准确的数字），然后换行，给出初始分数+简单分析。')

print(prompt)

def chat(lyric):
    completion = client.chat.completions.create(
        # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        model="qwen-plus",  # qwen-plus 属于 qwen3 模型，如需开启思考模式，请参见：https://help.aliyun.com/zh/model-studio/deep-thinking
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'歌词如下：\n{lyric}'}
        ]
    )

    result = completion.choices[0].message.content
    print(result)
    return result


def stream_chat(lyric):
    completion = client.chat.completions.create(
        model="qwen-plus",
        # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'歌词如下：\n{lyric}'}
        ],
        stream=True,
        # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
        # 使用Qwen3开源版模型时，请将下行取消注释，否则会报错
        # extra_body={"enable_thinking": False},
    )

    full_content = ""
    print("\n流式输出内容为：")
    for chunk in completion:
        # 如果stream_options.include_usage为True，则最后一个chunk的choices字段为空列表，需要跳过（可以通过chunk.usage获取 Token 使用量）
        if chunk.choices:
            full_content += chunk.choices[0].delta.content
            print(chunk.choices[0].delta.content)
    print(f"完整内容为：\n")
    ctx_arr = full_content.split('\n')
    # 提取第一行
    print(ctx_arr[0])
    # 获取除第一行外的其他行
    print('\n'.join(ctx_arr[1:]))

def get_cleaned_lyrics(raw_lyrics):
    # Step 1: 把英文中括号替换为中文中括号（避免冲突）
    lyrics = raw_lyrics.replace('[', '［').replace(']', '］')
    # Step 2: 使用正则表达式移除 ［时间戳］
    cleaned_lyrics = re.sub(r'［\d{2}:\d{2}\.\d+］', '', lyrics)
    return cleaned_lyrics

def get_lyrics():
    base_dir = "D:/__SYNC0-P/Downloads/CloudMusic/VipSongsDownload/aa"
    lyrics_data = []
    # 获取base_dir下的所有歌词文件内容，包括子目录
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".lrc"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    song_name = os.path.splitext(file)[0]  # 去掉扩展名作为歌曲名
                    parent_folder = os.path.basename(root)  # 获取当前文件所在目录名
                    lyrics_data.append({
                        "playlist": parent_folder,
                        "name": song_name,
                        "lyrics": get_cleaned_lyrics(content)
                    })
    return lyrics_data

# raw_documents = TextLoader("D:/__SYNC0-P/Downloads/CloudMusic/VipSongsDownload/2《愉悦巡航》Z2-Happy-13760170921/如果有来生 - 谭维维.lrc", encoding='utf-8').load()
#
# raw_lyrics = "\n".join([doc.page_content for doc in raw_documents])
# # Step 1: 把英文中括号替换为中文中括号（避免冲突）
# lyrics = raw_lyrics.replace('[', '［').replace(']', '］')
#
# # Step 2: 使用正则表达式移除 ［时间戳］
# cleaned_lyrics = re.sub(r'［\d{2}:\d{2}\.\d+］', '', lyrics)
#
# print(cleaned_lyrics)

# stream_chat(cleaned_lyrics)

# excel_data = []
# for song in song_data:
#     try:
#         result = chat(song["lyrics"])
#         lines = result.split('\n')
#         first_line = lines[0]
#         other_lines = '\n'.join(lines[1:])
#         excel_data.append({"歌曲名": song["name"], "愉悦度评分": float(first_line), "评分理由": other_lines})
#     except Exception as e:
#         print(e)
#
# import pandas as pd
#
# # 创建 DataFrame
# df = pd.DataFrame(excel_data)
#
# # 保存到 Excel 文件
# df.to_excel("output.xlsx", index=False)


def action():
    song_data = get_lyrics()
    # 定义CSV文件路径
    csv_file = "output.csv"

    # 写入表头（仅第一次）
    write_header = not os.path.exists(csv_file)

    with open(csv_file, mode='a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["歌单", "歌曲名", "愉悦度评分", "评分理由"])
        if write_header:
            writer.writeheader()

        for song in song_data:
            max_retries = 3  # 最大重试次数
            retry_count = 0
            success = False

            while retry_count < max_retries and not success:
                try:
                    result = chat(song["lyrics"])
                    lines = result.split('\n')
                    first_line = lines[0]
                    other_lines = '\n'.join(lines[1:])
                    row = {
                        "歌单": song["playlist"],
                        "歌曲名": song["name"],
                        "愉悦度评分": float(first_line),
                        "评分理由": other_lines
                    }
                    writer.writerow(row)
                    f.flush()  # 立即写入磁盘
                    print(f"已追加写入：{song['name']}")
                    success = True  # 成功则跳出循环

                except Exception as e:
                    retry_count += 1
                    print(f"[错误] {e}，歌曲《{song['name']}》第 {retry_count} 次重试前暂停 2 秒...")
                    time.sleep(2)  # 报错后暂停 2 秒

if __name__ == "__main__":
    action()