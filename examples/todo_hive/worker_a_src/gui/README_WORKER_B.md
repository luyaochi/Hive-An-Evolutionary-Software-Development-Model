# Worker A GUI 連接 Worker B 後台說明

## 概述

Worker A 的 GUI 已經更新，現在可以同時支持連接 Worker A 和 Worker B 的後台 API。

## 如何切換到 Worker B 後台

### 方法 1：修改 API 地址（推薦）

編輯 `gui/static/js/api.js` 文件，修改 `WorkerAApi` 的構造函數：

```javascript
// 原來的（連接 Worker A）
const api = new WorkerAApi('http://localhost:5000');

// 修改為（連接 Worker B）
const api = new WorkerAApi('http://localhost:5001');
```

### 方法 2：通過瀏覽器控制台

打開瀏覽器開發者工具（F12），在控制台中執行：

```javascript
// 切換到 Worker B
api.baseUrl = 'http://localhost:5001';
api.setBackendType('worker_b');
localStorage.setItem('backend_type', 'worker_b');
location.reload();
```

## 功能差異

### Worker A 後台（端口 5000）

- ✅ 用戶註冊（返回成功訊息）
- ✅ 用戶登錄（返回 token）
- ✅ 創建待辦事項
- ✅ 查看待辦事項列表

### Worker B 後台（端口 5001）

- ✅ 用戶註冊（返回 user + token，自動登錄）
- ✅ 用戶登錄（返回 user + token）
- ✅ 獲取當前用戶資訊 (`/api/me`)
- ❌ 待辦事項功能（不支持）

## 自動適配

GUI 會自動檢測和適配兩種後台：

1. **註冊響應**：
   - Worker A: `{message: "..."}` → 提示登錄
   - Worker B: `{user: {...}, token: "..."}` → 自動登錄並跳轉

2. **登錄響應**：
   - Worker A: `{token: "..."}` → 使用用戶名
   - Worker B: `{user: {...}, token: "..."}` → 使用返回的用戶名

3. **待辦事項**：
   - Worker A: 顯示待辦事項管理界面
   - Worker B: 隱藏待辦事項功能

## 測試步驟

### 測試連接 Worker B

1. 啟動 Worker B 後台：
   ```bash
   cd Worker_b_src
   python app.py
   ```
   後台將在 `http://localhost:5001` 運行

2. 修改 Worker A GUI 的 API 地址（見上方）

3. 啟動 Worker A GUI：
   ```bash
   cd Worker_a_src/gui
   python app_gui.py
   ```

4. 訪問 GUI：`http://localhost:5002`

5. 測試功能：
   - 註冊新用戶：應該自動登錄並跳轉（Worker B 特性）
   - 登錄：應該可以看到用戶資訊
   - 待辦事項：應該被隱藏（Worker B 不支持）

## 注意事項

1. **令牌不共享**：Worker A 和 Worker B 使用不同的 JWT 密鑰，令牌不能互換

2. **數據不共享**：兩個後台使用不同的存儲文件：
   - Worker A: `users.json`, `todos.json`
   - Worker B: `users_b.json`

3. **切換後台**：切換後台時需要重新登錄，因為令牌不兼容

4. **瀏覽器緩存**：切換後台後，建議清除瀏覽器的 localStorage 或使用無痕模式測試

## 故障排除

### 無法連接 Worker B

1. 確認 Worker B 後台正在運行（端口 5001）
2. 檢查 API 地址是否正確
3. 查看瀏覽器控制台的錯誤訊息

### 待辦事項功能仍然顯示

1. 檢查後台類型是否正確設置：`api.getBackendType()`
2. 清除瀏覽器緩存並重新載入頁面
3. 確認 API 響應格式正確

### 令牌驗證失敗

1. Worker A 和 Worker B 的令牌不兼容
2. 切換後台後必須重新登錄
3. 清除 localStorage 中的舊令牌
