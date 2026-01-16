# Worker A 設計文檔

## 概述

本設計文檔描述 Worker A 實現的用戶登錄和待辦事項管理功能。

## 設計目標

根據 `worker_a.md` 的任務分配，Worker A 負責實現：

1. **User Login（用戶登錄）**
   - 用戶登錄與憑證驗證
   - 無授權角色
   - 無密碼重置
   - 無第三方身份提供者

2. **Todo List Management（待辦事項管理）**
   - 創建待辦事項（Create todo items）
   - 列出待辦事項（List todo items）
   - 待辦事項與已認證用戶關聯
   - 無更新或刪除操作
   - 無優先級或標籤功能

## 架構設計

### 模組結構

```
worker_a_src/
├── app.py                          # Flask HTTP API 應用
├── requirements.txt                # Python 依賴
├── README.md                       # 使用文檔
├── DESIGN.md                       # 本設計文檔
├── auth/                           # 認證模組
│   ├── __init__.py
│   ├── user_storage.py             # 檔案基礎用戶存儲
│   ├── token_manager.py            # JWT token 管理
│   └── auth_service.py             # 認證服務（登錄和 JWT）
└── todos/                          # 待辦事項模組
    ├── __init__.py
    ├── todo_storage.py             # 檔案基礎待辦事項存儲
    └── todo_service.py             # 待辦事項服務
```

## 設計決策

### 認證系統設計

#### 1. FileBasedUserStorage

**職責：** 管理用戶資料的持久化存儲

**設計決策：**
- **存儲格式：** JSON 檔案（參考 `worker_b_src`）
- **用戶標識符：** UUID（與 Worker B 一致）
- **密碼處理：** bcrypt 哈希（與 Worker B 一致）
- **檔案名稱：** `users_a.json`（可配置為共享 `users_b.json`）

**資料結構：**
```json
{
  "users": [
    {
      "id": "uuid",
      "username": "string",
      "password_hash": "string",
      "created_at": "ISO 8601 string"
    }
  ]
}
```

**關鍵方法：**
- `get_user_by_username(username)` - 根據用戶名查找用戶
- `get_user_by_id(user_id)` - 根據 UUID 查找用戶
- `username_exists(username)` - 檢查用戶名是否存在
- `verify_password(username, password)` - 驗證密碼

#### 2. JWTTokenManager

**職責：** JWT 令牌的生成和驗證

**設計決策：**
- **令牌類型：** JWT（無狀態令牌）
- **算法：** HS256
- **過期時間：** 24 小時（可配置）
- **令牌載荷：** 包含 `user_id` 和 `username`

**關鍵方法：**
- `generate_token(user_id, username)` - 生成 JWT token
- `verify_token(token)` - 驗證並提取用戶資訊

#### 3. AuthService

**職責：** 協調用戶登錄流程，提供業務邏輯層

**設計決策：**
- **登錄驗證：** 使用 `FileBasedUserStorage` 驗證憑證
- **令牌生成：** 登錄成功後自動生成 JWT token
- **錯誤處理：** 清晰的錯誤訊息返回

**關鍵方法：**
- `login(username, password)` - 用戶登錄並獲取 token
- `verify_token(token)` - 驗證 token
- `get_user_by_token(token)` - 從 token 獲取用戶資訊

### 待辦事項系統設計

#### 1. FileBasedTodoStorage

**職責：** 管理待辦事項資料的持久化存儲

**設計決策：**
- **存儲格式：** JSON 檔案
- **待辦事項標識符：** UUID
- **用戶關聯：** 透過 `user_id`（UUID）關聯
- **檔案名稱：** `todos_a.json`

**資料結構：**
```json
{
  "todos": [
    {
      "id": "uuid",
      "content": "string",
      "user_id": "uuid",
      "created_at": "ISO 8601 string"
    }
  ]
}
```

**關鍵方法：**
- `create_todo(content, user_id)` - 創建待辦事項
- `get_todos_by_user_id(user_id)` - 獲取用戶的所有待辦事項
- `get_todo_by_id(todo_id)` - 根據 ID 獲取待辦事項

#### 2. TodoService

**職責：** 協調待辦事項管理流程，提供業務邏輯層

**設計決策：**
- **輸入驗證：** 內容不能為空，長度限制 1-1000 字符
- **用戶驗證：** 必須提供有效的 `user_id`
- **錯誤處理：** 清晰的錯誤訊息返回

**關鍵方法：**
- `create_todo(content, user_id)` - 創建待辦事項（帶驗證）
- `list_todos(user_id)` - 列出用戶的所有待辦事項
- `validate_content(content)` - 驗證內容格式

### HTTP API 設計

#### 認證端點

**POST `/api/login`**
- **描述：** 用戶登錄
- **認證：** 不需要
- **請求體：** `{"username": "string", "password": "string"}`
- **響應：** `{"user": {...}, "token": "jwt_token"}`

**GET `/api/me`**
- **描述：** 獲取當前用戶資訊
- **認證：** 需要（Bearer token）
- **響應：** `{"user": {...}}`

#### 待辦事項端點

**POST `/api/todos`**
- **描述：** 創建待辦事項
- **認證：** 需要（Bearer token）
- **請求體：** `{"content": "string"}`
- **響應：** `{"todo": {...}}`

**GET `/api/todos`**
- **描述：** 列出當前用戶的所有待辦事項
- **認證：** 需要（Bearer token）
- **響應：** `{"todos": [...]}`

## 實現細節

### 認證中間件

使用 Flask 裝飾器 `@require_auth` 實現認證中間件：

```python
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 從 Authorization header 提取 token
        # 驗證 token
        # 將用戶資訊添加到 request context
        return f(*args, **kwargs)
    return decorated_function
```

### 用戶上下文

認證後，用戶資訊存儲在 Flask request 對象中：
- `request.current_user` - 用戶名
- `request.current_user_id` - 用戶 UUID

### 錯誤處理

所有 API 端點都遵循統一的錯誤格式：
```json
{
  "error": "error message"
}
```

HTTP 狀態碼：
- `200` - 成功
- `201` - 創建成功
- `400` - 客戶端錯誤（無效輸入）
- `401` - 未認證或認證失敗
- `404` - 資源不存在

## 與 Worker B 的整合

### 用戶存儲共享

Worker A 的認證系統遵循 Worker B 的設計模式，可以共享用戶存儲：

1. **開發環境**：可以配置 Worker A 使用 `users_b.json`
   ```python
   auth_service = AuthService(storage_file="users_b.json")
   ```

2. **生產環境**：建議使用共享的用戶存儲文件或資料庫

### 一致性保證

- **用戶標識符**：都使用 UUID
- **密碼哈希**：都使用 bcrypt
- **令牌格式**：都使用 JWT（但 secret key 不同）

## 探索記錄

### 考慮過的方案

#### 認證存儲選項
- ✅ **選擇：檔案基礎用戶存儲（file-based user storage）**
  - 提供持久化能力
  - 與 Worker B 保持一致
  - 適合簡單應用場景

- ❌ **未選擇：內存用戶映射（in-memory user map）**
  - 無持久化能力
  - 不適合實際應用

#### 會話處理選項
- ✅ **選擇：無狀態令牌（stateless tokens - JWT）**
  - 無需服務器端會話存儲
  - 適合分散式系統
  - 與 Worker B 保持一致

- ❌ **未選擇：內存會話映射（in-memory session map）**
  - 不適合多實例部署
  - 需要服務器端存儲

#### 待辦事項存儲選項
- ✅ **選擇：JSON 檔案持久化（JSON file persistence）**
  - 提供持久化能力
  - 簡單易用
  - 適合小型應用

- ❌ **未選擇：內存列表（in-memory lists）**
  - 無持久化能力
  - 重啟後資料丟失

### 設計原則

1. **一致性**：遵循 Worker B 的設計模式，確保系統間的一致性
2. **分離關注點**：認證和待辦事項功能明確分離
3. **簡單性**：優先選擇簡單、易維護的方案
4. **可擴展性**：為未來的擴展預留空間（如更換存儲方案）

## 未來改進方向

1. **資料庫支持**：考慮支援 SQLite 或 PostgreSQL
2. **API 版本控制**：引入 API 版本號（如 `/api/v1/`）
3. **日誌記錄**：添加結構化日誌
4. **單元測試**：添加完整的單元測試套件
5. **API 文檔**：使用 Swagger/OpenAPI 生成 API 文檔