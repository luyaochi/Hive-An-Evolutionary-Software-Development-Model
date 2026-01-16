# Worker A 源代碼

這是 Worker A 實現的用戶登錄和待辦事項管理功能。

## 目錄結構

```
worker_a_src/
├── README.md                  # 本文件
├── DESIGN.md                  # 設計文檔
├── app.py                     # Flask HTTP API 應用
├── requirements.txt           # Python 依賴
├── auth/                      # 認證模組
│   ├── __init__.py
│   ├── user_storage.py        # 檔案基礎用戶存儲
│   ├── token_manager.py       # JWT token 管理
│   └── auth_service.py        # 認證服務（登錄和 JWT）
└── todos/                     # 待辦事項模組
    ├── __init__.py
    ├── todo_storage.py        # 檔案基礎待辦事項存儲
    └── todo_service.py        # 待辦事項服務
```

## 功能

### 認證功能
- 用戶登錄（User Login）
- JWT token 生成和驗證
- 使用 UUID 作為用戶標識符
- JSON 檔案持久化存儲
- bcrypt 密碼哈希

### 待辦事項功能
- 創建待辦事項（Create todo items）
- 列出待辦事項（List todo items）
- 待辦事項與已認證用戶關聯
- JSON 檔案持久化存儲
- UUID 作為待辦事項標識符

## 設計決策

### 認證系統
遵循 `worker_b_src` 的設計模式：
- **用戶存儲**：JSON 檔案基礎存儲（`users_a.json`）
- **認證方式**：JWT 無狀態令牌
- **密碼處理**：bcrypt 哈希
- **用戶標識符**：UUID

### 待辦事項系統
- **存儲方案**：JSON 檔案基礎存儲（`todos_a.json`）
- **標識符**：UUID
- **操作**：僅支援創建和列出（無更新或刪除）
- **用戶關聯**：透過 `user_id` 關聯已認證用戶

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動 HTTP API 服務

```bash
python app.py
```

服務將在 `http://localhost:5000` 啟動。

**注意**：用戶需要先通過 `worker_b_src` 的註冊功能創建帳號，然後使用該帳號在此服務中登錄。

## 使用 HTTP API

### 登錄用戶

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

響應：
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "alice",
    "created_at": "2024-01-01T00:00:00.000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 獲取當前用戶資訊

```bash
curl -X GET http://localhost:5000/api/me \
  -H "Authorization: Bearer <your_token>"
```

### 創建待辦事項

```bash
curl -X POST http://localhost:5000/api/todos \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "完成專案報告"}'
```

響應：
```json
{
  "todo": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "content": "完成專案報告",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2024-01-01T12:00:00.000000"
  }
}
```

### 列出待辦事項

```bash
curl -X GET http://localhost:5000/api/todos \
  -H "Authorization: Bearer <your_token>"
```

響應：
```json
{
  "todos": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "content": "完成專案報告",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2024-01-01T12:00:00.000000"
    }
  ]
}
```

## Python 程式碼使用

### 認證服務

```python
from auth import AuthService

# 初始化認證服務
auth_service = AuthService(storage_file="users_a.json")

# 登錄用戶並獲取 JWT token
success, response_data, error = auth_service.login("alice", "password123")

if success:
    user = response_data['user']
    token = response_data['token']
    print(f"登錄成功！用戶：{user['username']}, Token: {token}")
else:
    print(f"登錄失敗：{error}")

# 驗證 token
user_info = auth_service.verify_token(token)
if user_info:
    print(f"Token 有效，用戶：{user_info['username']}")
```

### 待辦事項服務

```python
from todos import TodoService

# 初始化待辦事項服務
todo_service = TodoService(storage_file="todos_a.json")

# 創建待辦事項
success, todo_data, error = todo_service.create_todo(
    "完成專案報告",
    user_id="550e8400-e29b-41d4-a716-446655440000"
)

if success:
    print(f"待辦事項創建成功：{todo_data['content']}")
else:
    print(f"創建失敗：{error}")

# 列出用戶的所有待辦事項
success, todos_list, error = todo_service.list_todos(
    user_id="550e8400-e29b-41d4-a716-446655440000"
)

if success:
    print(f"共有 {len(todos_list)} 個待辦事項")
    for todo in todos_list:
        print(f"  - {todo['content']} ({todo['created_at']})")
```

## 與 Worker B 的整合

Worker A 使用與 Worker B 相同的用戶存儲格式，但使用不同的文件名：
- Worker B：`users_b.json`（用於註冊）
- Worker A：`users_a.json`（用於登錄）

**重要**：為了讓 Worker A 能夠登錄 Worker B 註冊的用戶，需要確保兩個服務使用相同的用戶存儲文件。可以通過以下方式實現：

1. **共享用戶文件**：配置 Worker A 使用 `users_b.json`（在初始化時指定）
   ```python
   auth_service = AuthService(storage_file="users_b.json")
   ```

2. **複製用戶文件**：在開發環境中複製 `users_b.json` 到 `users_a.json`

## API 端點摘要

| 方法 | 端點 | 認證 | 描述 |
|------|------|------|------|
| POST | `/api/login` | 否 | 用戶登錄 |
| GET | `/api/me` | 是 | 獲取當前用戶資訊 |
| POST | `/api/todos` | 是 | 創建待辦事項 |
| GET | `/api/todos` | 是 | 列出待辦事項 |
| GET | `/health` | 否 | 健康檢查 |
| GET | `/` | 否 | API 資訊 |