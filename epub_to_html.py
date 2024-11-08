import json
from ebooklib import epub
from bs4 import BeautifulSoup
import ebooklib

# epub_to_html.py
def epub_to_html(file_path: str, output_path: str) -> None:
    book = epub.read_epub(file_path)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(soup.prettify())


if __name__ == "__main__":
    epub_file = '/Users/yangtianrui/Downloads/需要仔细清洗的书籍/劝学篇 by 冯天瑜,姜海龙译注 [fengtianyu,jianghailongyizhu].epub'
    output_file = "output5.html"
    epub_to_html(epub_file, output_file)