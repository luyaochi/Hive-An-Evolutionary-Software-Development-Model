"""
Worker B GUI Application
提供 Web 圖形介面，整合 Worker B 的認證 API
"""

from flask import Flask, render_template, send_from_directory
import os


def create_gui_app():
    """創建 GUI Flask 應用"""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    @app.route('/')
    def index():
        """主頁面"""
        return render_template('index.html')

    @app.route('/static/<path:filename>')
    def static_files(filename):
        """提供靜態文件"""
        return send_from_directory('static', filename)

    return app


if __name__ == '__main__':
    # 確保在正確的目錄中運行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    app = create_gui_app()
    print("=" * 60)
    print("Worker B GUI 應用程式")
    print("=" * 60)
    print("GUI 介面: http://localhost:5002")
    print("後端 API: http://localhost:5001")
    print("=" * 60)
    print("\n請確保後端 API 服務正在運行 (python app.py)")
    print("=" * 60)

    app.run(debug=True, port=5002, host='0.0.0.0')
