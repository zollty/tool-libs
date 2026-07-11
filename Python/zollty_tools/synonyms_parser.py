import json
import os


# synonyms 文件计数器：{title: 下一个可用数字}
_file_counter = {}


def _get_filename(title):
    """生成唯一的 synonyms 文件名，格式: title-N.json"""
    global _file_counter
    count = _file_counter.get(title, 0)
    _file_counter[title] = count + 1
    return f"{title}-{count}.json"


def reset_counter():
    """重置文件计数器，通常在处理新文件前调用"""
    global _file_counter
    _file_counter = {}


def _parse_synonyms_body(body, clean_text):
    """解析 synonyms body 内容，返回结构化字典"""
    import copy
    result = {}

    # 提取 title（body 内直接子元素的 span.unbox）
    title_tag = body.find('span', class_='unbox', recursive=False)
    if title_tag:
        result['title'] = clean_text(title_tag.get_text())

    # 同义词列表
    inline_ul = body.find('ul', class_='inline', recursive=False)
    if inline_ul:
        result['synonyms'] = [clean_text(li.get_text()) for li in inline_ul.find_all('li', class_='li', recursive=False)]

    # 描述段落
    p_tag = body.find('span', class_='p', recursive=False)
    if p_tag:
        result['description'] = clean_text(p_tag.get_text())

    # 详细定义列表
    deflist = body.find('ul', class_='deflist', recursive=False)
    if deflist:
        definitions = []
        for li in deflist.find_all('li', class_='li', recursive=False):
            def_item = {}

            # dt 标签
            dt = li.find('span', class_='dt', recursive=False)
            if dt:
                def_item['term'] = clean_text(dt.get_text())

            # dd 标签
            dd = li.find('span', class_='dd', recursive=False)
            if dd:
                # 提取定义文本（排除内部的 examples 和 labels）
                dd_copy = copy.copy(dd)
                for ex in dd_copy.find_all('ul', class_='examples'):
                    ex.decompose()
                for lbl in dd_copy.find_all('span', class_='labels'):
                    lbl.decompose()
                def_text = clean_text(dd_copy.get_text())
                if def_text:
                    def_item['definition'] = def_text

                # 提取例句
                examples = []
                for ex_ul in dd.find_all('ul', class_='examples'):
                    for ex_li in ex_ul.find_all('li', recursive=False):
                        ex_data = {}
                        # 先提取中文翻译
                        cn_text = ""
                        for tag_name in ['at', 'ot', 'unxt']:
                            t_tag = ex_li.find(tag_name)
                            if t_tag:
                                chn_tag = t_tag.find('chn')
                                if chn_tag:
                                    cn_text = clean_text(chn_tag.get_text())
                                    break
                        # 英文文本：取 unx 完整内容，再剔除中文部分
                        unx = ex_li.find('span', class_='unx')
                        if unx:
                            en_text = clean_text(unx.get_text())
                            if cn_text:
                                en_text = en_text.replace(cn_text, '').strip()
                            ex_data['en'] = en_text
                        if cn_text:
                            ex_data['cn'] = cn_text
                        if ex_data:
                            examples.append(ex_data)
                if examples:
                    def_item['examples'] = examples

            # labels（li 级别或 dd 内部）
            labels = li.find('span', class_='labels', recursive=False)
            if not labels and dd:
                labels = dd.find('span', class_='labels')
            if labels:
                def_item['labels'] = clean_text(labels.get_text())

            # undt 标签（中文翻译，在 dd 同级；BeautifulSoup 标签名转小写）
            undt = li.find('undt')
            if undt:
                chn_tag = undt.find('chn')
                if chn_tag:
                    def_item['definition_cn'] = clean_text(chn_tag.get_text())

            if def_item:
                definitions.append(def_item)
        if definitions:
            result['definitions'] = definitions

    # Patterns
    patterns_tag = body.find('span', class_='patterns', recursive=False)
    if patterns_tag:
        patterns_ul = patterns_tag.find_next_sibling()
        if patterns_ul and patterns_ul.name == 'ul' and 'bullet' in (patterns_ul.get('class') or []):
            patterns = []
            for li in patterns_ul.find_all('li', class_='li', recursive=False):
                text = clean_text(li.get_text())
                if text:
                    patterns.append(text)
            if patterns:
                result['patterns'] = patterns

    return result


def parse_synonyms_from_sense(sense_li, clean_text, output_dir=None):
    """从 sense_li 中解析 synonyms box，写入独立文件，返回 titles 列表"""
    synonyms_titles = []
    all_collapse = sense_li.find_all('div', class_='collapse', recursive=False)
    for collapse in all_collapse:
        unbox = collapse.find('span', attrs={'unbox': 'synonyms'})
        if not unbox:
            continue

        body = unbox.find('span', class_='body')
        if not body:
            continue

        # 提取 title (span.body > span.unbox 的文本)
        title_tag = body.find('span', class_='unbox', recursive=False)
        if not title_tag:
            continue

        title = clean_text(title_tag.get_text())
        if not title:
            continue

        # 解析 body
        synonyms_data = _parse_synonyms_body(body, clean_text)

        # 生成文件名
        filename = _get_filename(title)

        # 写入文件
        filepath = os.path.join(output_dir, filename) if output_dir else filename
        try:
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(synonyms_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入 synonyms 文件失败: {filepath}, 错误: {e}")

        synonyms_titles.append(title)

    return synonyms_titles
