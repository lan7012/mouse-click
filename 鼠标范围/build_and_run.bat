@echo off
cd /d "%~dp0"
pyinstaller --onefile --noconsole mouse_range.py
if errorlevel 1 (
    echo 打包失败，請檢查輸出信息。
    pause
    exit /b 1
)
if exist "%~dp0dist\mouse_range.exe" (
    start "" "%~dp0dist\mouse_range.exe"
) else (
    echo 找不到 dist\mouse_range.exe
)
