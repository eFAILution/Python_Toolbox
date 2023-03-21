# -*- coding: utf-8 -*-
import ctypes
import os

operating_sys = os.name


class styles:
    ok = 0
    ok_cancel = 1
    abort_retry_ignore = 2
    yes_no_cancel = 3
    yes_no = 4
    retry_cancel = 5
    cancel_tryAgain_continue = 6


class icon:
    STOP = 16
    QUESTION = 32
    EXCLAMATION = 48
    INFO = 64


class resp:  # return codes based on button clicked
    IDOK = 1
    IDCANCEL = 2
    IDABORT = 3
    IDRETRY = 4
    IDIGNORE = 5
    IDYES = 6
    IDNO = 7
    IDTRYAGAIN = 10
    IDCONTINUE = 11


def show_msg(message, title, style=0, icon=0, ontop=False):
    # TODO Support other operating systems
    # Can always use ipywidgets HTML DISPLAY to run javascript alert,
    # but not sure how to get back what button the user clicked
    if operating_sys == 'nt':  # Windows OS
        if ontop:
            style = style+0x40000
        return ctypes.windll.user32.MessageBoxW(
            0, message, title, style+icon)
