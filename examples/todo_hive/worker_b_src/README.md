# Worker B 源代碼

這是 Worker B 實現的用戶註冊功能，採用檔案基礎存儲方案。

## 目錄結構

```
Worker_b_src/
├── README.md                  # 本文件
├── DESIGN.md                  # 設計文檔
└── auth/
    ├── __init__.py            # 模組初始化
    ├── user_storage.py        # 檔案基礎用戶存儲
    └── registration_service.py # 註冊服務
```

## 功能

- 用戶註冊（User Registration）
- 用戶登錄（User Login）
- JWT token 生成和驗證
- 使用 UUID 作為用戶標識符
- JSON 檔案持久化存儲
- bcrypt 密碼哈希
- 用戶名和密碼驗證
- 完整的 HTTP REST API

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 啟動 HTTP API 服務

```bash
python app.py
```

服務將在 `http://localhost:5001` 啟動。

### 使用 HTTP API

#### 註冊用戶

```bash
curl -X POST http://localhost:5001/api/register \
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

#### 登錄用戶

```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

#### 獲取當前用戶資訊

```bash
curl -X GET http://localhost:5001/api/me \
  -H "Authorization: Bearer <your_token>"
```

### Python 程式碼使用

```python
from auth import AuthService

# 初始化認證服務
service = AuthService(storage_file="users_b.json")

# 註冊新用戶並獲取 JWT token
success, response_data, error = service.register("alice", "password123")

if success:
    user = response_data['user']
    token = response_data['token']
    print(f"User registered: {user['id']} - {user['username']}")
    print(f"JWT Token: {token}")
else:
    print(f"Registration failed: {error}")
```

### 驗證用戶名和密碼

```python
from auth import RegistrationService

service = RegistrationService()

# 驗證用戶名
is_valid, error = service.validate_username("alice")
if not is_valid:
    print(f"Username validation failed: {error}")

# 驗證密碼
is_valid, error = service.validate_password("password123")
if not is_valid:
    print(f"Password validation failed: {error}")
```

### 直接使用用戶存儲

```python
from auth import FileBasedUserStorage

storage = FileBasedUserStorage(storage_file="users_b.json")

# 註冊用戶
user = storage.register_user("bob", "mypassword")

# 檢查用戶是否存在
if storage.username_exists("bob"):
    print("User exists")

# 驗證密碼
if storage.verify_password("bob", "mypassword"):
    print("Password correct")

# 根據用戶名獲取用戶
user = storage.get_user_by_username("bob")

# 根據 UUID 獲取用戶
user = storage.get_user_by_id(user['id'])
```

## 依賴

- Python 3.6+
- bcrypt（用於密碼哈希）

安裝 bcrypt：
```bash
pip install bcrypt
```

## 資料結構

用戶資料存儲在 JSON 檔案中，格式如下：

```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "alice",
      "password_hash": "$2b$12$...",
      "created_at": "2024-01-01T00:00:00.000000"
    }
  ]
}
```

## 設計決策

詳細的設計決策和理由請參考 [DESIGN.md](DESIGN.md)。

主要設計決策：
- **UUID 作為用戶標識符**：符合 `decision.md` 的決策
- **JSON 檔案持久化**：符合 `decision.md` 的決策
- **bcrypt 密碼哈希**：業界標準的安全選擇

## 與 Worker A 的差異

- Worker B 使用 UUID 作為用戶標識符，Worker A 使用用戶名作為主鍵
- Worker B 使用用戶列表（數組）結構，Worker A 使用用戶名映射（字典）
- Worker B 專注於註冊功能，Worker A 實現了登錄和 Todo 管理

詳細比較請參考 [DESIGN.md](DESIGN.md)。

## API 端點

- `POST /api/register` - 註冊新用戶，返回 JWT token
- `POST /api/login` - 用戶登錄，返回 JWT token
- `GET /api/me` - 獲取當前用戶資訊（需要認證）
- `POST /api/verify-token` - 驗證 JWT token
- `GET /health` - 健康檢查
- `GET /` - API 資訊

詳細的 API 文檔請參考 [DESIGN.md](DESIGN.md)。

## 注意事項

- 預設儲存檔案名為 `users_b.json`（避免與 Worker A 的 `users.json` 衝突）
- 服務運行在端口 5001（避免與 Worker A 的 5000 衝突）
- 密碼使用 bcrypt 進行哈希，安全性高
- JWT token 預設有效期為 24 小時
- 用戶名必須唯一
- 用戶名長度限制：3-50 字符
- 密碼長度限制：6-100 字符
- 註冊成功後自動返回 JWT token，可直接用於後續 API 調用

## 授權

MIT License
