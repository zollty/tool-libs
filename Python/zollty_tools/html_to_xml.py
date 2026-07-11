from bs4 import BeautifulSoup

def strip_attrs(element):
    """移除元素所有属性"""
    if hasattr(element, 'attrs'):
        element.attrs.clear()

def clean_html(soup):
    """递归清理所有标签的属性"""
    for tag in soup.find_all(True):
        if tag.attrs:
            tag.attrs.clear()
    return soup

# 读取HTML文件
with open('test.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 解析并清理
soup = BeautifulSoup(html_content, 'html.parser')
soup = clean_html(soup)

# 获取美化后的XML输出
result = soup.prettify()

# 保存为XML格式
with open('test.xml', 'w', encoding='utf-8') as f:
    f.write(result)

# 保存为干净的HTML格式
html_output = soup.prettify(formatter='html')
with open('test_clean.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("转换完成，已保存到 test.xml 和 test_clean.html")
