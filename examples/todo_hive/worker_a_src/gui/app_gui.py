"""
Worker A GUI Server

Flask 應用程序，提供前端界面服務。
前端界面連接到 Worker A 後端 API (http://localhost:5000)
"""

from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)


@app.route('/')
def index():
    """渲染主頁面"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """健康檢查端點"""
    return {'status': 'healthy', 'service': 'Worker A GUI'}, 200


if __name__ == '__main__':
    print("=" * 60)
    print("Worker A GUI 服務器")
    print("=" * 60)
    print("前端界面: http://localhost:5002")
    print("後端 API: http://localhost:5000")
    print("=" * 60)
    print("請確保 Worker A 後端 API 服務器正在運行")
    print("=" * 60)
    
    app.run(debug=True, port=5002, host='0.0.0.0')