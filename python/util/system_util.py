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


def open_with_chrome(file_path):
    chrome_path = r'D:\chrome_56_x64\Chrome-bin\chrome.exe'
    cmd = "%s %s" % (chrome_path, file_path)
    os.system(cmd)


def open_with_default_browser(file_path):
    cmd = "explorer %s" % (file_path)
    os.system(cmd)
