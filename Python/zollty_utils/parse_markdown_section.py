import re
import json


def parse_markdown_to_sections(markdown_text):
    """
    解析Markdown，返回包含标题、级别和内容的字典列表
    """
    lines = markdown_text.split('\n')
    sections = []
    current_section = None
    content_lines = []

    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if match:
            # 保存上一个章节（如果有的话）
            if current_section:
                current_section['content'] = '\n'.join(content_lines)
                sections.append(current_section)

            # 开始新的章节
            level = len(match.group(1))
            title = match.group(2).strip()

            current_section = {
                'level': level,
                'title': title,
                'content': ''
            }

            content_lines = []  # 重置内容行
        elif current_section:
            # 如果不是标题行且当前有章节，则添加到内容中
            content_lines.append(line)
        # 忽略第一个标题之前的内容

    # 保存最后一个章节
    if current_section:
        current_section['content'] = '\n'.join(content_lines)
        sections.append(current_section)

    return sections


def parse_markdown_to_sections_clean(markdown_text):
    """
    解析Markdown，并清理内容的开头和结尾空行
    """
    lines = markdown_text.split('\n')
    sections = []
    current_section = None
    content_lines = []

    for line in lines:
        match = re.match(r'^(#{1,6})\s+(.+)$', line)

        if match:
            # 保存上一个章节（如果有的话）
            if current_section:
                # 清理开头和结尾的空行
                while content_lines and content_lines[0].strip() == '':
                    content_lines.pop(0)
                while content_lines and content_lines[-1].strip() == '':
                    content_lines.pop()

                current_section['content'] = '\n'.join(content_lines)
                sections.append(current_section)

            # 开始新的章节
            level = len(match.group(1))
            title = match.group(2).strip()

            current_section = {
                'level': level,
                'title': title,
                'content': ''
            }

            content_lines = []
        elif current_section:
            content_lines.append(line)

    # 保存最后一个章节
    if current_section:
        # 清理开头和结尾的空行
        while content_lines and content_lines[0].strip() == '':
            content_lines.pop(0)
        while content_lines and content_lines[-1].strip() == '':
            content_lines.pop()

        current_section['content'] = '\n'.join(content_lines)
        sections.append(current_section)

    return sections


# 扁平化输出函数
def flatten_markdown_sections(markdown_text):
    sections = parse_markdown_to_sections(markdown_text)
    flat_sections = []

    for section in sections:
        flat_section = {
            'level': section['level'],
            'title': section['title'],
            'content': section['content'],
            # 'summary': section['content'][:100].replace('\n', ' ') + '...'  # 可选摘要
        }
        flat_sections.append(flat_section)

    return flat_sections


# 统计信息函数
def get_markdown_stats(markdown_text):
    sections = parse_markdown_to_sections(markdown_text)

    stats = {
        'total_sections': len(sections),
        'level_counts': {},
        'total_content_length': 0,
        'avg_content_length': 0
    }

    total_chars = 0

    for section in sections:
        level = section['level']
        stats['level_counts'][level] = stats['level_counts'].get(level, 0) + 1
        total_chars += len(section['content'])

    stats['total_content_length'] = total_chars
    stats['avg_content_length'] = total_chars / len(sections) if sections else 0

    return stats


def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


if __name__ == '__main__':
    # 示例使用
    markdown = """# 第一章 简介

这是第一章的介绍内容。

这里可以有多行文本。

## 1.1 背景

这是背景介绍。

### 1.1.1 研究现状

现状描述。

## 1.2 目标

目标描述。

# 第二章 实现

实现细节"""

    file_path = r'D:\__SYNC2\git\JDK17\code_review_plugins\code-reviewer\api_chat\data2\summary\wholesales-service\com.yonyou.cms.wholesales.service.controller.MaterialPriceController.getMaterialPriceList-summary.md'
    markdown = read_text_file(file_path)

    sections = parse_markdown_to_sections(markdown)
    print(json.dumps(sections, indent=2, ensure_ascii=False))