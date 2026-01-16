# Worker A GUI 使用說明

## 概述

Worker A GUI 提供了一個現代化的 Web 用戶界面，用於與 Worker A 後端 API 交互。GUI 包含：

- **用戶登錄**：登錄到系統
- **待辦事項管理**：創建和查看待辦事項

## 系統架構

```
┌─────────────────┐
│   Web Browser   │
│  (User Client)  │
└────────┬────────┘
         │ HTTP
         │
┌────────▼────────┐      ┌─────────────────┐
│   GUI Server    │      │  Backend API     │
│  (Flask:5002)   │──────▶│  (Flask:5000)   │
│                 │ HTTP  │                 │
│  - Static Files │      │  - Auth API     │
│  - Templates    │      │  - Todo API     │
└─────────────────┘      └─────────────────┘
```

## 快速開始

### 1. 啟動後端 API 服務器

首先，確保 Worker A 後端 API 正在運行：

```bash
cd ../..
python app.py
```

後端 API 將在 `http://localhost:5000` 啟動。

### 2. 啟動 GUI 服務器

#### Windows

```bash
start_gui.bat
```

或者直接運行：

```bash
python app_gui.py
```

#### Linux/Mac

```bash
chmod +x start_gui.sh
./start_gui.sh
```

或者直接運行：

```bash
python3 app_gui.py
```

GUI 服務器將在 `http://localhost:5002` 啟動。

### 3. 訪問界面

在瀏覽器中打開：`http://localhost:5002`

## 功能說明

### 登錄功能

1. **輸入憑證**：輸入用戶名和密碼
2. **登錄**：點擊「登錄」按鈕
3. **自動跳轉**：登錄成功後自動跳轉到待辦事項管理頁面

**注意**：如果還沒有帳號，請先到 Worker B 註冊頁面（`http://localhost:5001`）註冊。

### 待辦事項管理

#### 新增待辦事項

1. 在「新增待辦事項」區域輸入內容
2. 點擊「新增」按鈕
3. 待辦事項將出現在列表中

#### 查看待辦事項

- 登錄後自動載入所有待辦事項
- 點擊「刷新」按鈕手動更新列表
- 顯示待辦事項的 ID 和創建時間

#### 字符限制

- 待辦事項內容最多 1000 字符
- 輸入框下方顯示字符計數

## 技術棧

### 前端
- **HTML5**：語義化標記
- **CSS3**：現代化樣式，響應式設計
- **JavaScript (ES6+)**：原生 JavaScript，無框架依賴

### 後端
- **Flask**：輕量級 Web 框架
  - 模板渲染
  - 靜態文件服務

## 文件結構

```
gui/
├── README.md                  # 本文件
├── app_gui.py                 # Flask GUI 服務器
├── start_gui.bat              # Windows 啟動腳本
├── start_gui.sh               # Linux/Mac 啟動腳本
├── templates/                 # HTML 模板
│   └── index.html            # 主頁面
└── static/                    # 靜態資源
    ├── css/
    │   └── style.css         # 樣式文件
    └── js/
        ├── api.js            # API 客戶端
        └── app.js            # 應用邏輯
```

## API 配置

GUI 默認連接到 `http://localhost:5000` 的後端 API。

如需更改 API 地址，請編輯 `static/js/api.js`：

```javascript
class WorkerAApi {
    constructor(baseUrl = 'http://localhost:5000') {  // 修改這裡
        this.baseUrl = baseUrl;
        // ...
    }
}
```

## 瀏覽器兼容性

- Chrome/Edge（推薦）
- Firefox
- Safari
- 移動瀏覽器

## 故障排除

### 無法連接到後端 API

1. 確保後端 API 服務器正在運行（`http://localhost:5000`）
2. 檢查瀏覽器控制台的錯誤訊息
3. 確認 API 地址配置正確

### 登錄失敗

1. 確保已通過 Worker B 註冊了帳號
2. 檢查用戶名和密碼是否正確
3. 確認 Worker A 後端 API 能夠訪問用戶存儲文件

### 待辦事項無法載入

1. 檢查是否已成功登錄
2. 確認令牌是否有效（登出後重新登錄）
3. 檢查後端 API 是否正常運行

## 安全注意事項

- 令牌存儲在 `localStorage`（僅用於開發環境）
- 生產環境建議使用更安全的存儲方式
- 必須使用 HTTPS 保護令牌傳輸

## 開發說明

### 修改樣式

編輯 `static/css/style.css`，使用 CSS 變量定義主題：

```css
:root {
    --primary-color: #4f46e5;
    --success-color: #10b981;
    /* ... */
}
```

### 添加功能

- **API 客戶端**：編輯 `static/js/api.js`
- **應用邏輯**：編輯 `static/js/app.js`
- **UI 結構**：編輯 `templates/index.html`

## 未來改進

- [ ] 添加待辦事項搜索功能
- [ ] 添加待辦事項分類/標籤
- [ ] 改進響應式設計
- [ ] 添加暗黑模式
- [ ] 添加國際化支持