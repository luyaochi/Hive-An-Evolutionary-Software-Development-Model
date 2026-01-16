#!/bin/bash

echo "============================================================"
echo "Worker A GUI 服務器啟動腳本"
echo "============================================================"
echo

cd "$(dirname "$0")"

echo "檢查 Python 環境..."
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 未找到 Python3！請確保 Python3 已安裝。"
    exit 1
fi

python3 --version
echo

echo "啟動 GUI 服務器..."
echo "前端界面將在 http://localhost:5002 啟動"
echo "請確保 Worker A 後端 API (http://localhost:5000) 正在運行"
echo

python3 app_gui.py