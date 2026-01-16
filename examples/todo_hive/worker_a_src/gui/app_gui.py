"""
Worker A GUI Application
提供 Web 圖形介面，整合 Worker A 的認證和待辦事項 API
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
    print("Worker A GUI 應用程式")
    print("=" * 60)
    print("GUI 介面: http://localhost:5002")
    print("預設後端 API: http://localhost:5000 (Worker A)")
    print("也可以連接到: http://localhost:5001 (Worker B)")
    print("=" * 60)
    print("\n請確保後端 API 服務正在運行")
    print("- Worker A: python app.py (端口 5000)")
    print("- Worker B: cd Worker_b_src && python app.py (端口 5001)")
    print("=" * 60)
    print("\n注意: 可以通過修改 static/js/api.js 中的 baseUrl 來切換後台")
    print("=" * 60)

    app.run(debug=True, port=5002, host='0.0.0.0')
