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
- 实时坐标输入：支持直接输入 X/Y/W/H，修改后会立即生效，便于精确调整点击区域。
- 区域保留：切换目标窗口后，会保留当前已选区域，避免重复重新框选。
- 默认延迟：最小 0.001 秒，最大 0.001 秒，适合高频点击测试。
- 前台/后台模式：可在 GUI 中切换，后台模式使用 Windows 消息模拟点击，不占用鼠标光标。
- 热键：默认开始 `F6`，停止 `F8`。

## 快速使用

1. 双击 `dist/gui_auto_clicker.exe` 启动 GUI。
2. 点击“单击选取”并在目标窗口中点击一次，绑定目标窗口。
3. 点击“区域选取”，在目标窗口内拖拽设定点击区域，或直接在 X/Y/W/H 输入框中填写坐标。
4. 点击“开始”或按 `F6` 开始点击，按 `F8` 停止。
5. 若需要切换目标窗口，当前区域会保留，可继续使用当前配置。

## 解析

本项目使用以下核心逻辑：

- `win32gui.WindowFromPoint` 获取鼠标所在窗口句柄，`win32process.GetWindowThreadProcessId` 获取 PID。
- `get_window_rect` 获取窗口全局坐标。
- 区域选取使用 `DrawFocusRect` 绘制 XOR 高亮矩形，绘制过程中不会阻塞鼠标事件。
- 点击循环使用 `pyautogui.click`（前台模式）或 `win32api.PostMessage` 发送 `WM_LBUTTONDOWN/WM_LBUTTONUP`（后台模式）。

## 运行

```powershell
python gui_auto_clicker.py
```

或直接运行 `dist/gui_auto_clicker.exe`。
