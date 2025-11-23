import os
import win32clipboard


def get_clipboard_text():
    """
    获取剪贴板的内容
    :return: str
    """
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        data = ''
        print('clipboard unknown error!!', e)
    return data


def set_clipboard_text(text):
    """
    设置剪贴板内容
    :param text:
    :return:
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()


def open_with_chrome(file_path):
    chrome_path = r'D:\chrome_56_x64\Chrome-bin\chrome.exe'
    cmd = "%s %s" % (chrome_path, file_path)
    os.system(cmd)


def open_with_default_browser(file_path):
    cmd = "explorer %s" % (file_path)
    os.system(cmd)
