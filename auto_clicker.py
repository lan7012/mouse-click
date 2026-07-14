#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动点击器 (Windows)

功能:
- 绑定到指定进程 (通过进程名或 PID)
- 可配置点击速度（最小/最大延迟）
- 在目标窗口的指定区域内随机点击
- 使用热键启动/停止（默认 F6）和退出（默认 F8）

依赖:
    pip install pyautogui psutil pywin32 keyboard

注意: 使用自动化工具请遵守相关软件服务条款，不要在不允许的场景中使用。
"""

import argparse
import random
import threading
import time
import sys

try:
    import psutil
    import pyautogui
    import keyboard
    import win32gui
    import win32process
    import win32con
    import win32api
except Exception as e:
    print("缺少依赖或在导入时出错:", e)
    print("请运行: pip install pyautogui psutil pywin32 keyboard")
    sys.exit(1)


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


def find_pid_by_name(name):
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"].lower() == name.lower():
                return proc.info["pid"]
        except Exception:
            continue
    return None


def pick_pid_by_click():
    print("请将鼠标移动到目标窗口并单击左键以选取进程...")
    # 等待左键按下并释放
    while True:
        if win32api.GetAsyncKeyState(0x01) & 0x8000:
            # 等待释放
            while win32api.GetAsyncKeyState(0x01) & 0x8000:
                time.sleep(0.01)
            x, y = win32api.GetCursorPos()
            try:
                hwnd = win32gui.WindowFromPoint((x, y))
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                print(f"选中 hwnd={hwnd}, pid={pid}")
                return pid
            except Exception as e:
                print("未能识别窗口，请重试：", e)
        time.sleep(0.01)


def pick_pid_by_drag():
    print("按住左键并拖拽选取区域，松开左键完成选择...")
    # 等待按下
    while not (win32api.GetAsyncKeyState(0x01) & 0x8000):
        time.sleep(0.01)
    x1, y1 = win32api.GetCursorPos()
    # 等待释放
    while (win32api.GetAsyncKeyState(0x01) & 0x8000):
        time.sleep(0.01)
    x2, y2 = win32api.GetCursorPos()
    midx = (x1 + x2) // 2
    midy = (y1 + y2) // 2
    try:
        hwnd = win32gui.WindowFromPoint((midx, midy))
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        print(f"选中区域中心 hwnd={hwnd}, pid={pid}")
        return pid
    except Exception as e:
        print("未能识别窗口，请重试：", e)
        return None


def get_window_rect(hwnd):
    # returns (left, top, right, bottom)
    return win32gui.GetWindowRect(hwnd)


class AutoClicker:
    def __init__(self, hwnd, region=None, min_delay=0.05, max_delay=0.2, button="left", bring_to_front=True):
        self.hwnd = hwnd
        self.region = region  # (x, y, w, h) relative to window
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.button = button
        self.bring_to_front = bring_to_front

        self._running = False
        self._stop = False
        self._thread = None

    def _random_point(self):
        left, top, right, bottom = get_window_rect(self.hwnd)
        win_w = right - left
        win_h = bottom - top

        if self.region:
            rx, ry, rw, rh = self.region
            x = left + rx + random.randint(0, max(0, rw - 1))
            y = top + ry + random.randint(0, max(0, rh - 1))
        else:
            x = left + random.randint(0, max(0, win_w - 1))
            y = top + random.randint(0, max(0, win_h - 1))
        return x, y

    def _click_loop(self):
        while not self._stop:
            if not self._running:
                time.sleep(0.05)
                continue

            if self.bring_to_front:
                try:
                    win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(self.hwnd)
                except Exception:
                    pass

            x, y = self._random_point()
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


def parse_region(s: str):
    # expect format x,y,w,h
    parts = s.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("region 格式应为 x,y,w,h")
    return tuple(int(p) for p in parts)


def main():
    parser = argparse.ArgumentParser(description="自动点击器: 绑定进程并在窗口区域内随机点击")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--process", help="进程名，例如 chrome.exe")
    group.add_argument("--pid", type=int, help="进程 ID")
    parser.add_argument("--pick", action="store_true", help="单击选取目标窗口进程")
    parser.add_argument("--drag-pick", action="store_true", help="拖拽选取目标窗口进程")
    parser.add_argument("--region-pick", action="store_true", help="在已选窗口上通过拖拽选择点击区域（相对窗口坐标）")

    parser.add_argument("--region", type=parse_region, help="窗口内相对区域 x,y,w,h（逗号分隔））")
    parser.add_argument("--min-delay", type=float, default=0.05, help="点击之间的最小延迟（秒）")
    parser.add_argument("--max-delay", type=float, default=0.2, help="点击之间的最大延迟（秒）")
    parser.add_argument("--button", choices=["left", "right", "middle"], default="left", help="点击鼠标按钮")
    parser.add_argument("--start-hotkey", default="F6", help="开始/停止切换热键（默认 F6）")
    parser.add_argument("--exit-hotkey", default="F8", help="退出热键（默认 F8）")
    parser.add_argument("--no-front", action="store_true", help="不要将窗口置于前端")

    args = parser.parse_args()

    pid = args.pid

    # 支持通过单击/拖拽选择目标窗口
    if args.pick:
        chosen = pick_pid_by_click()
        if chosen:
            pid = chosen
    elif args.drag_pick:
        chosen = pick_pid_by_drag()
        if chosen:
            pid = chosen

    if args.process and not pid:
        pid = find_pid_by_name(args.process)
        if pid is None:
            print("未找到进程：", args.process)
            sys.exit(1)

    hwnds = find_hwnds_by_pid(pid)
    if not hwnds:
        print("未找到与 PID 关联的可见窗口（pid={}）".format(pid))
        sys.exit(1)

    hwnd = hwnds[0]
    print("使用窗口句柄: {}".format(hwnd))

    def pick_region_for_window(hwnd):
        print("在目标窗口上按住左键并拖拽选择区域，松开完成选择...")
        # 等待按下
        while not (win32api.GetAsyncKeyState(0x01) & 0x8000):
            time.sleep(0.01)
        x1, y1 = win32api.GetCursorPos()
        # 等待释放
        while (win32api.GetAsyncKeyState(0x01) & 0x8000):
            time.sleep(0.01)
        x2, y2 = win32api.GetCursorPos()

        left, top, right, bottom = get_window_rect(hwnd)
        # clamp to window
        x1c = max(left, min(right, x1))
        x2c = max(left, min(right, x2))
        y1c = max(top, min(bottom, y1))
        y2c = max(top, min(bottom, y2))

        rx = min(x1c, x2c) - left
        ry = min(y1c, y2c) - top
        rw = abs(x2c - x1c)
        rh = abs(y2c - y1c)
        print(f"选取相对区域: x={rx}, y={ry}, w={rw}, h={rh}")
        return (rx, ry, rw, rh)

    # 如果要求区域选择，则在窗口上进行拖拽选区
    if args.region_pick:
        chosen_region = pick_region_for_window(hwnd)
        if chosen_region:
            args.region = chosen_region

    ac = AutoClicker(hwnd, region=args.region, min_delay=args.min_delay, max_delay=args.max_delay, button=args.button, bring_to_front=not args.no_front)

    print("热键: 开始/停止 -> {}，退出 -> {}".format(args.start_hotkey, args.exit_hotkey))
    print("按 {} 切换开始/停止。按 {} 退出。".format(args.start_hotkey, args.exit_hotkey))

    # 注册热键
    def toggle():
        if ac._running:
            ac.stop()
            print("已停止")
        else:
            ac.start()
            print("已开始")

    def exit_handler():
        print("退出中...")
        ac.shutdown()
        keyboard.unhook_all()
        sys.exit(0)

    keyboard.add_hotkey(args.start_hotkey, toggle)
    keyboard.add_hotkey(args.exit_hotkey, exit_handler)

    # 主循环：保持运行，热键处理在线程中
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        exit_handler()


if __name__ == "__main__":
    main()
