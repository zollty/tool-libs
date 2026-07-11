import traceback
import re
import os

def load_text(file_path):
    """
    从文件中加载Java后端开发代码规范

    Args:
        file_path (str): 代码规范文件的路径

    Returns:
        str: 文件内容或默认提示信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'，请检查路径是否正确")
        exit(1)
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        traceback.print_exc()  # 打印完整堆栈信息
        exit(1)


def replace_file_references(text, base_path='.'):
    """
    检查文本中是否引用了其他文件，并用文件内容替换引用位置

    Args:
        text (str): 要处理的文本内容
        base_path (str): 文件引用的基准路径，默认为当前目录

    Returns:
        str: 处理后的文本内容
    """

    # 匹配 {@file:filename} 格式的引用，允许空格
    pattern = r'\{\s*@file\s*:\s*([^\s}]+)\s*\}'

    def replace_match(match):
        # 获取文件名
        file_name = match.group(1)

        if file_name:
            file_path = os.path.join(base_path, file_name)
            try:
                # 尝试读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                print(f"警告: 文件 '{file_path}' 未找到")
                return match.group(0)  # 返回原始引用字符串
            except Exception as e:
                print(f"警告: 读取文件 '{file_path}' 时出错: {e}")
                return match.group(0)  # 返回原始引用字符串

        return match.group(0)  # 如果没有匹配到文件名，返回原始字符串

    # 使用正则表达式替换所有匹配项
    result = re.sub(pattern, replace_match, text)
    return result


def check_and_replace_file_references(input_file, output_file=None, base_path='.'):
    """
    检查并替换文件中的引用

    Args:
        input_file (str): 输入文件路径
        output_file (str, optional): 输出文件路径，如果为None则覆盖原文件
        base_path (str): 文件引用的基准路径
    """
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换文件引用
        processed_content = replace_file_references(content, base_path)

        # 写入输出文件
        output_path = output_file if output_file else input_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        print(f"处理完成，结果已保存至: {output_path}")

    except FileNotFoundError:
        print(f"错误: 找不到输入文件 '{input_file}'")
    except Exception as e:
        print(f"处理文件时出错: {e}")

# 示例使用
if __name__ == "__main__":
    # 示例1: 直接处理文本
    sample_text = """这是一个示例文本。
它包含22个文件引用: @file:example.txt
它包含一个文件引用: { @file: code_review.ini }
还有另一种格式: {@file:java_dev_standards.txt}
以及正常的文本内容。"""

    print("原文本:")
    print(sample_text)
    print("\n处理后:")
    print(replace_file_references(sample_text))

    # 示例2: 处理文件
    # check_and_replace_file_references('input.txt', 'output.txt')
