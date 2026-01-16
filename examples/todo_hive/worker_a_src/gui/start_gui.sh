#!/bin/bash
# Worker A GUI 啟動腳本 (Linux/macOS)

echo "========================================"
echo "Worker A GUI 應用程式啟動腳本"
echo "========================================"
echo ""

# 檢查 Python 是否安裝
if ! command -v python3 &> /dev/null; then
    echo "[錯誤] 未找到 Python，請先安裝 Python 3.6+"
    exit 1
fi

echo "[1/2] 檢查後端 API 服務..."
echo "請確保後端 API 正在運行 (python app.py)"
echo ""

# 切換到 GUI 目錄
cd "$(dirname "$0")"

echo "[2/2] 啟動 GUI 應用程式..."
echo ""
echo "GUI 介面: http://localhost:5002"
echo "後端 API: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止服務"
echo "========================================"
echo ""

python3 app_gui.py
