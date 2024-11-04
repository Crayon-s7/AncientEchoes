import ebooklib
import re
import json
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from ebooklib import epub
from utils import *
import os

class Book:
    def __init__(self, name, content_src=None, parent=None):
        self.name = name
        self.content_src = content_src
        self.chapters = []
        self.parent = parent
        self.index = 0
        self.notes = [] # 注释
        self.explanation = "" # 题解
        self.original_texts = [] # 原文
        self.translations = [] # 译文
        self.marked_notes = [] # 标记的文本

    def add_chapter(self, chapter_node):
        chapter_node.parent = self
        chapter_node.index = len(self.chapters)
        self.chapters.append(chapter_node)


    def get_structural_result(self, content):
        path = self.get_full_name()
        chapter_text = self.get_content(content)
        chapter_text = self.get_content(content)

        chapter_text = merge_same_tags(chapter_text)
        explanation_pattern = re.compile(r'<p class="kindle-cn-para-no-indent">【题解】</p>\s*<p>(.*?)</p>', re.DOTALL)
        original_pattern = re.compile(r'<p class="kindle-cn-para-no-indent">【原文】</p>\s*<p>(.*?)</p>', re.DOTALL)
        translation_pattern = re.compile(r'<p class="kindle-cn-para-no-indent">【译文】</p>\s*<p>(.*?)</p>', re.DOTALL)
        notes_pattern = re.compile(r'<p class="kindle-cn-para-no-indent">【注释】</p>\s*<p>(.*?)</p>', re.DOTALL)
        marked_pattern = re.compile(r'〔\d+〕([^：〔〕]+)：', re.DOTALL)

        explanation = parse_merged_html(chapter_text, explanation_pattern)
        original_texts = parse_merged_html(chapter_text, original_pattern)
        translations = parse_merged_html(chapter_text, translation_pattern)
        notes = parse_merged_html(chapter_text, notes_pattern)

        marked_notes, explanation_notes, original_texts = parse_notes(notes, original_texts, marked_pattern)

        self.marked_notes = marked_notes
        self.notes = explanation_notes
        self.original_texts = original_texts
        self.translations = translations
        self.explanation = explanation

        print("Parsed", self.name, "with", len(self.translations), "original", len(self.original_texts), len(self.explanation))
        file_path = os.path.join('results', path.split("_")[0], path + ".json")
        self.save_to_json(file_path)
        print("Saved to", file_path)




    def traverse(self, content):
        if self.content_src is None:
            file_name = self.name
            path = os.path.join('results', file_name)

            if not os.path.exists(path):
                os.makedirs(path)

        if not classify_chapter(self.name):
            return []
        
        if len(self.chapters) == 0:
            self.get_structural_result(content)

        for chapter in self.chapters:
            chapter.traverse(content)

    def count_leaf_nodes(self):
        if not self.chapters:
            return 1
        return sum(chapter.count_leaf_nodes() for chapter in self.chapters)
    
    def get_content(self, book, content_src=None):

        if self.chapters:
            raise ValueError("This is not a leaf node")
        
        if self.content_src is None:
            raise ValueError("Content source is None")
        
        if content_src is None:
            content_src = self.content_src.split("#")
        else:
            content_src = content_src.split("#")

        file_name = content_src[0]
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                if item.get_name() == file_name:
                    html_content = item.get_body_content()
                    html_string = html_content.decode('utf-8')

        if len(content_src) == 1:
            anchor = None
            start_index = 0
        else:
            anchor = content_src[1]
            pattern = r'<[^>]* id="{}"[^>]*>'.format(re.escape(anchor))
            match = re.search(pattern, html_string)
            if match:
                start_index = match.start()

        if len(self.parent.chapters) == 1:
            return html_string
        
        if len(self.parent.chapters) == self.index + 1:
            if anchor is None:
                return html_string
            else:
                return html_string[start_index:]
        
        next_node = self.parent.chapters[self.index + 1]
        next_node_content_src = next_node.content_src
        next_node_content_src = next_node_content_src.split("#")
        next_node_file_name = next_node_content_src[0]
        next_node_anchor = next_node_content_src[1] if len(next_node_content_src) == 2 else None

        if next_node_file_name == file_name:
            if next_node_anchor is None:
                return html_string[start_index:]
            else:
                pattern = r'<[^>]* id="{}"[^>]*>'.format(re.escape(next_node_anchor))
                match = re.search(pattern, html_string)
                if match:
                    end_index = match.start()
                    return html_string[start_index:end_index]
        else:
            return html_string[start_index:]

    def save_to_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)


    def get_full_name(self):
        if self.parent is None:
            return self.name
        else:
            return self.parent.get_full_name() + "_" + self.name

    def to_dict(self):
        return {
            "name": self.get_full_name(),
            "explanation": self.explanation,
            "original_texts": self.original_texts,
            "translations": self.translations,
            "marked_notes": self.marked_notes,
            "notes": self.notes
        }
    
    def __str__(self, level=0):
        indent = "  " * level
        ret = f"{indent}{self.name}: {self.content_src}\n"
        for chapter in self.chapters:
            ret += chapter.__str__(level + 1)
        return ret


def parse_book(book_path):
    book_content = epub.read_epub(book_path)
    name = book_path.split("\\")[-1].split(".")[0]
    nav_items = book_content.get_items_of_type(ebooklib.ITEM_NAVIGATION)
    nav_item = next(nav_items)
    soup = BeautifulSoup(nav_item.get_content(), 'xml')
    text = str(soup)
    namespace = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    # 解析XML内容
    root = ET.fromstring(text)

    # 提取目录结构
    nav_map = root.find('ncx:navMap', namespace)
    
    def process_nav_points(nav_point, level=0):
        nav_label = nav_point.find('ncx:navLabel/ncx:text', namespace).text
        content_src = nav_point.find('ncx:content', namespace).get('src')
        node = Book(nav_label, content_src)
        
        # 递归处理子navPoint
        for child_nav_point in nav_point.findall('ncx:navPoint', namespace):
            child_node = process_nav_points(child_nav_point, level + 1)
            node.add_chapter(child_node)
        
        return node

    # 处理navMap中的所有navPoint
    book = Book(name)
    for nav_point in nav_map.findall('ncx:navPoint', namespace):
        child_node = process_nav_points(nav_point)
        book.add_chapter(child_node)
    
    return book, book_content