import codecs
import os

import natsort


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


def write_file_content_append(file_path, text, encoding='utf8'):
    """
    写文件-append模式
    :param file_path: str
    :param text: str
    :param encoding: str
    :return: None
    """
    try:
        with open(file_path, mode='ab') as f1:
            f1.write(text.encode(encoding=encoding))
    except Exception as e:
        print(e)


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
    return natsort.natsorted(all_fullpath)


def get_files_fullpath_curdir(suffix=''):
    """
    获取当前目录下所有.xxx文件的路径
    :param suffix: 后缀如".sql" ".java" ; 若不填则不进行文件过滤
    :return: list of str
    """
    return get_files_fullpath(os.getcwd(), suffix)
