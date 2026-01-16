# Worker A 設計文檔

## 概述

本設計實現了 Todo List 系統的兩個核心領域：
1. **用戶認證（User Authentication）**
2. **待辦事項管理（Todo List Management）**

## 選擇的實現方案

### 認證領域

#### 用戶存儲：方案 A2 - 檔案基礎用戶存儲（File-based User Storage）

**選擇理由：**
- 提供數據持久化能力，適合演示和測試
- 使用 JSON 格式，易於閱讀和調試
- 無需額外的數據庫依賴
- 可以輕易遷移到其他存儲方案（如數據庫）

**實現細節：**
- 使用 `users.json` 文件存儲用戶資料
- 使用 `bcrypt` 進行密碼哈希
- 自動創建存儲文件（如果不存在）

**未選擇的方案：方案 A1 - 內存用戶映射**
- 雖然更簡單，但不提供持久化能力
- 服務器重啟後會丟失所有用戶數據
- 不適合任何需要數據保留的場景

#### 會話處理：方案 B1 - 無狀態令牌（JWT）

**選擇理由：**
- 無需服務器端會話存儲，簡化架構
- 適合分散式系統（未來擴展性）
- 令牌包含所有必要信息，易於驗證
- 標準化的認證機制，易於理解和維護

**實現細節：**
- 使用 `PyJWT` 庫實現 JWT 令牌
- 令牌有效期：24 小時
- 使用 HS256 算法簽名
- 令牌包含 `username`、`iat`（簽發時間）、`exp`（過期時間）

**未選擇的方案：方案 B2 - 內存會話映射**
- 需要服務器端狀態管理
- 不適合多實例部署
- 服務器重啟會導致所有用戶登出

### 待辦事項領域

#### 存儲選項：方案 C2 - JSON 檔案持久化

**選擇理由：**
- 提供持久化能力，數據不會因服務器重啟而丟失
- JSON 格式易於閱讀和調試
- 與用戶存儲方案保持一致（同樣使用文件存儲）
- 可以輕易遷移到數據庫方案

**實現細節：**
- 使用 `todos.json` 文件存儲所有待辦事項
- 每個待辦事項包含：
  - `id`: UUID（使用 `uuid.uuid4()` 生成）
  - `user_id`: 關聯的用戶名
  - `content`: 待辦事項內容
  - `created_at`: ISO 格式的時間戳

**未選擇的方案：方案 C1 - 內存列表**
- 不提供持久化能力
- 數據在服務器重啟後丟失
- 不適合需要數據保留的場景

## 架構設計

### 模組結構

```
Worker_a_src/
├── auth/                    # 認證領域
│   ├── __init__.py
│   ├── user_storage.py      # 文件基礎用戶存儲
│   ├── token_manager.py     # JWT 令牌管理
│   └── auth_service.py      # 認證服務（協調層）
├── todos/                   # 待辦事項領域
│   ├── __init__.py
│   ├── todo_storage.py      # JSON 檔案存儲
│   └── todo_service.py      # 待辦事項服務
├── app.py                   # HTTP API 應用程式
├── requirements.txt         # Python 依賴
├── DESIGN.md               # 設計文檔（本文件）
└── EXPLORATION.md          # 探索記錄
```

### 領域分離

明確分離了兩個領域：

1. **認證領域（auth/）**
   - `FileUserStorage`: 用戶資料存儲
   - `JWTTokenManager`: 令牌生成和驗證
   - `AuthService`: 協調用戶存儲和令牌管理

2. **待辦事項領域（todos/）**
   - `JSONTodoStorage`: 待辦事項資料存儲
   - `TodoService`: 待辦事項業務邏輯

### API 設計

#### 認證端點

- `POST /api/register`
  - 請求體：`{ "username": "string", "password": "string" }`
  - 響應：`{ "message": "User registered successfully" }` (201)
  - 或：`{ "error": "error message" }` (400)

- `POST /api/login`
  - 請求體：`{ "username": "string", "password": "string" }`
  - 響應：`{ "token": "jwt_token_string" }` (200)
  - 或：`{ "error": "error message" }` (401)

#### 待辦事項端點

- `POST /api/todos`
  - 認證：需要 Bearer token（Authorization header）
  - 請求體：`{ "content": "todo content" }`
  - 響應：`{ "id": "uuid", "user_id": "username", "content": "todo", "created_at": "timestamp" }` (201)
  - 或：`{ "error": "error message" }` (400)

- `GET /api/todos`
  - 認證：需要 Bearer token（Authorization header）
  - 響應：`{ "todos": [...] }` (200)

## 認證流程

1. 用戶註冊：`POST /api/register` → 密碼被哈希並存儲
2. 用戶登錄：`POST /api/login` → 驗證憑證 → 返回 JWT 令牌
3. 訪問受保護資源：在 `Authorization` header 中提供 `Bearer <token>`
4. API 驗證令牌：`@require_auth` 裝飾器驗證令牌並提取用戶名

## 數據模型

### 用戶（存儲在 users.json）
```json
{
  "username": {
    "username": "string",
    "password_hash": "bcrypt_hash_string"
  }
}
```

### 待辦事項（存儲在 todos.json）
```json
[
  {
    "id": "uuid",
    "user_id": "username",
    "content": "todo content",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

## 安全考量

1. **密碼安全**
   - 使用 `bcrypt` 進行密碼哈希
   - 密碼永遠不會以明文形式存儲

2. **令牌安全**
   - 使用密鑰簽名 JWT 令牌
   - 令牌包含過期時間
   - 在生產環境中應使用更強的密鑰

3. **認證中間件**
   - 所有待辦事項端點都需要認證
   - 用戶只能訪問自己的待辦事項

## 依賴項

- `flask==3.0.0`: HTTP 框架
- `bcrypt==4.0.1`: 密碼哈希
- `PyJWT==2.8.0`: JWT 令牌處理

## 運行方式

1. 安裝依賴：`pip install -r requirements.txt`
2. 運行應用：`python app.py`
3. 應用將在 `http://localhost:5000` 啟動

## 與鎖定決策的一致性

✅ **Python 基礎實現**：所有代碼使用 Python 編寫

✅ **HTTP 基礎 API**：使用 Flask 提供 RESTful API

✅ **明確分離認證和待辦事項領域**：
   - `auth/` 目錄：認證領域
   - `todos/` 目錄：待辦事項領域
   - 兩個領域通過服務層接口交互
