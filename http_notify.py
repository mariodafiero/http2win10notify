import json
import time

import win32con  # requires pywin32, http://sourceforge.net/projects/pywin32/
from flask import Flask, request
from win32api import *
from win32gui import *

showmsgfor = 5  # display message for x seconds.

# Class
class WindowsBalloonTip:
    def __init__(self):
        message_map = {win32con.WM_DESTROY: self.OnDestroy, }

        # Register the window class.
        wc = WNDCLASS()
        self.hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = 'PythonTaskbar'
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        self.classAtom = RegisterClass(wc)

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)

    def balloon_tip(self, title, msg):
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        hwnd = CreateWindow(self.classAtom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0,
                            0, self.hinst, None)
        UpdateWindow(hwnd)

        hicon = LoadIcon(0, win32con.IDI_APPLICATION)

        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (hwnd, 0, flags, win32con.WM_USER + 20, hicon, 'Tooltip')
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (
            hwnd, 0, NIF_INFO, win32con.WM_USER + 20, hicon, 'Balloon Tooltip', msg, 7000, title, NIIF_INFO))

        # crude way of doing this... to fix.
        time.sleep(showmsgfor)  # display message

        # dismiss message
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0)


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        data = request.get_json()
       
        try:
            # requires a json message to be sent {"sub":"subject","txt":"text"}
            # jsonmsg = json.loads(msg.payload)
            # w.balloon_tip(jsonmsg['sub'], jsonmsg['txt'])
            w.balloon_tip("Message", data)
        except:
            # fallback to just displaying the text if no JSON message found.
            w.balloon_tip('mqtt notification', "error")

        print('Value ', data)
        return 'OK'
    else:
        return 'Use POST requests'


w = WindowsBalloonTip()

if __name__ == '__main__':
    # app.debug = True
    i = 0

    app.run(host='0.0.0.0', port=8555)
