#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼠标范围限制工具

功能：
- 点击“框选范围”按钮后在屏幕上拖拽选取矩形
- 选区设置完成后，按 F7 开始限制鼠标只能在该范围内
- 按 F8 停止限制
- 默认热键可修改
- 框选时显示选区提示线，完成后不弹出提示框
"""

import ctypes
from ctypes import wintypes
import time
import sys
import tkinter as tk
from tkinter import ttk

try:
    import win32api
    import win32con
    import win32gui
    import keyboard
except Exception as e:
    print('缺少依赖或导入失败:', e)
    print('请先运行: python -m pip install -r requirements.txt')
    sys.exit(1)

user32 = ctypes.windll.user32


class MouseRangeApp:
    def __init__(self, root):
        self.root = root
        root.title('鼠标范围限制')
        root.resizable(False, False)

        self.region = None
        self.restricting = False

        self.start_hotkey = tk.StringVar(value='F7')
        self.stop_hotkey = tk.StringVar(value='F8')
        self.status_var = tk.StringVar(value='默认范围已加载，按 F7 开始')
        self.region_var = tk.StringVar(value='177,48 - 2334,1392')
        self.left_var = tk.StringVar(value='177')
        self.top_var = tk.StringVar(value='48')
        self.right_var = tk.StringVar(value='2334')
        self.bottom_var = tk.StringVar(value='1392')

        frm = ttk.Frame(root, padding=12)
        frm.grid()

        ttk.Button(frm, text='框选范围', command=self._select_region).grid(column=0, row=0, columnspan=2, pady=(0, 10), sticky='ew')

        ttk.Label(frm, text='手动输入范围:').grid(column=0, row=1, sticky='w', pady=(0, 4), columnspan=2)
        ttk.Label(frm, text='Left').grid(column=0, row=2, sticky='e', padx=(0, 4))
        ttk.Entry(frm, textvariable=self.left_var, width=8).grid(column=1, row=2, sticky='w')
        ttk.Label(frm, text='Top').grid(column=0, row=3, sticky='e', padx=(0, 4), pady=(4, 0))
        ttk.Entry(frm, textvariable=self.top_var, width=8).grid(column=1, row=3, sticky='w', pady=(4, 0))
        ttk.Label(frm, text='Right').grid(column=0, row=4, sticky='e', padx=(0, 4), pady=(4, 0))
        ttk.Entry(frm, textvariable=self.right_var, width=8).grid(column=1, row=4, sticky='w', pady=(4, 0))
        ttk.Label(frm, text='Bottom').grid(column=0, row=5, sticky='e', padx=(0, 4), pady=(4, 0))
        ttk.Entry(frm, textvariable=self.bottom_var, width=8).grid(column=1, row=5, sticky='w', pady=(4, 0))
        ttk.Button(frm, text='设置范围', command=self._apply_manual_region).grid(column=0, row=6, columnspan=2, pady=(6, 10), sticky='ew')

        ttk.Label(frm, text='开始热键:').grid(column=0, row=7, sticky='e', padx=(0, 4))
        ttk.Entry(frm, textvariable=self.start_hotkey, width=12).grid(column=1, row=7, sticky='w')
        ttk.Label(frm, text='结束热键:').grid(column=0, row=8, sticky='e', padx=(0, 4), pady=(4, 0))
        ttk.Entry(frm, textvariable=self.stop_hotkey, width=12).grid(column=1, row=8, sticky='w', pady=(4, 0))

        ttk.Label(frm, text='当前范围:').grid(column=0, row=9, sticky='e', padx=(0, 4), pady=(10, 0))
        ttk.Label(frm, textvariable=self.region_var).grid(column=1, row=9, sticky='w', pady=(10, 0))

        ttk.Label(frm, text='状态:').grid(column=0, row=10, sticky='e', padx=(0, 4), pady=(4, 0))
        ttk.Label(frm, textvariable=self.status_var).grid(column=1, row=10, sticky='w', pady=(4, 0))

        ttk.Button(frm, text='开始限制', command=self.start).grid(column=0, row=11, pady=(10, 0), sticky='ew')
        ttk.Button(frm, text='停止限制', command=self.stop).grid(column=1, row=11, pady=(10, 0), sticky='ew')

        self.start_hotkey.trace_add('write', lambda *args: self._apply_hotkeys())
        self.stop_hotkey.trace_add('write', lambda *args: self._apply_hotkeys())

        self._registered_start = None
        self._registered_stop = None
        self._apply_hotkeys()
        self._set_region((177, 48, 2334, 1392))

    def _apply_hotkeys(self):
        if self._registered_start is not None:
            keyboard.remove_hotkey(self._registered_start)
            self._registered_start = None
        if self._registered_stop is not None:
            keyboard.remove_hotkey(self._registered_stop)
            self._registered_stop = None

        try:
            self._registered_start = keyboard.add_hotkey(self.start_hotkey.get(), self.start)
            self._registered_stop = keyboard.add_hotkey(self.stop_hotkey.get(), self.stop)
            self.status_var.set(f'热键已生效: {self.start_hotkey.get()} / {self.stop_hotkey.get()}')
        except Exception as e:
            self.status_var.set(f'热键注册失败: {e}')

    def _draw_focus_rect(self, rect, dc):
        if not rect:
            return
        left, top, right, bottom = rect
        try:
            win32gui.DrawFocusRect(dc, (left, top, right, bottom))
        except Exception:
            pass

    def _select_region(self):
        self.status_var.set('框选中...')
        self.root.update()

        while not (win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000):
            time.sleep(0.01)

        x1, y1 = win32api.GetCursorPos()
        prev_rect = None
        dc = win32gui.GetDC(0)

        try:
            while win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                x2, y2 = win32api.GetCursorPos()
                rect = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                if prev_rect:
                    self._draw_focus_rect(prev_rect, dc)
                self._draw_focus_rect(rect, dc)
                prev_rect = rect
                time.sleep(0.01)
            if prev_rect:
                self._draw_focus_rect(prev_rect, dc)
        finally:
            win32gui.ReleaseDC(0, dc)

        self._set_region(rect)

    def _apply_manual_region(self):
        try:
            left = int(self.left_var.get())
            top = int(self.top_var.get())
            right = int(self.right_var.get())
            bottom = int(self.bottom_var.get())
        except ValueError:
            self.status_var.set('手动范围坐标必须为整数')
            return

        rect = (min(left, right), min(top, bottom), max(left, right), max(top, bottom))
        self._set_region(rect)

    def _set_region(self, rect):
        if rect and rect[2] > rect[0] and rect[3] > rect[1]:
            self.region = rect
            self.region_var.set(f'{rect[0]},{rect[1]} - {rect[2]},{rect[3]}')
            self.left_var.set(str(rect[0]))
            self.top_var.set(str(rect[1]))
            self.right_var.set(str(rect[2]))
            self.bottom_var.set(str(rect[3]))
            self.status_var.set('范围已设置，按热键开始/停止')
        else:
            self.region = None
            self.region_var.set('无')
            self.status_var.set('范围设置失败，请重试')

    class RECT(ctypes.Structure):
        _fields_ = [
            ('left', wintypes.LONG),
            ('top', wintypes.LONG),
            ('right', wintypes.LONG),
            ('bottom', wintypes.LONG),
        ]

    def start(self):
        if not self.region:
            self.status_var.set('请先框选范围')
            return
        try:
            rect = self.RECT(*self.region)
            if not user32.ClipCursor(ctypes.byref(rect)):
                raise OSError('ClipCursor failed')
            self.status_var.set('已开始限制，按结束热键停止')
        except Exception as e:
            self.status_var.set(f'开始限制失败: {e}')

    def stop(self):
        try:
            if not user32.ClipCursor(None):
                raise OSError('ClipCursor release failed')
            self.status_var.set('已停止限制')
        except Exception as e:
            self.status_var.set(f'停止限制失败: {e}')

    def shutdown(self):
        try:
            user32.ClipCursor(None)
        except Exception:
            pass
        if self._registered_start is not None:
            keyboard.remove_hotkey(self._registered_start)
        if self._registered_stop is not None:
            keyboard.remove_hotkey(self._registered_stop)


def main():
    root = tk.Tk()
    app = MouseRangeApp(root)
    root.protocol('WM_DELETE_WINDOW', lambda: (app.shutdown(), root.destroy()))
    root.mainloop()


if __name__ == '__main__':
    main()
