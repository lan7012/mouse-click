#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI 自动点击器（Windows）

提供按钮：绑定进程（输入进程名或 PID）、单击/拖拽识别进程、在窗口上拖拽选取点击区域、开始/停止点击、退出。

依赖：pyautogui, psutil, pywin32, keyboard
"""

import threading
import time
import random
import sys
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import psutil
    import pyautogui
    import win32gui
    import win32process
    import win32api
    import win32con
    import keyboard
except Exception as e:
    print("缺少依赖或导入失败:", e)
    print("请先运行: python -m pip install -r requirements.txt")
    sys.exit(1)


def find_pid_by_name(name):
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"].lower() == name.lower():
                return proc.info["pid"]
        except Exception:
            continue
    return None


def find_hwnds_by_pid(pid):
    hwnds = []

    def callback(hwnd, extra):
        try:
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        except Exception:
            return True
        if found_pid == pid and win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)
        return True

    win32gui.EnumWindows(callback, None)
    return hwnds


def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)


class AutoClicker:
    def __init__(self):
        self.hwnd = None
        self.region = None
        self.min_delay = 0.001
        self.max_delay = 0.001
        self.button = 'left'
        self.background_mode = False

        self._running = False
        self._stop = False
        self._thread = None

    def set_target(self, hwnd, region=None):
        self.hwnd = hwnd
        if region is not None:
            self.region = region
        elif self.region is None:
            self.region = None

    def _random_point(self):
        if not self.hwnd:
            return None
        left, top, right, bottom = get_window_rect(self.hwnd)
        if self.region:
            rx, ry, rw, rh = self.region
            x = left + rx + random.randint(0, max(0, rw - 1))
            y = top + ry + random.randint(0, max(0, rh - 1))
        else:
            x = left + random.randint(0, max(0, right - left - 1))
            y = top + random.randint(0, max(0, bottom - top - 1))
        return x, y

    def _click_loop(self):
        while not self._stop:
            if not self._running:
                time.sleep(0.05)
                continue
            try:
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception:
                pass
            pt = self._random_point()
            if pt:
                x, y = pt
                if self.background_mode:
                    # send background click to window without moving mouse
                    try:
                        lx = int(x - win32gui.GetWindowRect(self.hwnd)[0])
                        ly = int(y - win32gui.GetWindowRect(self.hwnd)[1])
                        lparam = (ly << 16) | (lx & 0xFFFF)
                        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
                        time.sleep(0.01)
                        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, lparam)
                    except Exception:
                        pass
                else:
                    pyautogui.click(x=x, y=y, button=self.button)
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._click_loop, daemon=True)
            self._thread.start()
        self._running = True

    def stop(self):
        self._running = False

    def shutdown(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=1)


class App:
    def __init__(self, root):
        self.root = root
        root.title('自动点击器 - GUI')

        self.clicker = AutoClicker()

        frm = ttk.Frame(root, padding=10)
        frm.grid()

        ttk.Button(frm, text='单击选取', command=self.pick_click).grid(column=0, row=0)
        ttk.Button(frm, text='区域选取', command=self.region_pick).grid(column=1, row=0)
        # 复选框表示是否使用前台模式（占用鼠标）
        self.background_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text='前台模式（占用鼠标）', variable=self.background_var).grid(column=2, row=0, columnspan=2)

        ttk.Label(frm, text='Min delay (s):').grid(column=0, row=2, sticky='w')
        self.min_var = tk.DoubleVar(value=0.001)
        ttk.Entry(frm, textvariable=self.min_var, width=10).grid(column=1, row=2, sticky='w')
        ttk.Label(frm, text='Max delay (s):').grid(column=2, row=2, sticky='w')
        self.max_var = tk.DoubleVar(value=0.001)
        ttk.Entry(frm, textvariable=self.max_var, width=10).grid(column=3, row=2, sticky='w')

        ttk.Label(frm, text='X:').grid(column=0, row=3, sticky='w')
        self.x_var = tk.StringVar(value='492')
        ttk.Entry(frm, textvariable=self.x_var, width=8).grid(column=1, row=3, sticky='w')
        ttk.Label(frm, text='Y:').grid(column=2, row=3, sticky='w')
        self.y_var = tk.StringVar(value='60')
        ttk.Entry(frm, textvariable=self.y_var, width=8).grid(column=3, row=3, sticky='w')
        ttk.Label(frm, text='W:').grid(column=0, row=4, sticky='w')
        self.w_var = tk.StringVar(value='27')
        ttk.Entry(frm, textvariable=self.w_var, width=8).grid(column=1, row=4, sticky='w')
        ttk.Label(frm, text='H:').grid(column=2, row=4, sticky='w')
        self.h_var = tk.StringVar(value='16')
        ttk.Entry(frm, textvariable=self.h_var, width=8).grid(column=3, row=4, sticky='w')

        # 热键设置
        ttk.Label(frm, text='开始热键:').grid(column=0, row=5, sticky='w')
        self.start_hot_var = tk.StringVar(value='F6')
        ttk.Entry(frm, textvariable=self.start_hot_var, width=10).grid(column=1, row=5, sticky='w')
        ttk.Label(frm, text='停止热键:').grid(column=2, row=5, sticky='w')
        self.stop_hot_var = tk.StringVar(value='F8')
        ttk.Entry(frm, textvariable=self.stop_hot_var, width=10).grid(column=3, row=5, sticky='w')
        # 自动应用热键（无需点击）

        ttk.Button(frm, text='开始', command=self.start_clicking).grid(column=0, row=6)
        ttk.Button(frm, text='停止', command=self.stop_clicking).grid(column=1, row=6)
        ttk.Button(frm, text='退出', command=self.exit_app).grid(column=3, row=6)

        ttk.Label(frm, text='状态:').grid(column=0, row=7, sticky='w')
        self.status_var = tk.StringVar(value='空闲')
        ttk.Label(frm, textvariable=self.status_var).grid(column=1, row=7, columnspan=3, sticky='w')

        ttk.Label(frm, text='已选 PID:').grid(column=0, row=8, sticky='w')
        self.pid_var = tk.StringVar(value='')
        ttk.Label(frm, textvariable=self.pid_var).grid(column=1, row=8, columnspan=3, sticky='w')

        ttk.Label(frm, text='已选区域:').grid(column=0, row=9, sticky='w')
        self.region_var = tk.StringVar(value='')
        ttk.Label(frm, textvariable=self.region_var).grid(column=1, row=9, columnspan=3, sticky='w')

        # 当热键输入变化时，自动应用
        self.start_hot_var.trace_add('write', lambda *args: self.apply_hotkeys())
        self.stop_hot_var.trace_add('write', lambda *args: self.apply_hotkeys())
        # 当复选框变化时，更新 clicker 模式
        self.background_var.trace_add('write', lambda *args: self._update_clicker_mode())
        for var in (self.x_var, self.y_var, self.w_var, self.h_var):
            var.trace_add('write', lambda *args: self._apply_manual_region())

        # 默认设为后台模式（不占用鼠标）并注册热键
        self._update_clicker_mode()
        self.apply_hotkeys()
        self._apply_manual_region()

    def bind_process(self):
        # 绑定输入 PID/进程 的功能已移除
        messagebox.showinfo('提示', '绑定功能已移除，请使用 "单击选取窗口" 按钮选取目标窗口')

    def pick_click(self):
        # 无需初始提示，直接等待单击选取目标窗口
        while True:
            if win32api.GetAsyncKeyState(0x01) & 0x8000:
                while win32api.GetAsyncKeyState(0x01) & 0x8000:
                    time.sleep(0.01)
                x, y = win32api.GetCursorPos()
                try:
                    hwnd = win32gui.WindowFromPoint((x, y))
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    self.clicker.set_target(hwnd)
                    self.pid_var.set(str(pid))
                    # 在屏幕上绘制所选窗口的边框（短暂），不弹窗
                    try:
                        left, top, right, bottom = get_window_rect(hwnd)
                        self._draw_rect((left, top, right, bottom))
                        # 在 1 秒后清除矩形
                        self.root.after(1000, lambda: self._clear_rect())
                    except Exception:
                        pass
                    self.status_var.set(f'已选 PID {pid} (窗口已标注)')
                    return
                except Exception as e:
                    self.status_var.set(f'识别失败: {e}')
            time.sleep(0.01)

    def _apply_manual_region(self, *args):
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            w = max(0, int(self.w_var.get()))
            h = max(0, int(self.h_var.get()))
        except ValueError:
            return
        self.clicker.region = (x, y, w, h)
        self.region_var.set(f'x={x},y={y},w={w},h={h}')

    def _sync_region_fields(self, region):
        if not region:
            return
        x, y, w, h = region
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.w_var.set(str(w))
        self.h_var.set(str(h))

    def pick_drag(self):
        # 拖拽选取已移除
        messagebox.showinfo('提示', '拖拽选取功能已移除，使用 "单击选取窗口" 以确定目标窗口')

    def region_pick(self):
        if not self.clicker.hwnd:
            messagebox.showwarning('警告', '请先绑定或选取窗口')
            return
        # 在开始区域选取前，屏幕上绘制可选取的窗口范围（不弹窗）
        try:
            left, top, right, bottom = get_window_rect(self.clicker.hwnd)
            self.status_var.set(f'可选范围: left={left}, top={top}, right={right}, bottom={bottom} (请在窗口内拖拽)')
            # 绘制可选范围框，保留直到开始拖拽
            self._draw_rect((left, top, right, bottom))
            # 创建一个明显的顶层提示（非阻塞），便于用户注意到可选范围
            hint = tk.Toplevel(self.root)
            hint.wm_overrideredirect(True)
            hint.attributes('-topmost', True)
            hint.configure(background='#ffeb3b')
            lbl = tk.Label(hint, text='在窗口内按住左键拖拽以选择区域，松开完成', bg='#ffeb3b', fg='black')
            lbl.pack(padx=8, pady=4)
            # 将提示放到主窗口下方偏中位置
            try:
                rx = self.root.winfo_rootx()
                ry = self.root.winfo_rooty() + self.root.winfo_height() + 6
                hint.geometry(f'+{rx}+{ry}')
            except Exception:
                pass
        except Exception:
            self.status_var.set('请在目标窗口内按住左键并拖拽选择区域')

        # 等待按下左键开始拖拽
        while not (win32api.GetAsyncKeyState(0x01) & 0x8000):
            time.sleep(0.01)
        x1, y1 = win32api.GetCursorPos()
        # 拖拽过程中实时绘制选区（在可选范围内约束）
        while (win32api.GetAsyncKeyState(0x01) & 0x8000):
            x2, y2 = win32api.GetCursorPos()
            # 约束到窗口范围
            lx, ty, rx2, by = get_window_rect(self.clicker.hwnd)
            x1c = max(lx, min(rx2, x1))
            x2c = max(lx, min(rx2, x2))
            y1c = max(ty, min(by, y1))
            y2c = max(ty, min(by, y2))
            # 绘制当前选区
            try:
                sel_rect = (min(x1c, x2c), min(y1c, y2c), max(x1c, x2c), max(y1c, y2c))
                self._draw_rect(sel_rect)
            except Exception:
                pass
            time.sleep(0.02)

        # 释放鼠标，获取最终位置
        x2, y2 = win32api.GetCursorPos()
        left, top, right, bottom = get_window_rect(self.clicker.hwnd)
        x1c = max(left, min(right, x1))
        x2c = max(left, min(right, x2))
        y1c = max(top, min(bottom, y1))
        y2c = max(top, min(bottom, y2))
        rx = min(x1c, x2c) - left
        ry = min(y1c, y2c) - top
        rw = abs(x2c - x1c)
        rh = abs(y2c - y1c)
        self.clicker.region = (rx, ry, rw, rh)
        self._sync_region_fields((rx, ry, rw, rh))
        self.region_var.set(f'x={rx},y={ry},w={rw},h={rh}')
        # 清除屏幕绘制的矩形
        self._clear_rect()
        try:
            hint.destroy()
        except Exception:
            pass
        # 简短高亮状态
        self.status_var.set('已选区域 (已标注)')

    def apply_hotkeys(self):
        # remove previous hotkeys
        try:
            if hasattr(self, 'registered_hotkeys'):
                for h in self.registered_hotkeys:
                    try:
                        keyboard.remove_hotkey(h)
                    except Exception:
                        pass
        except Exception:
            pass
        self.registered_hotkeys = []
        start_hot = self.start_hot_var.get().strip()
        stop_hot = self.stop_hot_var.get().strip()
        if start_hot:
            try:
                h1 = keyboard.add_hotkey(start_hot, lambda: self.start_clicking())
                self.registered_hotkeys.append(h1)
            except Exception as e:
                messagebox.showerror('热键错误', f'无法注册开始热键: {e}')
        if stop_hot:
            try:
                h2 = keyboard.add_hotkey(stop_hot, lambda: self.stop_clicking())
                self.registered_hotkeys.append(h2)
            except Exception as e:
                messagebox.showerror('热键错误', f'无法注册停止热键: {e}')
        self.status_var.set('热键已应用')

    # 使用 GDI DrawFocusRect 在屏幕上绘制 XOR 矩形，鼠标/点击仍可透过
    def _draw_rect(self, rect):
        try:
            hdc = win32gui.GetDC(0)
            # 擦除上一个矩形
            if hasattr(self, '_last_rect') and self._last_rect:
                try:
                    self._draw_focus_rects(hdc, self._last_rect)
                except Exception:
                    pass
            try:
                self._draw_focus_rects(hdc, rect)
                self._last_rect = rect
            except Exception:
                pass
        finally:
            try:
                win32gui.ReleaseDC(0, hdc)
            except Exception:
                pass

    def _draw_focus_rects(self, hdc, rect):
        # 绘制多条相邻矩形以形成更粗的边框
        left, top, right, bottom = rect
        for offset in (-2, -1, 0, 1, 2):
            try:
                win32gui.DrawFocusRect(hdc, (left + offset, top + offset, right - offset, bottom - offset))
            except Exception:
                pass

    def _clear_rect(self):
        try:
            if hasattr(self, '_last_rect') and self._last_rect:
                hdc = win32gui.GetDC(0)
                try:
                    self._draw_focus_rects(hdc, self._last_rect)
                except Exception:
                    pass
                finally:
                    try:
                        win32gui.ReleaseDC(0, hdc)
                    except Exception:
                        pass
                self._last_rect = None
        except Exception:
            self._last_rect = None

    def _update_clicker_mode(self):
        # 背景模式为默认；复选框勾选表示前台模式
        try:
            is_front = bool(self.background_var.get())
            self.clicker.background_mode = not is_front
            self.status_var.set('前台模式' if is_front else '后台模式')
        except Exception:
            pass

    def start_clicking(self):
        try:
            self.clicker.min_delay = float(self.min_var.get())
            self.clicker.max_delay = float(self.max_var.get())
        except Exception:
            messagebox.showerror('错误', '延迟必须是数字')
            return
        if not self.clicker.hwnd:
            messagebox.showwarning('警告', '请先绑定或选取窗口')
            return
        self.clicker.start()
        self.status_var.set('正在点击...')

    def stop_clicking(self):
        self.clicker.stop()
        self.status_var.set('已停止')

    def exit_app(self):
        self.clicker.shutdown()
        self.root.quit()


def main():
    root = tk.Tk()
    app = App(root)
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f'+{x}+{y}')
    root.mainloop()


if __name__ == '__main__':
    main()
