import os
import re
import zipfile
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def txt2epub(epub_path, txt_path, book_name, author):
    """
    将txt文件转换为epub文件
    :param epub_path: epub文件保存路径
    :param txt_path: txt文件路径
    :param book_name: 书名
    :param author: 作者
    :return:
    """
    if os.path.exists(txt_path):
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            regex = r"^\s*([第卷][0123456789一二三四五六七八九十零百千万两]*[章回部节集卷].*)\s*"
            splits = re.split(regex, content, flags=re.M)
            items = [(splits[i], splits[i + 1]) for i in range(1, len(splits) - 1, 2)]

            if len(items) > 0:
                # 设置模板加载器
                template_dir = os.path.abspath('templates')
                tmp_loader = FileSystemLoader(template_dir)
                tmp_env = Environment(loader=tmp_loader)

                # 初始化EPUB文件
                book = zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED)

                # 写入mimetype（需单独处理，不压缩）
                book.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)

                # 写入META-INF/container.xml
                container_xml = (
                    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                    '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>'
                    '</container>'
                )
                book.writestr('META-INF/container.xml', container_xml)

                # 生成并写入content.opf
                opf_template = tmp_env.get_template('content.opf')
                now = datetime.now().isoformat()
                content_opf = opf_template.render(items=items, book_name=book_name, author=author, date=now)
                book.writestr('OEBPS/content.opf', content_opf)

                # 生成并写入章节内容（使用writestr方法）
                for index, (title, content) in enumerate(items, start=1):
                    part_template = tmp_env.get_template('part.html')
                    part_html = part_template.render(title=title, content=content, book_name=book_name, author=author, index=index)
                    book.writestr(f'OEBPS/text/chap{index}.html', part_html, compress_type=zipfile.ZIP_DEFLATED)

                # 生成并写入toc.ncx
                ncx_template = tmp_env.get_template('toc.ncx')
                toc_ncx = ncx_template.render(items=items, book_name=book_name)
                book.writestr('OEBPS/toc.ncx', toc_ncx)

                # 写入CSS样式
                book.write(os.path.join(template_dir, 'style.css'), 'OEBPS/style.css')

                book.close()
            else:
                print("未检测到有效的章节内容")
    else:
        print("文件不存在")



if __name__ == '__main__':
    txt2epub(epub_path='', txt_path='', book_name='', author='')