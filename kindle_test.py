import json
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import ebooklib
import re
import bs4

sample_json_result = {
    "title": "书名",
    "chapters": [
        {
            "chapter_title": "章节标题",
            "sections": [
                {
                    "section_title": "小节标题",
                    "original_text": "原文内容",
                    "annotations": [
                        {
                            "annotation_id": "注解编号",
                            "text": "注解内容",
                            "refers_to": "关联的原文段落"
                        }
                    ],
                    "translation": "译文内容"
                }
            ]
        }
    ]
}


def load_epub_file(file_path: str) -> epub.EpubBook:
    return epub.read_epub(file_path)


def search_chapter(chapters, chapter_title_class, chapter_title_tag, child_hierarchy):
    sections = []
    # 查找当前级别的所有章节标题
    if chapter_title_class:
        chapter_elements = chapters.find_all(chapter_title_tag, class_=chapter_title_class)
    else:
        chapter_elements = chapters.find_all(chapter_title_tag)

    if not chapter_elements:
        return []

    for chapter_element in chapter_elements:
        chapter_title = chapter_element.get_text(strip=True)

        # 初始化当前章节的内容和子章节列表
        original_sections_bs4 = []
        original_sections_text = []
        child_sections = []

        # 定位到下一个兄弟节点
        sibling = chapter_element.next_sibling

        while sibling:
            if isinstance(sibling, bs4.element.Tag):
                # 检查是否为同级别的章节标题，若是则停止
                if sibling.name == chapter_title_tag:
                    if chapter_title_class:
                        if chapter_title_class in sibling.get('class', []):
                            break
                    else:
                        break

                # 检查是否为子章节标题
                is_subchapter = False
                if child_hierarchy:
                    next_tag, next_class = child_hierarchy[0]
                    if sibling.name == next_tag:
                        if next_class:
                            if next_class in sibling.get('class', []):
                                is_subchapter = True
                        else:
                            is_subchapter = True

                if is_subchapter:
                    # 收集子章节内容
                    subchapter_elements = [sibling]
                    sub_sibling = sibling.next_sibling
                    while sub_sibling:
                        if isinstance(sub_sibling, bs4.element.Tag):
                            # 检查是否为同级别的章节标题或下一个子章节标题
                            if sub_sibling.name == chapter_title_tag:
                                if chapter_title_class:
                                    if chapter_title_class in sub_sibling.get('class', []):
                                        break
                                else:
                                    break
                            if sub_sibling.name == next_tag:
                                if next_class:
                                    if next_class in sub_sibling.get('class', []):
                                        break
                                else:
                                    break
                        subchapter_elements.append(sub_sibling)
                        sub_sibling = sub_sibling.next_sibling

                    # 将子章节内容转换为新的 BeautifulSoup 对象
                    subchapter_soup = BeautifulSoup(''.join(str(e) for e in subchapter_elements), 'html.parser')

                    # 递归解析子章节
                    child_subsections = search_chapter(subchapter_soup, next_class, next_tag, child_hierarchy[1:])
                    if child_subsections:
                        child_sections.extend(child_subsections)
                    else:
                        # 如果没有更深的子章节，直接添加当前子章节
                        subchapter_title = sibling.get_text(strip=True)
                        sub_original_sections_bs4 = subchapter_soup.contents
                        sub_original_sections_text = [
                            element.get_text(strip=True) if isinstance(element, bs4.element.Tag) else str(
                                element).strip() for element in sub_original_sections_bs4]
                        child_sections.append({
                            "chapter_title": subchapter_title,
                            "original_sections_bs4": sub_original_sections_bs4,
                            "original_sections_text": sub_original_sections_text,
                            "sections": []
                        })

                    # 跳过已处理的子章节部分
                    sibling = sub_sibling
                    continue
                else:
                    # 非子章节内容，添加到 original_sections_bs4 和 original_sections_text
                    original_sections_bs4.append(sibling)
                    if isinstance(sibling, bs4.element.Tag):
                        text = sibling.get_text(strip=True)
                    else:
                        text = str(sibling).strip()
                    if text:
                        original_sections_text.append(text)
            else:
                # 非标签内容，如字符串或注释，直接添加
                original_sections_bs4.append(sibling)
                text = str(sibling).strip()
                if text:
                    original_sections_text.append(text)

            sibling = sibling.next_sibling

        # 构建当前章节的字典
        section_dict = {
            "chapter_title": chapter_title,
            "original_sections_bs4": original_sections_bs4,
            "original_sections_text": original_sections_text,
            "sections": child_sections
        }

        sections.append(section_dict)

    return sections


def epub_to_html(epub_book: epub.EpubBook):
    res = []
    for item in epub_book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        # 定义章节层级结构，依次为标签名和类名
        hierarchy = [
            ('h1', 'kindle-cn-heading-1'),
            ('h2', 'kindle-cn-heading2'),
            ('p', 'border'),
            # 根据需要添加更多层级
        ]

        # 开始递归解析
        chapters = search_chapter(soup, hierarchy[0][1], hierarchy[0][0], hierarchy[1:])
        res.extend(chapters)

    return res


if __name__ == "__main__":
    file_path = '/Users/yangtianrui/Downloads/epub/六韬 (中华经典名著全本全注全译丛书) by 陈曦.epub'
    book = load_epub_file(file_path)
    html_content = epub_to_html(book)
    print("rs")
