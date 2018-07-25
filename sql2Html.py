import codecs
import os

import natsort
from bs4 import BeautifulSoup

from util import sql_parser, file_util, system_util


def get_suffixfiles_fullpath(suffix):
    """
    获取当前目录下所有.xxx文件的路径 (路径列表自然排序)
    :param suffix: 后缀如".sql" ".java"
    :return: list of str
    """
    sql_files = list(filter(lambda x: x.endswith(
        suffix), os.listdir(os.getcwd())))
    sqlFilesFullPath = list(map(lambda x: os.getcwd() + '\\' + x, sql_files))
    return natsort.natsorted(sqlFilesFullPath)


def get_file_content(file_path):
    """
    读取文件, 暂时只支持utf8和gbk编码的文件, 自动去除BOM
    :param file_path:
    :return: str
    """
    try:
        with open(file_path, encoding='utf-8') as f1:
            raw = f1.read()
            # 去掉BOM
            bom_head = raw.encode(encoding='utf-8')[:3]
            if bom_head == codecs.BOM_UTF8:
                raw = raw.encode(encoding='utf-8')[3:].decode(encoding='utf-8')
            return raw
    except Exception as e:
        with open(file_path, encoding='GBK') as f2:
            return f2.read()


HTML_FILE_NAME = 'pwd_show.html'

CSS = """
    th {
        background-color: rgb(81, 130, 187);
        color: #fff;
        border-bottom-width: 0;
    }
    td {
        color: #000;
    }
    tr, th {
        border-width: 1px;
        border-style: solid;
        border-color: rgb(81, 130, 187);
    }
    td, th {
        padding: 5px 10px;
        font-size: 12px;
        font-family: Verdana;
        font-weight: bold;
    }
    table {
        border-width: 1px;
        border-collapse: collapse;
        float: left;
        margin: 10px;
    }
"""

HTML = """
<html><head><title>PdmShow</title><style>%s</style></head><body></body></html>
""" % CSS


def sql_to_html(sql_text):
    table_list = sql_parser.get_tables(sql_text)
    soup = BeautifulSoup(HTML, 'lxml')
    # 遍历数据表
    for table in table_list:
        table1 = soup.new_tag(name='table')
        # 标题行
        tr_head = soup.new_tag(name='tr')
        td_head = soup.new_tag(name='th', colspan="3")
        td_head.append(table.name + '(' + table.comment + ')')
        tr_head.append(td_head)
        table1.append(tr_head)
        # field行
        for field in table.fields:
            tr_field = soup.new_tag(name='tr')
            td_name = soup.new_tag(name='td')
            td_name.append(field.name)
            td_type = soup.new_tag(name='td')
            td_type.append(field.type)
            td_comment = soup.new_tag(name='td')
            td_comment.append(field.comment)
            tr_field.append(td_name)
            tr_field.append(td_type)
            tr_field.append(td_comment)
            table1.append(tr_field)
        soup.body.append(table1)
    result_html = soup.prettify()
    file_util.write_file_content(HTML_FILE_NAME, result_html)
    full_path = os.path.join(os.getcwd(), HTML_FILE_NAME)
    system_util.open_with_default_browser(full_path)


def run_file_transfer():
    path_list = get_suffixfiles_fullpath('.sql')
    if len(path_list) > 0:
        for sql_file_path in path_list:
            sql_text = get_file_content(sql_file_path)
            sql_to_html(sql_text)


if __name__ == '__main__':
    text = system_util.get_clipboard_text()
    if 'create table ' in text:
        # 直接对剪贴板的内容进行转换
        sql_to_html(text)
    else:
        run_file_transfer()
