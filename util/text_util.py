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
    else:
        raise RuntimeError('keyword not in text')


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
        raise RuntimeError('keyword not in text')


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
        raise RuntimeError('keyword not in text')


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
        raise RuntimeError('keyword not in text')
