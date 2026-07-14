# 鼠标范围限制工具

## 功能

- 点击“框选范围”按钮后拖拽选取屏幕上的矩形区域
- 选区设置完成后，按 F7 开始限制鼠标只能在此范围内移动
- 按 F8 结束限制
- 默认热键可在界面中修改
- 框选过程中显示区域提示线，完成后不弹出提示框

## 使用

1. 安装依赖：

```powershell
pip install -r requirements.txt
```

2. 运行脚本：

```powershell
python mouse_range.py
```

3. 点击“框选范围”，按住鼠标左键拖拽完成范围选择。
4. 按 F7 开始限制，F8 结束。

## 打包

如果已安装 PyInstaller：

```powershell
pyinstaller --onefile --noconsole mouse_range.py
```

打包后可执行文件会生成在 `dist\mouse_range.exe`。
