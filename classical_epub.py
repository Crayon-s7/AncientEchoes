import os
import json
import re

from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup

def convert_epub_to_html(epub_path):
    try:
        book = epub.read_epub(epub_path)
        html_files = []

        for item in book.items:
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                html_files.append(item.get_content().decode('utf-8'))

        return html_files
    except Exception as e:
        print(f"Error: {e}")
        return None

def classify_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 使用正则表达式匹配类名中包含kindle或calibre的标记
    kindle_pattern = re.compile(r'kindle', re.IGNORECASE)
    calibre_pattern = re.compile(r'calibre\d*', re.IGNORECASE)

    for class_name in soup.find_all(class_=True):
        classes = class_name.get('class', [])
        if any(kindle_pattern.search(cls) for cls in classes):
            return 'kindle'
        if any(calibre_pattern.search(cls) for cls in classes):
            return 'calibre'

    return '其他'

def process_epub_files(epub_dir, output_json):
    result = []
    result_dict = {}

    for file_name in os.listdir(epub_dir):
        if file_name.endswith('.epub'):
            file_path = os.path.join(epub_dir, file_name)
            html_contents = convert_epub_to_html(file_path)
            classification = '其他'
            if html_contents is None:
                result.append({'filename': file_name, 'classification': classification})
                result_dict[file_name] = classification
                continue

            for html_content in html_contents:
                classification = classify_html(html_content)
                if classification in ['kindle', 'calibre']:
                    break  # 优先选定kindle或calibre分类

            result.append({'filename': file_name, 'classification': classification})
            result_dict[file_name] = classification

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(f"分类结果已保存到 {output_json}")

    output_json_name_2 = output_json.split(".")[0] + "_dict.json"
    with open(output_json_name_2, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)


# 调用函数
epub_directory = '/Users/yangtianrui/Downloads/epub'  # 替换为EPUB文件夹路径
output_file = 'classification_results.json'  # 结果保存文件
process_epub_files(epub_directory, output_file)