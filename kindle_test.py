import json
from ebooklib import epub
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import ebooklib
import re

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

def search_chapter(chapters, chapter_title,chapter_title_type):
    sections = chapters.find_all(chapter_title_type, class_=chapter_title)
    if not sections:
        return {
            "chapter_title": "Unknown Chapter",
            "sections": []
        }
    sections_name = sections[0].get_text()
    # 存储分段内容的列表
    soup_sections = []

    for idx, section in enumerate(sections):
        content = []
        for sibling in section.find_next_siblings():
            if sibling.name == chapter_title_type and sibling.get('class') == [chapter_title]:
                break
            content.append(sibling)

        # 将当前标签及后续内容封装为一个新的 BeautifulSoup 对象
        new_soup = BeautifulSoup(str(section) + ''.join(str(c) for c in content), 'html.parser')
        soup_sections.append(new_soup)
    res = {
        "chapter_title": sections_name,
        "sections": soup_sections
    }
    return res


def epub_to_html(epub_book: epub.EpubBook):
    # 返回一个 BeautifulSoup 对象或者是html字符串
    res=[]
    for item in epub_book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        # 以 <h2> 标签为分割点
        h1_chapter = search_chapter(soup, 'kindle-cn-heading-1', 'h1')
        if h1_chapter['chapter_title'] != 'Unknown Chapter':
            for section in h1_chapter['sections']:
                h2_chapter = search_chapter(section, 'kindle-cn-heading-2', 'h2')
                res.append(h2_chapter)
        # res.append(soup_sections)
    return res





if __name__ == "__main__":
    file_path = '/Users/yangtianrui/Downloads/epub/六韬 (中华经典名著全本全注全译丛书) by 陈曦.epub'
    book = load_epub_file(file_path)
    html_content = epub_to_html(book)
    print("rs")