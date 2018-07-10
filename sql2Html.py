from bs4 import BeautifulSoup
from shuogg import file_util
import os
import codecs
import re
import natsort
import win32clipboard


def open_with_chrome(file_path):
    chrome_path = r'D:\chrome_56_x64\Chrome-bin\chrome.exe'
    cmd = "%s %s" % (chrome_path, file_path)
    os.system(cmd)


def open_with_default_browser(file_path):
    cmd = "explorer %s" % (file_path)
    os.system(cmd)


def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        data = ''
        print('clipboard unknown error!!',e)
    return data


class Field:
    def __init__(self, name='', type='', comment=''):
        self.name = name
        self.type = type
        self.comment = comment
        self.is_not_null = False
        self.is_key = False
        self.is_auto_increase = False

    def __repr__(self):
        return "Field(name=%s, type=%s, comment=%s)" % (self.name, self.type, self.comment)


class Table:
    def __init__(self):
        self.name = ''
        self.comment = ''
        self.fields = []

    def __repr__(self):
        return "Table(name=%s, comment=%s, field=%s)" % (self.name, self.comment, repr(self.fields))


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


def get_tables(sql_text):
    """
    sql文本转Table对象列表
    :param sql_text: sql文本
    :return: list of Table
    """
    tables = []
    ret = re.findall(r'(create\stable\s(.+)[^\(]+\(([^;]+)\);)', sql_text)
    for per_table_ret in ret:
        table_name = per_table_ret[1]
        table_body = per_table_ret[2]
        table_body_lines = list(
            map(lambda x: x.strip(), table_body.strip().splitlines()))
        new_table = Table()
        # 遍历( ... )里面的每一行
        for line in table_body_lines:
            key_names = []
            if 'primary key' in line:
                key_names.append(line[line.find('(') + 1:line.find(')')])
            if 'key ' not in line:
                ret_line = re.search(r'([\w_]+)\s+([^\s,]+)\s?(.*)', line)
                field_name = ret_line.group(1)
                field_type = ret_line.group(2)
                field_tail = ret_line.group(3)
                field_comment = '--'
                if 'comment ' in field_tail:
                    field_comment = re.search(
                        r'[\w\s]+\'(.+)\'', line).group(1)
                new_field = Field(field_name, field_type, field_comment)
                if 'not null' in line:
                    new_field.is_not_null = True
                if 'auto_increment' in line:
                    new_field.is_auto_increase = True
                new_table.fields.append(new_field)
        # 处理primary key
        for per_field in new_table.fields:
            if per_field.name in key_names:
                per_field.is_key = True
        table_comment = 'null'
        ret_comment = re.search(
            r'alter\stable\s%s.+\'(.+)\'' % table_name, sql_text)
        if ret_comment is not None:
            table_comment = ret_comment.group(1)
        new_table.comment = table_comment
        new_table.name = table_name
        tables.append(new_table)
    return tables


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
    table_list = get_tables(sql_text)
    soup = BeautifulSoup(HTML, 'lxml')
    # 遍历数据表
    for table in table_list:
        table1 = soup.new_tag(name='table')
        # 标题行
        tr_head = soup.new_tag(name='tr')
        td_head = soup.new_tag(name='th', colspan="3")
        td_head.append(table.name)
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
    open_with_default_browser(full_path)


def run_file_transfer():
    path_list = get_suffixfiles_fullpath('.sql')
    if len(path_list) > 0:
        for sql_file_path in path_list:
            sql_text = get_file_content(sql_file_path)
            sql_to_html(sql_text)


if __name__ == '__main__':
    text = get_clipboard_text()
    if 'create table ' in text:
        # 直接对剪贴板的内容进行转换
        sql_to_html(text)
    else:
        run_file_transfer()
