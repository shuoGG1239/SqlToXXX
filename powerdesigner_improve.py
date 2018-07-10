import os
import codecs
import re
import sys

"""
    PowerDesigner输出的javabean优化:
        直接将该脚本跟.java放在同一个目录, 然后运行脚本即可. 优化后的.java文件放在model文件夹中

"""

annotation_enable = True
getter_setter_enable = True
tostring_enable = True

test_text = """
/***********************************************************************
 * Module:  Blacklist.java
 * Author:  linshuo
 * Purpose: Defines the Class Blacklist
 ***********************************************************************/

import java.util.*;

/** 异常名单，暂时用于拉黑反复发短信的
 *
 * @pdOid f91784d9-1581-4e82-88dc-65019d419193 */
public class Blacklist {
   /** @pdOid c6572728-1c8c-4519-8ca6-6c0cf1c44e02 */
   public int id;
   /** 手机号
    *
    * @pdOid 7fef1f1a-0dc9-4f64-9803-320624ac6b69 */
   public java.lang.String mobile;
   /** @pdOid 0c009c84-25f4-4d1f-bcd5-b9b963b1e8bb */
   public java.util.Date createTime;

}

"""

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

package_name = 'com.simba'


def mkdir_in_dir(dir_path, name):
    """
    当前dir_path目录下建一个文件夹
    :param name: 文件夹名称
    :return: 新建的文件夹的完整路径
    """
    new_directory = dir_path + '\\' + name + "\\"
    try:
        os.mkdir(dir_path + '\\' + name)
    except Exception as e:
        print(e)
    return new_directory


def quick_mkdir(name):
    """
    当前目录下建一个文件夹
    :param name: 文件夹名称
    :return: 新建的文件夹的完整路径
    """
    new_directory = os.getcwd() + '\\' + name + "\\"
    if not os.path.exists(new_directory):
        try:
            os.mkdir(os.getcwd() + '\\' + name)
        except Exception as e:
            print(e)
    return new_directory


def get_files_fullpath(dir_path, suffix=''):
    """
    获取dir_path目录下所有.xxx文件的路径
    :param suffix: 后缀如".sql" ".java" ; 若不填则不进行文件过滤
    :return: list of str
    """
    files = list(filter(lambda x: os.path.isfile(x), os.listdir(dir_path)))
    if suffix != '':
        # 留下后缀为suffix的文件
        files = list(filter(lambda x: x.endswith(suffix), files))
    all_fullpath = list(map(lambda x: os.getcwd() + '\\' + x, files))
    return all_fullpath


def get_files_fullpath_curdir(suffix=''):
    """
    获取当前目录下所有.xxx文件的路径
    :param suffix: 后缀如".sql" ".java" ; 若不填则不进行文件过滤
    :return: list of str
    """
    return get_files_fullpath(os.getcwd(), suffix)


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


def write_file_content(file_path, text, encoding='utf8'):
    """
    写文件
    :param file_path: str
    :param text: str
    :param encoding: str
    :return: None
    """
    try:
        with open(file_path, mode='wb') as f1:
            f1.write(text.encode(encoding=encoding))
    except Exception as e:
        print(e)


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
        new_text = text[:position + len(keyword)] + \
                   inserted_text + text[position + len(keyword):]
        return new_text
    else:
        return text


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
    else:
        return text


def del_next_line(text, keyword):
    """
    删除下一行
    :param text:
    :param keyword:
    :return: str: 删除行之后的结果 
    """
    position = text.find(keyword)
    if position != -1:
        text_pre = text[:position + len(keyword)]
        text_rear = text[position + len(keyword):]
        text_rear = text_rear[text_rear.find('\n') + 1:]
        return text_pre + text_rear[text_rear.find('\n'):]
    else:
        return text


def del_pre_line(text, keyword):
    """
    删除上一行
    :param text:
    :param keyword:
    :return: str: 删除行之后的结果
    """
    position = text.find(keyword)
    if position != -1:
        pos_line_head = text.rfind('\n', 0, position)
        pos_pre_line_head = text.rfind('\n', 0, pos_line_head)
        return text[0:pos_pre_line_head] + text[pos_line_head:]
    else:
        return text


def do_PD_improve(text):
    """
    对PowerDesigner输出的javabean进行优化
    :param text: str: 代码
    :return: str: 优化后的代码
    """
    # pd的tinyint==byte, 将byte替换为int
    text = text.replace(' byte ', ' int ')

    # 干掉注释中的乱码
    ret = re.sub(r"@(\w|\s|\-)+", '', text)

    # 加import注解类
    if annotation_enable is True:
        ret = insert_prefix(
            ret, 'import', 'import com.simba.annotation.DescAnnotation;\n')

    # 替换掉完整路径的类
    ret = ret.replace('java.lang.String', 'String')
    if ret.find('java.util.Date') == -1:
        ret = ret.replace('import java.util.*;', '')
    ret = ret.replace('java.util.Date', 'Date')

    # 把所有的字段的public替换为private PS:'\b'是单词边界
    ret = re.sub(r'\bpublic\b', 'private', ret)
    ret = re.sub(r"private\s+class", 'public class', ret)

    # 将注释的正文提取出来,如果没有正文,置为空字符串
    desc_list = re.findall(r'/\*\*\s(.+)', ret)
    desc_list = list(map(lambda x: x.strip(), desc_list))
    desc_list = list(map(lambda x: '' if x == '*/' else x, desc_list))

    # 在class上面加上 @DescAnnotation注解
    if annotation_enable is True:
        ret = insert_prefix(ret, 'public class',
                            '@DescAnnotation(desc = "' + desc_list[0] + '")\n')

    # 获得class类名
    class_name = re.findall(r'public class (\w+)', ret)[0]

    # 找出所有的成员变量行
    field_ret = re.findall(r"(private(\w|\s)+;)", ret)  # 返回的列表的每个元素都为元组
    field_line_list = list(map(lambda x: x[0], field_ret))

    # 在每行成员变量上加注释, 并将每行的变量名和变量类型抽取出来
    typefield_list = []
    for field_str, i in zip(field_line_list, range(len(field_line_list))):
        if annotation_enable is True:
            ret = insert_prefix(
                ret, field_str, '@DescAnnotation(desc = "' + desc_list[i + 1] + '")\n\t')
            if i < len(field_line_list) - 1:
                ret = insert_suffix(ret, field_str, '\n')
        pattern_ret = re.search(r'private\s(\w+)\s(\w+);', field_str)
        field_type = pattern_ret.group(1)
        field = pattern_ret.group(2)
        typefield_list.append((field_type, field))

    # 将注释的内容下移1行
    desc_list_1 = re.findall(r'(/\*\*\s(.+))', ret)
    class_line_str, class_content = desc_list_1[0]
    if class_content.find('*/') == -1:
        ret = del_next_line(ret, class_line_str)
        ret = insert_suffix(ret, class_line_str, '\n * ' + class_content)
    for line_str, content in desc_list_1[1:]:
        if content.find('*/') == -1:
            ret = del_next_line(ret, line_str)
            ret = insert_suffix(ret, line_str, '\n    * ' + content)
    # ret = re.sub(r'/\*\*\s.+(?<!\*/)', '/**', ret)
    ret = re.sub(r'/\*\*\s[^\*\n]+', '/**', ret)

    # 生成所有getter和setter
    getter_setter_list = []
    for type_field in typefield_list:
        gset = GETTER_SETTER.format(
            type_field[0], type_field[1][0].upper() + type_field[1][1:], type_field[1])
        getter_setter_list.append(gset)
    getter_setter_string = "".join(getter_setter_list)
    getter_setter_string = "" if getter_setter_enable is False else getter_setter_string

    # 生成toString
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
    tostring = TO_STRING_TEMPLATE.format(tostring)
    tostring = "" if tostring_enable is False else tostring

    # 在class最后的'}'前面插入所有的getter和setter以及toString
    ret = insert_prefix(ret, '}', getter_setter_string + tostring)

    # 加package包名
    ret = 'package ' + package_name + '.model;\n' + ret

    # 干掉id上注释和注解
    ret = del_pre_line(del_pre_line(ret, ' id;'), ' id;')

    return ret


def gen_beans_cur_dir():
    """
    将当前目录下的所有javaBean文件进行转换并保存在model文件夹下
    :return:
    """
    new_directory = quick_mkdir('model')
    for fullpath in get_files_fullpath_curdir('.java'):
        file_name = os.path.split(fullpath)[1]
        new_full_filepath = new_directory + file_name
        text = get_file_content(fullpath)
        write_file_content(new_full_filepath, do_PD_improve(text))


def gen_beans_in_dir(dir_path):
    """
    将dir_path目录下的所有javaBean文件进行转换并保存在dir_path/model文件夹下
    :return:
    """
    new_directory = mkdir_in_dir(dir_path, 'model')
    for fullpath in get_files_fullpath(dir_path, '.java'):
        file_name = os.path.split(fullpath)[1]
        new_full_filepath = new_directory + file_name
        text = get_file_content(fullpath)
        write_file_content(new_full_filepath, do_PD_improve(text))


def run_with_args():
    """
    加上windows的参数来运行
    :return: None
    """
    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]):
            gen_beans_in_dir(sys.argv[1])
        else:
            print('非文件夹不转换!')
            os.system('pause')  # 实现按任意键退出的效果
    else:
        try:
            gen_beans_cur_dir()
        except Exception as e:
            print('Translate Error')
        print("Translate complete!")


def run_with_cmd():
    """
    命令行模式运行
    """
    cmd = input('请输入包名(默认为com.simba):')
    if cmd != '':
        global package_name
        package_name = cmd
    try:
        gen_beans_cur_dir()
    except Exception as e:
        print('Translate Error')
    print("Translate complete!")
    # os.system('pause')


if __name__ == '__main__':
    run_with_cmd()
