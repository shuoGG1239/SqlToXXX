import codecs
import os
import re
import win32clipboard
import natsort

from shuogg import file_util

package_name = 'com.simba'
IS_SIMBA = True

GETTER_SETTER = """
    public {0} get{1}() {{
        return {2};
    }}

    public void set{1}({0} {2}) {{
        this.{2} = {2};
    }}
"""

TO_STRING_TEMPLATE = """
    @Override
    public String toString() {{
        return {}
    }}

"""

CLASS_COMMENT = """
/**
 * {}
 */
"""

FIELD_COMMENT = """
    /**
     * {}
     */
"""

CRLF = '\r\n'

DESC_ANNO = """@DescAnnotation(desc = "{}")
"""

TAB = '    '


def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        data = ''
        print('clipboard unknown error!!', e)
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


def insert_suffix(text, keyword, inserted_text):
    """
    在关键字后面插入文本 (从头算起的第1个关键字)
    :param text:
    :param keyword:
    :param inserted_text:
    :return: str: 插入后的结果
    """
    position = text.find(keyword)
    if position != -1:
        new_text = text[:position + len(keyword)] + inserted_text + text[position + len(keyword):]
        return new_text


def insert_prefix(text, keyword, inserted_text):
    """
    在关键字前面插入文本 (从头算起的第1个关键字)
    :param text:
    :param keyword:
    :param inserted_text:
    :return: str: 插入后的结果
    """
    position = text.find(keyword)
    if position != -1:
        new_text = text[:position] + inserted_text + text[position:]
        return new_text


def get_tables(sql_text):
    """
    sql文本转Table对象列表
    :param sql_text: sql文本
    :return: list of Table
    """
    tables = []
    ret = re.findall(r'(create\stable\s(.+)[^\(]+\(([^;]+)\);)', sql_text)
    for per_table_ret in ret:
        table_name = per_table_ret[1].replace('\r', '').replace('\n', '')
        table_body = per_table_ret[2]
        table_body_lines = list(map(lambda x: x.strip(), table_body.strip().splitlines()))
        new_table = Table()
        # 遍历( ... )里面的每一行
        key_names = []
        for line in table_body_lines:
            if 'primary key' in line:
                key_names.append(line[line.find('(') + 1:line.find(')')])
            if 'key ' not in line:
                ret_line = re.search(r'([\w_]+)\s+([^\s,]+)\s?(.*)', line)
                field_name = ret_line.group(1)
                field_type = ret_line.group(2)
                field_tail = ret_line.group(3)
                field_comment = '--'
                if 'comment ' in field_tail:
                    field_comment = re.search(r'[\w\s]+\'(.+)\'', line).group(1)
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
            r'alter\stable\s%s.+\'(.+)\'' % table_name.strip(), sql_text)
        if ret_comment is not None:
            table_comment = ret_comment.group(1)
        new_table.comment = table_comment
        new_table.name = table_name
        tables.append(new_table)
    return tables


def sql_to_beans(sql_text, save_dir='./'):
    """
    sql(可含多个表)转为javabeans并保存到指定目录(默认当前目录)
    :param sql_text: pdm的sql
    :param save_dir:
    :return:
    """
    table_list = get_tables(sql_text)
    for table in table_list:
        bean_str = table_to_bean(table)
        file_name = table.name[0].upper() + table.name[1:] + '.java'
        file_util.write_file_content(save_dir + file_name, bean_str)


def table_to_bean(table):
    """
    Table对象转为javaBean
    :param table: Table obj
    :return: javaBean text
    """
    # 生成package
    class_name = table.name[0].upper() + table.name[1:]
    package_line = 'package ' + package_name + '.model;\n'
    bean_content = package_line
    # 生成类注释
    bean_content += CLASS_COMMENT.format(table.comment)
    if IS_SIMBA:
        bean_content += DESC_ANNO.format(table.comment)
    bean_content += ('public class ' + class_name + ' {')
    # 生成private type fieldName
    typefield_list = []
    for field in table.fields:
        real_type = get_field_type(field.type)
        real_name = field.name[0].lower() + field.name[1:]
        typefield_list.append((real_type, real_name))
        bean_content += FIELD_COMMENT.format(field.comment)
        if IS_SIMBA:
            bean_content += (TAB + DESC_ANNO.format(field.comment))
        bean_content += (TAB + "private " + real_type + ' ' + real_name + ';\n')

    # 生成所有getter和setter
    bean_content += gen_getter_setter(typefield_list)
    # 生成toString
    bean_content += gen_tostring(class_name, typefield_list)
    bean_content += '}'
    # 生成import
    import_lines = '\n'
    if ' Date ' in bean_content:
        import_lines += 'import java.util.Date;\n\n'
    if IS_SIMBA:
        import_lines += 'import com.simba.annotation.DescAnnotation;\n'
    bean_content = insert_suffix(bean_content, package_line, import_lines)

    return bean_content


def gen_getter_setter(typefield_list):
    """
    生成并返回getter setter
    :param typefield_list: 字段类型+名的元组列表 eg:[(int,id), (String,name), (Date,createTime)]
    :return: str
    """
    getter_setter_list = []
    for type_field in typefield_list:
        gset = GETTER_SETTER.format(
            type_field[0], type_field[1][0].upper() + type_field[1][1:], type_field[1])
        getter_setter_list.append(gset)
    return "".join(getter_setter_list)


def gen_tostring(class_name, typefield_list):
    """
    生成并返回tostring
    :param class_name
    :param typefield_list: 字段类型+名的元组列表 eg:[(int,id), (String,name), (Date,createTime)]
    :return: str
    """
    tostring = '\"' + class_name + '{\" +\n'
    tostring += '\t\t\"' + \
                typefield_list[0][1] + '=\" + ' + typefield_list[0][1] + ' +\n'
    typefield_list_ext_first = typefield_list[1:]
    for type_field in typefield_list_ext_first:
        single_quote_left = r"'" if type_field[0] == 'String' else ""
        single_quote_right = r" + '\''" if type_field[0] == 'String' else ""
        tostring += '\t\t\", ' + type_field[1] + '=' + single_quote_left + '\" + ' + type_field[
            1] + single_quote_right + ' + \n'
    tostring += "\t\t\'}\';"
    return TO_STRING_TEMPLATE.format(tostring)


def get_field_type(sql_type):
    """
    sql的类型映射到java的类型
    :param sql_type:
    :return: str
    """
    sql_type = sql_type.lower()
    if 'varchar' in sql_type or 'text' == sql_type or 'char' in sql_type or 'binary' in sql_type or 'blob' in sql_type:
        return 'String'
    if 'bigint' in sql_type or 'fixed' in sql_type:
        return 'long'
    if sql_type == 'int' or 'integer' in sql_type or 'enum' in sql_type:
        return 'int'
    if sql_type == 'tinyint' or 'bit' in sql_type:
        return 'byte'
    if 'double' in sql_type or 'numeric' in sql_type or 'real' in sql_type or 'dec' in sql_type:
        return 'double'
    if 'float' in sql_type:
        return 'float'
    if 'date' in sql_type or 'time' in sql_type or 'year' in sql_type:
        return 'Date'
    if 'bool' in sql_type:
        return 'boolean'
    raise RuntimeError('Unknown sql type:' + sql_type)


def run_file_transfer():
    """
    对当前目录下的所有sql文件进行转换
    :return:
    """
    path_list = get_suffixfiles_fullpath('.sql')
    if len(path_list) > 0:
        for sql_file_path in path_list:
            sql_text = get_file_content(sql_file_path)
            sql_to_beans(sql_text)


if __name__ == '__main__':
    text = get_clipboard_text()
    if 'create table ' in text:
        # 直接对剪贴板的内容进行转换
        sql_to_beans(text)
    else:
        run_file_transfer()
