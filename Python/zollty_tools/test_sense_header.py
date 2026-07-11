"""
测试 parse_sense_header 函数

测试数据来自 sense_data_example.html 中的5种不同 sense 结构：
1. phrase_sng_5: grammar 在 sensetop 内，cf 在 sensetop 外
2. phrase_sng_2: sensetop 内有 symbols（牛津等级）
3. novel_sng_3: variants 在 sensetop 内，grammar 在外，adT 有 ad/mh 子标签
4. variant_sng_2: cf 在 sensetop 内
5. variant_sng_1: def 和 adT 都在 sensetop 内
"""
import sys
import os
from bs4 import BeautifulSoup

# 将 zollty_tools 目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'zollty_tools'))

from html_to_json import parse_sense_header, clean_text


# 全局：加载测试数据
TEST_HTML_FILE = os.path.join(os.path.dirname(__file__), 'sense_data_example.html')
with open(TEST_HTML_FILE, 'r', encoding='utf-8') as f:
    TEST_HTML = f.read()

SENSE_SOUP = BeautifulSoup(TEST_HTML, 'html.parser')
SENSE_LIS = SENSE_SOUP.find_all('li', class_='sense')


def test_phrase_sng_5():
    """sense 1: grammar 在 sensetop 内，cf 在 sensetop 外"""
    sense_li = SENSE_LIS[0]
    result = parse_sense_header(sense_li)
    
    assert result['grammar'] == '[intransitive, transitive]'
    assert result['phrase'] == 'phrase (something)'
    assert result['definition'] == 'to divide a piece of music into small groups of notes; to play or sing these in a particular way, especially in an effective way'
    assert result['definition_cn'] == '划分乐句，分乐节（尤指为奏乐或歌唱）'
    print("✅ test_phrase_sng_5 passed")


def test_phrase_sng_2():
    """sense 2: sensetop 内有 symbols（牛津等级）"""
    sense_li = SENSE_LIS[1]
    result = parse_sense_header(sense_li)
    
    assert result['oxford_levels'] == [{'dictionary': 'ox3000', 'level': 'a1'}]
    assert 'grammar' not in result
    assert 'phrase' not in result
    assert result['definition'] == 'a group of words that have a particular meaning when used together'
    assert result['definition_cn'] == '成语；习语；惯用法；警句'
    print("✅ test_phrase_sng_2 passed")


def test_novel_sng_3():
    """sense 3: variants 在 sensetop 内，grammar 在外，adT 有 ad/mh 子标签"""
    sense_li = SENSE_LIS[2]
    result = parse_sense_header(sense_li)
    
    assert result['grammar'] == '[singular]'
    assert result['phrase'] == 'the novel'
    assert result['definition'] == 'the type of literature that novels represent'
    assert result['definition_cn'] == '小说：小说所代表的文学类型'
    print("✅ test_novel_sng_3 passed")


def test_variant_sng_2():
    """sense 4: cf 在 sensetop 内"""
    sense_li = SENSE_LIS[3]
    result = parse_sense_header(sense_li)
    
    assert 'grammar' not in result
    assert result['phrase'] == 'variant (of/on something)'
    assert result['definition'] == 'a thing that is a slightly different form or type of something else'
    assert result['definition_cn'] == '变种；变体；变形'
    print("✅ test_variant_sng_2 passed")


def test_variant_sng_1():
    """sense 5: def 和 adT 都在 sensetop 内"""
    sense_li = SENSE_LIS[4]
    result = parse_sense_header(sense_li)
    
    assert 'grammar' not in result
    assert 'phrase' not in result
    assert result['definition'] == 'slightly different in form or type from something else'
    assert result['definition_cn'] == '变体：形式或类型与其他形式略有不同'
    print("✅ test_variant_sng_1 passed")


if __name__ == '__main__':
    test_phrase_sng_5()
    test_phrase_sng_2()
    test_novel_sng_3()
    test_variant_sng_2()
    test_variant_sng_1()
    print("\n🎉 All tests passed!")
