#!/usr/bin/python
# vim:fileencoding=utf-8:sw=4:et
"""
Use win32 clipboard content as video url
"""

from __future__ import print_function, unicode_literals, absolute_import
import sys
import os
import io
import logging as log

def get_clipboard_text():
    """Get win32 clipboard text data"""
    data = ""

    CF_UNICODETEXT = 13
    CF_TEXT = 1

    import ctypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalLock.restype = ctypes.c_wchar_p # lock & copy memory

    cf = CF_UNICODETEXT
    if not user32.IsClipboardFormatAvailable(cf):
        cf = CF_TEXT

    user32.OpenClipboard(None)
    pcontent = user32.GetClipboardData(cf)
    if pcontent:
        data = kernel32.GlobalLock(pcontent)
        kernel32.GlobalUnlock(pcontent)
        idx_null = data.find('\x00')
        if idx_null > 0:
            data = data[:idx_null]
    user32.CloseClipboard()

    return data

def main():
    log_level = log.INFO
    log.basicConfig(format="%(levelname)s>> %(message)s", level=log_level)

    # check if an url is available
    url_flag = False
    for arg in sys.argv:
        if arg in {"-h", "--help"}:
            url_flag = True
            break
        if arg.startswith("http"):
            url_flag = True
            break

    if not url_flag:
        data = get_clipboard_text().strip()
        if data.startswith("http"):
            print(data)
            sys.argv.append(data)
        else:
            print("** You need to copy a video url to the clipboard...")

    import video_lixian
    try:
        video_lixian.main()
    except Exception, e:
        print("** Err: {}".format(e.message))

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()

