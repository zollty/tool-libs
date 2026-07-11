from ut import str, file

# 字符串工具使用示例
test_string = "   "
print(f"is_blank: {str.is_blank(test_string)}")  # True

# 文件工具使用示例
content = file.read_text('ut2.py')
print(f"File content: \n{content}")  # Hello, World!