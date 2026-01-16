@echo off
echo ============================================================
echo Worker A GUI 服務器啟動腳本
echo ============================================================
echo.

cd /d "%~dp0"

echo 檢查 Python 環境...
python --version
if errorlevel 1 (
    echo 錯誤: 未找到 Python！請確保 Python 已安裝並添加到 PATH。
    pause
    exit /b 1
)

echo.
echo 啟動 GUI 服務器...
echo 前端界面將在 http://localhost:5002 啟動
echo 請確保 Worker A 後端 API (http://localhost:5000) 正在運行
echo.

python app_gui.py

pause