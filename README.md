# 鼠标点击

本项目是一个 Windows 平台的自动点击工具，包含命令行和 GUI 两种版本。

## 文件结构

- `auto_clicker.py`：命令行版本，支持绑定窗口、指定区域、随机点击、前台/后台点击模式。
- `gui_auto_clicker.py`：图形界面版本，包含单击选取窗口、区域选取、热键启动/停止、后台点击模式。
- `requirements.txt`：依赖列表。
- `dist/auto_clicker.exe`：已生成的命令行可执行文件。
- `dist/gui_auto_clicker.exe`：已生成的 GUI 可执行文件。
- `build/`：PyInstaller 构建缓存目录。

## 功能说明

- 单击选取：直接点击目标窗口后自动绑定该窗口，无需弹窗确认。
- 区域选取：在目标窗口内拖拽选区，实时显示高亮选区，并自动记录相对区域。
- 默认延迟：最小 0.01 秒，最大 0.05 秒，适合快速点击测试。
- 前台/后台模式：可在 GUI 中切换，后台模式使用 Windows 消息模拟点击，不占用鼠标光标。
- 热键：默认开始 `F6`，停止 `F8`。

## 快速使用

1. 双击 `dist/gui_auto_clicker.exe` 启动 GUI。
2. 点击“单击选取”并在目标窗口中点击一次，绑定目标窗口。
3. 点击“区域选取”，在目标窗口内拖拽设定点击区域。
4. 点击“开始”或按 `F6` 开始点击，按 `F8` 停止。

## 解析

本项目使用以下核心逻辑：

- `win32gui.WindowFromPoint` 获取鼠标所在窗口句柄，`win32process.GetWindowThreadProcessId` 获取 PID。
- `get_window_rect` 获取窗口全局坐标。
- 区域选取使用 `DrawFocusRect` 绘制 XOR 高亮矩形，绘制过程中不会阻塞鼠标事件。
- 点击循环使用 `pyautogui.click`（前台模式）或 `win32api.PostMessage` 发送 `WM_LBUTTONDOWN/WM_LBUTTONUP`（后台模式）。

## GitHub 上传说明

- 当前仓库目录：`鼠标点击`
- 可执行文件已经包含在 `dist/` 下，可作为 GitHub Release 附件上传。
- 若要在 GitHub 上发布下载，请将 `dist/gui_auto_clicker.exe` 和 `dist/auto_clicker.exe` 上传到 Release 资产。

## 新增工具：鼠标范围限制

- 目录：`鼠标范围/`
- 功能：通过界面框选或手动输入坐标，使用 F7 开始限制鼠标只能在指定矩形区域内移动，F8 结束限制。
- 默认范围：`177,48,2334,1392`
- 运行方式：`python 鼠标范围\mouse_range.py`
- 可执行文件：`鼠标范围\dist\mouse_range.exe`

### 解析

- 核心逻辑使用 `ctypes.windll.user32.ClipCursor` 实现鼠标范围限制。
- `mouse_range.py` 中的 `_select_region()` 监听鼠标左键拖拽并绘制选区，完成后保存矩形坐标。
- `_apply_manual_region()` 支持手动输入左、上、右、下坐标。
- `start()` 将当前矩形传递给 `ClipCursor` 开始限制，`stop()` 传 `None` 释放限制。
- 热键配置通过 `keyboard` 模块注册，默认 F7/F8，可在 GUI 中修改。

## 环境

- Python 3.13
- 依赖：`pyautogui`, `psutil`, `pywin32`, `keyboard`

## 安装

```powershell
python -m pip install -r requirements.txt
```

## 运行

```powershell
python gui_auto_clicker.py
```

或直接运行 `dist/gui_auto_clicker.exe`。
