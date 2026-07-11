import re
from collections import Counter

# 测试
text = """The line chart illustrates the sales volume of new energy vehicles in China from 2018 to 2022, which clearly demonstrates a sharp upward trend in terms of annual figures.

To be more specific, the number of new energy vehicles sold increased significantly, rising from 1.26 million in 2018 to 6.88 million in 2022. What’s more, the market share of such vehicles also grew steadily.

There are at least three factors accounting for this phenomenon. First and foremost, with the rapid development of the national economy, people’s living standards have improved accordingly, leading to a stronger demand for green and high-tech products. In addition, substantial policy support from the government, such as purchase subsidies and tax incentives, has encouraged this shift. Another essential cause is the advancement of battery technology, which has made electric vehicles more practical and affordable.

In conclusion, the rising trend is likely to persist in the near future. This is a positive development that contributes to environmental sustainability.
"""


def count_words_basic(text):
    """
    基础方法：使用split()分割单词
    优点：简单快速
    缺点：不能正确处理标点符号（如 "word." 会被当作 "word" 和 "." 两个部分）
    """
    words = text.split()
    return len(words)


def count_words_regex(text):
    """
    使用正则表达式统计单词个数
    优点：能正确处理标点符号和连字符
    """
    # \w+ 匹配一个或多个字母数字字符（包括下划线）
    # 如果想要更精确，可以使用 [a-zA-Z0-9]+
    words = re.findall(r'\b[\w\'-]+\b', text)

    # 显示前20个单词
    print("前20个单词:", words[:20])
    return len(words)


def analyze_words(text):
    """
    增强版：统计单词数量并分析词频
    """
    # 将文本转换为小写，统一计数
    text_lower = text.lower()

    # 使用正则表达式提取单词
    # \b 表示单词边界，[\w\'-]+ 匹配一个或多个字母数字字符、连字符或撇号
    words = re.findall(r"\b[\w'-]+\b", text_lower)

    # 统计词频
    word_freq = Counter(words)

    print(f"总单词数: {len(words)}")
    print(f"去重后的单词数: {len(word_freq)}")
    print("\n最常见的10个单词:")

    # 按频率排序
    for word, freq in word_freq.most_common(10):
        print(f"  '{word}': {freq}次")

    return len(words), word_freq


def count_words_simple(text):
    """
    最简单实用的单词计数函数
    """
    # 匹配一个或多个字母数字字符，可以包含连字符和撇号
    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)


print(f"基础方法统计: {count_words_basic(text)} 个单词")

# 快速使用
word_count = count_words_simple(text)
print(f"最简单正则方法-文本中的单词数: {word_count}")


print(f"标准正则表达式方法统计: {count_words_regex(text)} 个单词")


# 使用增强版
word_count, word_freq = analyze_words(text)