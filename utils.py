from deepseek import get_response
from prompts import chapter_classifier_prompt
import re
from difflib import SequenceMatcher

def get_tag_content(content, full_tag):
    if " " in full_tag:
        tag = full_tag.split(" ")[0][1:]
    else:
        tag = full_tag[1:-1]
    pattern = re.compile(f'{full_tag}(.*?)</{tag}>', re.DOTALL)
    matches = pattern.findall(content)
    return matches

def get_tag_set(content):
    pattern = re.compile(r'<(\w+)([^>]*)>')
    # 使用正则表达式查找所有匹配的标签
    matches = pattern.findall(content)
    tag_set = set()
    tag_set.add("&#13;")
    for match in matches:
        tag, attributes = match
        if tag == "img":
            continue
        full_tag = f'<{tag}{attributes}>'
        tag_set.add(full_tag)
        tag_tail = f'</{tag}>'
        tag_set.add(tag_tail)
    return tag_set

def delete_tag(content, tag_set):
    for tag in tag_set:
        content = re.sub(tag, '', content)
    return content
def merge_same_tags(html_string):
    # 使用正则表达式匹配所有标签及其内容
    tag_set = get_tag_set(html_string)
    pattern = r'<(\w+)([^>]*)>(.*?)</\1>'
    matches = re.findall(pattern, html_string, re.DOTALL)

    # 用于存储合并后的标签内容
    merged_tags = []
    current_tag = None
    current_content = []

    for tag, attrs, content in matches:
        # 创建一个唯一的键来标识相同的标签和属性
        key = (tag, attrs)

        # 如果当前标签与上一个标签相同，则合并内容
        if key == current_tag:
            content = delete_tag(content, tag_set)
            # print('content',content)
            current_content.append(content.strip())
        else:
            # 如果当前标签与上一个标签不同，则保存上一个标签的内容
            if current_tag is not None:
                merged_tags.append((current_tag, ' '.join(current_content)))
            # 开始新的标签内容
            current_tag = key
            content = delete_tag(content, tag_set)
            current_content = [content.strip()]

    # 添加最后一个标签的内容
    if current_tag is not None:
        merged_tags.append((current_tag, ' '.join(current_content)))

    # 构建新的 HTML 字符串
    merged_html = ''
    for (tag, attrs), content in merged_tags:
        if len(content) > 10:
            content = content.replace('\n','')
            content = content.replace(' ','')
            content = content.replace('\u3000','')
            merged_html += f'<{tag}{attrs}>{content}</{tag}>\n'
        elif len(content) == 0:
            continue
        else:
            merged_html += f'<{tag}{attrs}>{content}</{tag}>\n'

    return merged_html.strip()


def clean_string(string):
    string = string.replace('\n','')
    string = string.replace(' ','')
    string = string.replace('\u3000','')
    pattern = re.compile(r'^\d+(\.\d+)*\s*')
    string = pattern.sub('', string)
    return string

def parse_merged_html(merged_html, pattern):
	matches = pattern.findall(merged_html)
	result = []
	for match in matches:
		result.append(clean_string(match.strip()))
	return result

def classify_chapter(chapter_name):
    response = get_response(chapter_name, chapter_classifier_prompt)
    return response == "true"

def parse_notes(notes, original_texts, marked_pattern):
    marked_notes = []
    explanation_notes = []
    for note, original_text in zip(notes, original_texts):
        marked_words = parse_merged_html(note, marked_pattern)
        # print(marked_words)
        marked_words_indexs = []
        for word in marked_words:
            if len(marked_words_indexs) == 0:
                marked_words_indexs.append(note.find(word))
            else:
                marked_words_indexs.append(note.find(word, marked_words_indexs[-1]+1))
        # print(marked_words_indexs)
        split_notes = []
        for i in range(len(marked_words_indexs)):
            if i == len(marked_words_indexs)-1:
                split_notes.append(note[marked_words_indexs[i]:])
            else:
                split_notes.append(note[marked_words_indexs[i]:marked_words_indexs[i+1]])

        # 正则表达式匹配括号及其内部的内容
        pattern = re.compile(r'（[^）]*）')
        marked_words = [pattern.sub('', annotation) for annotation in marked_words]
        
        explanation_note = {}
        for split_note, annotation in zip(split_notes, marked_words):
            text = '：'.join(split_note.split("：")[1:])
            pattern = re.compile(r'〔\d+〕')
            text = pattern.sub('', text)
            explanation_note[annotation] = text
        
        
        for i in range(len(split_notes)):
            if i == 0:
                pre_index = 0
            else:
                pre_index = original_text.find(f'〔{i}〕')
                cur_index = original_text.find(f'〔{i+1}〕')
                # print(pre_index, cur_index, original_text)
                original_text = original_text[:pre_index] + original_text[pre_index:cur_index].replace(marked_words[i], f"**{marked_words[i]}**") + original_text[cur_index:]

        pattern = re.compile(r'〔\d+〕')
        original_text = pattern.sub('', original_text)
        marked_notes.append(original_text)
        explanation_notes.append(explanation_note)
    original_texts = [pattern.sub('', original_text) for original_text in original_texts]

    return marked_notes, explanation_notes, original_texts

def get_tag_set(content):
    pattern = re.compile(r'<(\w+)([^>]*)>')
    # 使用正则表达式查找所有匹配的标签
    matches = pattern.findall(content)
    tag_set = set()
    tag_set.add("&#13;")
    for match in matches:
        tag, attributes = match
        if tag == "img":
            continue
        full_tag = f'<{tag}{attributes}>'
        tag_set.add(full_tag)
        tag_tail = f'</{tag}>'
        tag_set.add(tag_tail)
    return tag_set

def delete_tag(content, tag_set):
    for tag in tag_set:
        content = re.sub(tag, '', content)
    return content

def fuzzy_match(target, candidates, threshold=0.3):
    """
    基于编辑距离的模糊匹配算法
        :param target: 目标字符串
        :param candidates: 候选字符串列表
        :param threshold: 匹配阈值
        :return: 最佳匹配字符串
    """
    best_match = None
    best_ratio = 0
    index = -1
    for i, candidate in enumerate(candidates):
        ratio = SequenceMatcher(None, target, candidate).ratio()
        ratio = ratio * (len(target) + len(candidate)) / (2 * len(target))


        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate
            index = i
    return best_match if best_ratio >= threshold else None, best_ratio, index