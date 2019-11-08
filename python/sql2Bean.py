from util import sql_parser, text_util, file_util, system_util

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


def sql_to_beans(sql_text, save_dir='./'):
    """
    sql(可含多个表)转为javabeans并保存到指定目录(默认当前目录)
    :param sql_text: pdm的sql
    :param save_dir:
    :return:
    """
    table_list = sql_parser.get_tables(sql_text)
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
        real_type = sql_parser.get_field_type(field.type)
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
    bean_content = text_util.insert_suffix(bean_content, package_line, import_lines)

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


def run_file_transfer():
    """
    对当前目录下的所有sql文件进行转换
    :return:
    """
    path_list = file_util.get_files_fullpath_curdir('.sql')
    if len(path_list) > 0:
        for sql_file_path in path_list:
            sql_text = file_util.get_file_content(sql_file_path)
            sql_to_beans(sql_text)


if __name__ == '__main__':
    text = system_util.get_clipboard_text()
    if 'create table ' in text:
        # 直接对剪贴板的内容进行转换
        sql_to_beans(text)
    else:
        run_file_transfer()
