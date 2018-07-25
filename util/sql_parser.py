import re


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


def get_tables(sql_text):
    """
    sql文本转Table对象列表
    :param sql_text: sql文本
    :return: list of Table
    """
    tables = []
    ret = re.findall(r'(create\stable\s(.+)[^(]+\(([^;]+)\);)', sql_text)
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
