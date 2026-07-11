import json
import os
import re
from bs4 import BeautifulSoup
from synonyms_parser import parse_synonyms_from_sense, reset_counter


# xrefs 中 xt 属性到 JSON key 的映射
_XT_MAP = {
    'see': 'see_also',
    'rn': 'related_noun',
    'opp': 'opposite',
    'cp': 'compare',
    'syn': 'synonym',
    'nsyn': 'synonym',
}


def clean_text(text):
    """清理零宽字符等特殊字符，并规范化空白"""
    if not isinstance(text, str):
        return text
    # 移除零宽空格 (U+200B) 和其他零宽字符
    text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
    # 将换行和多余空白合并为单个空格
    text = re.sub(r'\s+', ' ', text).strip()
    # 移除中文字符之间的多余空格
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    # 移除中文标点后的多余空格
    text = re.sub(r'([：，。；！？、“”])\s+', r'\1', text)
    return text


def _parse_xrefs(soup):
    """解析 xrefs 元素，返回 {key: [items]} 字典"""
    xrefs_result = {}
    for xrefs in soup.find_all('span', class_='xrefs'):
        xt = xrefs.get('xt')
        if xt not in _XT_MAP:
            continue
        key = _XT_MAP[xt]
        items = []
        for a_tag in xrefs.find_all('a', class_='Ref'):
            href = a_tag.get('href', '')
            entry_match = re.match(r'entry://(.+)', href)
            if entry_match:
                xh = a_tag.find('span', class_='xh')
                title = clean_text(xh.get_text()) if xh else clean_text(a_tag.get_text())
                items.append({
                    'title': title,
                    'entry': entry_match.group(1)
                })
        if items:
            if key not in xrefs_result:
                xrefs_result[key] = items
            else:
                xrefs_result[key].extend(items)
    return xrefs_result


def _parse_topics(element):
    """解析 element 中的 topic，返回 topic 列表（href 中 entry:// 之后的部分）"""
    topics = []
    for topic_g in element.find_all('span', class_='topic-g'):
        for a_tag in topic_g.find_all('a', class_='Ref'):
            href = a_tag.get('href', '')
            match = re.match(r'entry://(.+)', href)
            if match:
                topics.append(match.group(1))
    return topics


def _extract_phrase_cn(element):
    """从 element 中移除 <dis-gT> 中文翻译标签，返回 (clean_text, phrase_cn)"""
    import copy
    el_copy = copy.copy(element)
    phrase_cn = None
    for dis_gt in el_copy.find_all('dis-gt'):
        chn_tag = dis_gt.find('chn')
        if chn_tag:
            text = clean_text(chn_tag.get_text())
            if text:
                phrase_cn = text
        dis_gt.decompose()
    return clean_text(el_copy.get_text()), phrase_cn


def parse_sense_header(sense_li):
    """解析 sense 的头部信息（从 <li class="sense"> 到 <ul class="examples"> 之间）
    
    返回包含以下字段的字典：
    - oxford_levels: 牛津等级列表（从 symbols 中的 a 标签解析）
    - grammar: 语法标注
    - phrase: 短语/变体形式（从 sensetop 中的 cf/variants 提取，或独立的 cf）
    - definition: 英文释义
    - definition_cn: 中文释义（支持 defT / adT 标签，包括内部的 ad/mh 等子标签）
    """
    header = {}

    # 1. 牛津等级（sense级别）
    sense_oxford_levels = []
    for a_tag in sense_li.find_all('a', href=re.compile(r'entry://@ox\d+&level=[a-zA-Z0-9]+')):
        href = a_tag.get('href', '')
        match = re.search(r'@ox(?P<dict>\d+)&level=(?P<level>[a-zA-Z0-9]+)', href)
        if match:
            sense_oxford_levels.append({
                'dictionary': f"ox{match.group('dict')}",
                'level': match.group('level')
            })
    if sense_oxford_levels:
        seen = set()
        unique = []
        for item in sense_oxford_levels:
            key = (item['dictionary'], item['level'])
            if key not in seen:
                seen.add(key)
                unique.append(item)
        header['oxford_levels'] = unique

    # 2. 标签/领域标注（labels，如 grammar语法、music音乐）
    labels = []

    # 从 div.variants 提取 labels（如果内部包含 span.labels），格式: (also {tags} → {variant})
    for variants_tag in sense_li.find_all('div', class_='variants'):
        if not variants_tag.find('span', class_='labels'):
            continue
        # 跳过 collapse 内部的（避免重复）
        if variants_tag.find_parent('div', class_='collapse'):
            continue

        # 提取 also（在 v-g 外面的情况，如 "(also <v-g>..." ）
        also_prefix = ""
        v_g = variants_tag.find('span', class_='v-g')
        if v_g and v_g.previous_sibling:
            prev_text = clean_text(str(v_g.previous_sibling))
            if 'also' in prev_text.lower():
                also_prefix = "also "

        # 提取 labels 文本
        labels_tag = variants_tag.find('span', class_='labels')
        labels_text = clean_text(labels_tag.get_text()) if labels_tag else ""

        # 如果 labels_text 以 also 开头，提取出来
        if labels_text.lower().startswith('also'):
            labels_text = labels_text[5:].lstrip()
            also_prefix = "also "

        # 提取变体词
        v_tag = variants_tag.find('span', class_='v')
        variant_word = clean_text(v_tag.get_text()) if v_tag else ""

        # 组合成 "({qualifier}{tags} → {variant})" 格式
        if labels_text and variant_word:
            label_text = f"({also_prefix}{labels_text} → {variant_word})"
            labels.append(label_text)
        elif labels_text:
            label_text = f"({also_prefix}{labels_text})"
            labels.append(label_text)

    # 独立的 span.labels（不在 div.variants 内部，也不在 div.collapse 内部的）
    for labels_tag in sense_li.find_all('span', class_='labels'):
        if labels_tag.find_parent('div', class_='variants'):
            continue
        if labels_tag.find_parent('div', class_='collapse'):
            continue
        label_text = clean_text(labels_tag.get_text())
        if label_text:
            labels.append(label_text)

    if labels:
        header['labels'] = labels

    # 3. 语法 (grammar) - 可能在 sensetop 内或 sensetop 外
    grammar_tag = sense_li.find('span', class_='grammar')
    if grammar_tag:
        header['grammar'] = clean_text(grammar_tag.get_text())

    # 4. 短语/变体形式（cf, variants 等）
    # 优先从 sensetop 提取，排除 grammar/def/symbols/labels/deft/adt/o10/包含labels的variants 等非短语内容
    sensetop = sense_li.find('span', class_='sensetop')
    if sensetop:
        import copy
        st_copy = copy.copy(sensetop)
        # 排除非短语内容（增加排除包含 labels 的 variants）
        for exclude in st_copy.find_all(['span', 'div'], class_=['def', 'symbols', 'grammar', 'labels']):
            exclude.decompose()
        # 排除包含 span.labels 的 div.variants
        for variants_tag in st_copy.find_all('div', class_='variants'):
            if variants_tag.find('span', class_='labels'):
                variants_tag.decompose()
        for exclude in st_copy.find_all(['deft', 'adt', 'o10']):
            exclude.decompose()
        # 排除 dis-g 中的 wrap 括号
        for exclude in st_copy.find_all('span', class_='wrap'):
            exclude.decompose()
        phrase_text, phrase_cn = _extract_phrase_cn(st_copy)
        if phrase_text:
            header['phrase'] = phrase_text
        if phrase_cn:
            header['phrase_cn'] = phrase_cn

    # 独立的 cf（如果 sensetop 中没有 phrase），排除 examples 内部的
    if 'phrase' not in header:
        for cf_tag in sense_li.find_all('span', class_='cf'):
            # 跳过在 examples 内部的 cf
            if cf_tag.find_parent('ul', class_='examples'):
                continue
            phrase_text, phrase_cn = _extract_phrase_cn(cf_tag)
            if phrase_text:
                header['phrase'] = phrase_text
            if phrase_cn:
                header['phrase_cn'] = phrase_cn
            break

    # 独立的 variants（如果还没有 phrase，且内部没有 span.labels）
    if 'phrase' not in header:
        for variants_tag in sense_li.find_all('div', class_='variants'):
            if variants_tag.find('span', class_='labels'):
                continue
            phrase_text, phrase_cn = _extract_phrase_cn(variants_tag)
            if phrase_text:
                header['phrase'] = phrase_text
            if phrase_cn:
                header['phrase_cn'] = phrase_cn
            break

    # 4. 英文释义（def 可能在 sensetop 内或 sensetop 外）
    def_tag = sense_li.find('span', class_='def')
    if def_tag:
        header['definition'] = clean_text(def_tag.get_text())

    # 5. 中文释义（支持 deft / adT 等多种标签，包括内部的 ad/mh 等子标签）
    for def_tag_name in ['deft', 'adt']:
        defT = sense_li.find(def_tag_name)
        if defT:
            chn_tag = defT.find('chn')
            if chn_tag:
                header['definition_cn'] = clean_text(chn_tag.get_text())
                break

    if header['definition'] and header['definition_cn']:
        header['definition'] = header['definition'].replace(header['definition_cn'], '')

    return header


def parse_sense_li(sense_li, output_dir=None):
    """解析单个 sense li 元素"""
    # 先解析头部信息
    sense = parse_sense_header(sense_li)

    # 解析 sense id
    sense_id = sense_li.get('id')
    if sense_id:
        sense['id'] = sense_id

    # 解析 topic
    sense_topics = _parse_topics(sense_li)
    if sense_topics:
        sense['topics'] = sense_topics

    # 例句 (examples)
    examples = []
    examples_ul = sense_li.find('ul', class_='examples')
    if examples_ul:
        for li in examples_ul.find_all('li', recursive=False):
            ex = {}
            # 提取 cf（短语搭配形式，在 example li 内部）
            cf_tag = li.find('span', class_='cf')
            if cf_tag:
                ex['phrase'] = clean_text(cf_tag.get_text())
            x_tag = li.find('span', class_='x')
            if x_tag:
                ex['en'] = clean_text(x_tag.get_text())
            # 支持 xt/at/ot 多种中文翻译标签
            for tag_name in ['xt', 'at', 'ot']:
                t_tag = li.find(tag_name)
                if t_tag:
                    chn_tag = t_tag.find('chn')
                    if chn_tag:
                        ex['cn'] = clean_text(chn_tag.get_text())
                        break
            # 提取例句美式发音文件名
            audio_wr = li.find('audio-wr')
            if audio_wr:
                us_audio_a = audio_wr.find('a', class_='pron-us')
                if us_audio_a:
                    href = us_audio_a.get('href', '')
                    ex['am_audio'] = href.replace('sound://', '')
            if ex:
                examples.append(ex)
    sense['examples'] = examples

    # 额外例句 (Extra Examples)
    extra_examples = []
    extra_unbox = sense_li.find('span', unbox='extra_examples')
    if extra_unbox:
        for li in extra_unbox.find_all('li'):
            ex = {}
            unx_tag = li.find('span', class_='unx')
            if unx_tag:
                ex['en'] = clean_text(unx_tag.get_text())
            oT_tag = li.find('ot')
            if oT_tag:
                chn_tag = oT_tag.find('chn')
                if chn_tag:
                    ex['cn'] = clean_text(chn_tag.get_text())
            if ex:
                extra_examples.append(ex)
    if extra_examples:
        sense['extra_examples'] = extra_examples

    # 搭配 (Collocations)
    collocations = {}
    all_collapse = sense_li.find_all('div', class_='collapse', recursive=False)
    for collapse in all_collapse:
        coll_box = collapse.find('span', class_='unbox')
        if coll_box and coll_box.find('span', class_='box_title', string='Oxford Collocations Dictionary'):
            for sub_unbox in coll_box.find_all('span', class_='unbox', recursive=True):
                coll_title = clean_text(sub_unbox.get_text())
                next_ul = sub_unbox.find_next_sibling()
                if next_ul and next_ul.name == 'ul':
                    items = [clean_text(li.get_text()) for li in next_ul.find_all('li')]
                    collocations[coll_title] = items
            break
    if collocations:
        sense['collocations'] = collocations

    # Synonyms box
    synonyms_titles = parse_synonyms_from_sense(sense_li, clean_text, output_dir)
    if synonyms_titles:
        if len(synonyms_titles) == 1:
            sense['synonyms'] = synonyms_titles[0]
        else:
            sense['synonyms'] = synonyms_titles

    # xrefs (see_also, related_noun, opposite, compare, synonym)
    xrefs_result = _parse_xrefs(sense_li)
    if xrefs_result:
        sense.update(xrefs_result)

    return sense


def _parse_single_entry(entry_soup, output_dir=None):
    """解析单个OALD entry为结构化JSON"""
    soup = entry_soup

    result = {}

    # 0. entry id（从 <div class="entry" id="..."> 提取）
    entry_div = soup.find('div', class_='entry')
    if entry_div:
        entry_id = entry_div.get('id')
        if entry_id:
            result['id'] = entry_id

    # 1. 单词 (headword)
    headword_tag = soup.find('h1', class_='headword')
    result['word'] = clean_text(headword_tag.get_text()) if headword_tag else None

    # 2. 词性 (pos)
    pos_tag = soup.find('span', class_='pos')
    result['pos'] = clean_text(pos_tag.get_text()) if pos_tag else None

    # 2.5 从 webtop 中提取 grammar 和 labels（排除 idiom 内部的 webtop）
    grammars = []
    labels = []
    for webtop in soup.find_all('div', class_='webtop'):
        # 跳过 idiom 内部的 webtop
        if webtop.find_parent('div', class_='idioms'):
            continue
        grammar_tag = webtop.find('span', class_='grammar')
        if grammar_tag:
            grammars.append(clean_text(grammar_tag.get_text()))
        for labels_tag in webtop.find_all('span', class_='labels'):
            label_text = clean_text(labels_tag.get_text())
            if label_text:
                labels.append(label_text)
    if grammars:
        result['grammar'] = grammars[0] if len(grammars) == 1 else grammars
    if labels:
        result['labels'] = labels

    # 3. 牛津等级（从 <a> 标签的 href 属性解析，支持 ox3000/ox5000 等）
    oxford_levels = []
    for a_tag in soup.find_all('a', href=re.compile(r'entry://@ox\d+&level=[a-zA-Z0-9]+')):
        href = a_tag.get('href', '')
        match = re.search(r'@ox(?P<dict>\d+)&level=(?P<level>[a-zA-Z0-9]+)', href)
        if match:
            oxford_levels.append({
                'dictionary': f"ox{match.group('dict')}",
                'level': match.group('level')
            })
    if oxford_levels:
        # 去重：通过 (dictionary, level) 元组来去重
        seen = set()
        unique_levels = []
        for item in oxford_levels:
            key = (item['dictionary'], item['level'])
            if key not in seen:
                seen.add(key)
                unique_levels.append(item)
        result['oxford_levels'] = unique_levels

    # 4. 音标 - 只保留美式音标及其发音文件名
    phon_am_tag = soup.find('div', class_='phons_n_am')
    phonetics = {}
    if phon_am_tag:
        phon_span = phon_am_tag.find('span', class_='phon')
        if phon_span:
            phonetics['am'] = clean_text(phon_span.get_text())
        # 提取发音文件名
        audio_a = phon_am_tag.find('a', href=re.compile(r'sound://.*\.mp3'))
        if audio_a:
            href = audio_a.get('href', '')
            phonetics['am_audio'] = href.replace('sound://', '')
    result['phonetics'] = phonetics

    # 5. Word Family
    word_family = []
    word_family_list = soup.find('span', unbox='wordfamily')
    if word_family_list:
        for li in word_family_list.find_all('li', class_='li'):
            text = clean_text(li.get_text(separator=' '))
            if text:
                word_family.append(text)
    result['word_family'] = word_family

    # 6. 释义 (senses) - 只从主释义列表(ol.senses_multiple / ol.sense_single)中查找
    senses = []
    sense_ol = soup.find('ol', class_=['senses_multiple', 'sense_single'])
    if sense_ol:
        sense_lis = sense_ol.find_all('li', class_='sense')
    else:
        sense_lis = soup.find_all('li', class_='sense')
    for sense_li in sense_lis:
        senses.append(parse_sense_li(sense_li, output_dir=output_dir))

    # 检查是否有 sense 包含 topic
    has_sense_topic = any('topics' in s for s in senses)

    # 如果没有 sense 有 topic，但 entry 有 topic，放到 word 级别
    if not has_sense_topic:
        entry_topics = _parse_topics(soup)
        if entry_topics:
            result['topics'] = entry_topics

    result['senses'] = senses

    # 解析 entry 级别的 xrefs（在 ol 内部与 li.sense 平级的位置）
    if sense_ol:
        for xrefs in sense_ol.find_all('span', class_='xrefs', recursive=False):
            xt = xrefs.get('xt')
            if xt not in _XT_MAP:
                continue
            key = _XT_MAP[xt]
            items = []
            for a_tag in xrefs.find_all('a', class_='Ref'):
                href = a_tag.get('href', '')
                entry_match = re.match(r'entry://(.+)', href)
                if entry_match:
                    xh = a_tag.find('span', class_='xh')
                    title = clean_text(xh.get_text()) if xh else clean_text(a_tag.get_text())
                    items.append({
                        'title': title,
                        'entry': entry_match.group(1)
                    })
            if items:
                if key not in result:
                    result[key] = items
                else:
                    result[key].extend(items)

    # 7. Idioms
    idioms = []
    idioms_div = soup.find('div', class_='idioms')
    if idioms_div:
        for idm_g in idioms_div.find_all('span', class_='idm-g'):
            idiom = {}
            # 习语短语
            idm_tag = idm_g.find('span', class_='idm')
            if idm_tag:
                idiom['phrase'] = clean_text(idm_tag.get_text())
            # 习语 labels
            idm_labels = idm_g.find('span', class_='labels')
            if idm_labels:
                idiom['labels'] = clean_text(idm_labels.get_text())
            # 释义
            idiom_senses = []
            idiom_ol = idm_g.find('ol', class_=['senses_multiple', 'sense_single'])
            if idiom_ol:
                for sense_li in idiom_ol.find_all('li', class_='sense'):
                    idiom_senses.append(parse_sense_li(sense_li, output_dir=output_dir))
            if idiom_senses:
                idiom['senses'] = idiom_senses
            if idiom:
                idioms.append(idiom)
    if idioms:
        result['idioms'] = idioms

    return result


def parse_oald_html(html_content, output_dir=None):
    """解析OALD HTML词典卡片为结构化JSON，支持多entry"""
    reset_counter()

    soup = BeautifulSoup(html_content, 'html.parser')

    result = []
    for entry_div in soup.find_all('div', id='entryContent'):
        entry = _parse_single_entry(entry_div, output_dir=output_dir)
        result.append(entry)

    return result


if __name__ == '__main__':
    import sys
    import glob

    # 如果没有参数，默认处理 test.html
    if len(sys.argv) > 1:
        input_pattern = sys.argv[1]
        input_files = glob.glob(input_pattern)
        if not input_files:
            print(f"没有匹配到文件: {input_pattern}")
            sys.exit(1)
    else:
        input_files = ['test.html']

    for input_file in input_files:
        print(f"\n处理文件: {input_file}")

        if not os.path.exists(input_file):
            print(f"文件不存在: {input_file}")
            continue

        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 输出JSONP
        output_file = os.path.splitext(input_file)[0] + '.json'
        output_dir = os.path.dirname(os.path.abspath(output_file))

        result = parse_oald_html(html_content, output_dir=output_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"转换完成，结果已保存到: {output_file}")
