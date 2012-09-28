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
    import win32clipboard
    import win32api
    """Get win32 clipboard text data"""
    data = ""
    win32clipboard.OpenClipboard(0)
    try:
        cf = win32clipboard.CF_UNICODETEXT
        if not win32clipboard.IsClipboardFormatAvailable(cf):
            cf = win32clipboard.CF_TEXT
        data = win32clipboard.GetClipboardData(cf)
        idx_null = data.find('\x00')
        if idx_null > 0:
            data = data[:idx_null]
    except win32api.error, e:
        print("**Error: {}".format(e.message))
    win32clipboard.CloseClipboard()
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
    video_lixian.main()

if __name__ == '__main__':
    main()

