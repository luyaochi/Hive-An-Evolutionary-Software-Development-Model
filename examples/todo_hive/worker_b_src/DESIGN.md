# Worker B 設計文檔

## 概述

本設計文檔描述 Worker B 實現的用戶註冊功能，採用檔案基礎存儲方案。

## 設計目標

根據 `worker_b.md` 的任務分配和 `decision.md` 的決策記錄，Worker B 負責實現：
- **User Registration（用戶註冊）**
- 使用 **JSON 檔案持久化**方案
- 使用 **UUID 作為用戶標識符**

## 架構設計

### 模組結構

```
Worker_b_src/
├── app.py                          # Flask HTTP API 應用
├── requirements.txt                # Python 依賴
├── README.md                       # 使用文檔
├── DESIGN.md                       # 本設計文檔
└── auth/
    ├── __init__.py                 # 模組初始化
    ├── user_storage.py             # 檔案基礎用戶存儲
    ├── registration_service.py     # 註冊服務
    ├── token_manager.py            # JWT token 管理
    └── auth_service.py             # 認證服務（整合註冊和 JWT）
```

### 核心組件

#### 1. FileBasedUserStorage

**職責：** 管理用戶資料的持久化存儲

**設計決策：**
- **存儲格式：** JSON 檔案
- **用戶標識符：** UUID（符合 `decision.md` 的要求）
- **密碼處理：** bcrypt 哈希
- **資料結構：**
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
- `register_user(username, password)` - 註冊新用戶，生成 UUID
- `get_user_by_username(username)` - 根據用戶名查找用戶
- `get_user_by_id(user_id)` - 根據 UUID 查找用戶
- `username_exists(username)` - 檢查用戶名是否存在
- `verify_password(username, password)` - 驗證密碼

#### 2. RegistrationService

**職責：** 協調用戶註冊流程，提供業務邏輯層

**設計決策：**
- **輸入驗證：** 用戶名和密碼的基本驗證
- **錯誤處理：** 清晰的錯誤訊息返回
- **安全性：** 返回用戶資料時排除密碼哈希

**關鍵方法：**
- `register(username, password)` - 註冊新用戶（主要入口）
- `validate_username(username)` - 驗證用戶名格式
- `validate_password(password)` - 驗證密碼格式

#### 3. JWTTokenManager

**職責：** 管理 JWT token 的生成和驗證

**設計決策：**
- **Token 格式：** JWT (JSON Web Token)
- **簽名算法：** HS256
- **Token 內容：** 包含 user_id (UUID) 和 username
- **過期時間：** 可配置（預設 24 小時）

**關鍵方法：**
- `generate_token(user_id, username)` - 生成 JWT token
- `verify_token(token)` - 驗證 token 並返回用戶資訊
- `is_token_valid(token)` - 檢查 token 是否有效
- `get_username_from_token(token)` - 從 token 提取用戶名
- `get_user_id_from_token(token)` - 從 token 提取用戶 ID

#### 4. AuthService

**職責：** 整合註冊服務和 JWT token 管理

**設計決策：**
- **註冊流程：** 註冊成功後自動生成 JWT token
- **登錄流程：** 驗證憑證後生成 JWT token
- **Token 驗證：** 提供統一的 token 驗證介面

**關鍵方法：**
- `register(username, password)` - 註冊用戶並返回 token
- `login(username, password)` - 登錄用戶並返回 token
- `verify_token(token)` - 驗證 token
- `get_user_by_token(token)` - 根據 token 獲取用戶資訊

#### 5. Flask API 應用 (app.py)

**職責：** 提供 HTTP API 端點

**設計決策：**
- **框架：** Flask
- **端口：** 5001（避免與 Worker A 衝突）
- **認證方式：** Bearer token（Authorization header）

**API 端點：**
- `POST /api/register` - 註冊新用戶，返回 JWT token
- `POST /api/login` - 用戶登錄，返回 JWT token
- `GET /api/me` - 獲取當前用戶資訊（需要認證）
- `POST /api/verify-token` - 驗證 JWT token
- `GET /health` - 健康檢查
- `GET /` - API 資訊

## 設計決策與理由

### 1. 使用 UUID 作為用戶標識符

**決策：** 每個用戶分配一個 UUID 作為唯一標識符

**理由：**
- ✅ 符合 `decision.md` 中 Queen 的決策
- ✅ UUID 是標準化的唯一標識符，避免衝突
- ✅ 不依賴外部系統（如資料庫自增 ID）
- ✅ 分散式友好，可遷移至分散式系統

**實作細節：**
- 使用 Python 標準庫 `uuid.uuid4()` 生成
- 存儲為字符串格式

### 2. JSON 檔案存儲

**決策：** 使用 JSON 檔案存儲用戶資料

**理由：**
- ✅ 符合 `decision.md` 中 Queen 的決策
- ✅ 使用標準格式，易於讀寫和調試
- ✅ 可漸進式遷移至資料庫
- ✅ 無需外部依賴（除了 bcrypt 用於安全）

**實作細節：**
- 檔案格式：UTF-8 編碼
- 格式化：縮排 2 空格，易於閱讀
- 檔案命名：`users_b.json`（避免與 Worker A 的檔案衝突）

### 3. bcrypt 密碼哈希

**決策：** 使用 bcrypt 進行密碼哈希

**理由：**
- ✅ 業界標準的密碼哈希算法
- ✅ 內建鹽值生成
- ✅ 可調整計算成本，對抗暴力破解
- ✅ 安全性高於簡單的哈希算法

**實作細節：**
- 使用 `bcrypt.hashpw()` 進行哈希
- 使用 `bcrypt.checkpw()` 進行驗證
- 密碼存儲時使用 `gensalt()` 自動生成鹽值

### 4. 資料結構設計

**決策：** 使用用戶列表結構，每個用戶包含完整資訊

**理由：**
- ✅ 結構清晰，易於理解
- ✅ 擴展性好，可輕鬆添加新欄位
- ✅ JSON 格式友好
- ✅ 符合 `decision.md` 中提到的資料結構模式

**欄位說明：**
- `id`: UUID，用戶唯一標識符
- `username`: 字符串，用戶名（唯一）
- `password_hash`: 字符串，bcrypt 哈希後的密碼
- `created_at`: ISO 8601 時間戳，用戶創建時間

### 5. 錯誤處理策略

**決策：** 返回 Tuple，包含成功標誌、資料和錯誤訊息

**理由：**
- ✅ 清晰的錯誤處理流程
- ✅ 便於調試和日誌記錄
- ✅ 符合 Python 慣例
- ✅ 易於擴展錯誤類型

**錯誤類型：**
- 用戶名已存在
- 用戶名或密碼為空
- 用戶名格式無效
- 密碼格式無效

## 探索過的替代方案

### 方案比較

#### 1. 用戶標識符策略

**考慮過的方案：**
- **方案 A：** 使用用戶名作為唯一標識符
  - ❌ 用戶名變更困難
  - ❌ 暴露業務邏輯（用戶名不可變）
  - ✅ 實現簡單

- **方案 B：** 使用自增整數 ID
  - ❌ 需要外部系統管理
  - ❌ 分散式環境下難以保證唯一性
  - ✅ 存儲空間小

- **方案 C：** 使用 UUID（**已選擇**）
  - ✅ 標準化唯一標識符
  - ✅ 分散式友好
  - ✅ 不依賴外部系統
  - ✅ 符合 `decision.md` 的決策

#### 2. 存儲格式策略

**考慮過的方案：**
- **方案 A：** 純文本檔案（每行一個用戶）
  - ❌ 結構化差
  - ❌ 難以查詢和更新
  - ✅ 簡單

- **方案 B：** CSV 檔案
  - ❌ 不適合嵌套資料
  - ❌ 密碼哈希需要特殊處理
  - ✅ 易於解析

- **方案 C：** JSON 檔案（**已選擇**）
  - ✅ 結構化良好
  - ✅ 標準格式
  - ✅ 易於讀寫和擴展
  - ✅ 符合 `decision.md` 的決策

#### 3. 密碼哈希策略

**考慮過的方案：**
- **方案 A：** MD5 或 SHA-256
  - ❌ 已被視為不安全
  - ❌ 易受彩虹表攻擊
  - ✅ 計算快速

- **方案 B：** PBKDF2
  - ✅ 安全
  - ❌ 需要更多配置
  - ✅ 標準算法

- **方案 C：** bcrypt（**已選擇**）
  - ✅ 業界標準
  - ✅ 內建鹽值
  - ✅ 可調整成本參數
  - ✅ 安全性高

## 與 Worker A 的差異

### 相同點
- 都使用 JSON 檔案存儲
- 都使用 bcrypt 進行密碼哈希
- 都採用檔案基礎存儲方案

### 不同點
- **用戶標識符：** Worker B 使用 UUID，Worker A 使用用戶名作為主鍵
- **資料結構：** Worker B 使用用戶列表（數組），Worker A 使用用戶名映射（字典）
- **檔案命名：** Worker B 使用 `users_b.json`，Worker A 使用 `users.json`
- **功能範圍：** Worker B 專注於註冊，Worker A 實現了登錄和 Todo 管理

## 演化性考量

### 未來可能的演進路徑

1. **存儲後端遷移：**
   - 當前：JSON 檔案
   - 未來可遷移至：SQLite、PostgreSQL、MongoDB 等
   - **演化阻力：** 低（資料結構保持不變）

2. **用戶標識符策略：**
   - 當前：UUID
   - 未來可保持：UUID 是標準化選擇
   - **演化阻力：** 無（已經是理想選擇）

3. **密碼哈希策略：**
   - 當前：bcrypt
   - 未來可遷移至：argon2、scrypt 等
   - **演化阻力：** 中等（需要遷移現有密碼哈希）

4. **驗證規則擴展：**
   - 當前：基本驗證
   - 未來可添加：複雜度要求、頻率限制等
   - **演化阻力：** 低（驗證邏輯獨立）

## 實現約束

根據 `README.md` 和 `decision.md`，以下決策已鎖定：

- ✅ Python 基礎實現
- ✅ HTTP 基礎 API（本實現提供核心邏輯，API 層需額外實現）
- ✅ 明確分離認證領域
- ✅ JSON 檔案持久化
- ✅ UUID 作為標識符

## HTTP API 設計

### API 端點

#### 1. 註冊用戶
```
POST /api/register
Content-Type: application/json

Request:
{
    "username": "alice",
    "password": "password123"
}

Response (201):
{
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "alice",
        "created_at": "2024-01-01T00:00:00.000000"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (400):
{
    "error": "Username already exists"
}
```

#### 2. 用戶登錄
```
POST /api/login
Content-Type: application/json

Request:
{
    "username": "alice",
    "password": "password123"
}

Response (200):
{
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "alice",
        "created_at": "2024-01-01T00:00:00.000000"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (401):
{
    "error": "Invalid credentials"
}
```

#### 3. 獲取當前用戶資訊
```
GET /api/me
Authorization: Bearer <token>

Response (200):
{
    "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "alice",
        "created_at": "2024-01-01T00:00:00.000000"
    }
}
```

#### 4. 驗證 Token
```
POST /api/verify-token
Content-Type: application/json

Request:
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200):
{
    "valid": true,
    "user": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "alice"
    }
}
```

### JWT Token 結構

JWT token 包含以下 payload：
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "alice",
    "iat": 1704067200,
    "exp": 1704153600
}
```

- `user_id`: 用戶 UUID
- `username`: 用戶名
- `iat`: 發行時間（issued at）
- `exp`: 過期時間（expiration）

## 使用範例

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

# 登錄用戶
success, response_data, error = service.login("alice", "password123")

if success:
    token = response_data['token']
    print(f"Login successful, token: {token}")
```

### HTTP API 使用

```bash
# 註冊用戶
curl -X POST http://localhost:5001/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

# 登錄用戶
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

# 獲取當前用戶資訊（需要 token）
curl -X GET http://localhost:5001/api/me \
  -H "Authorization: Bearer <token>"

# 驗證 token
curl -X POST http://localhost:5001/api/verify-token \
  -H "Content-Type: application/json" \
  -d '{"token": "<token>"}'
```

## 測試建議

建議的測試場景：

### 功能測試
1. 成功註冊新用戶並獲取 JWT token
2. 嘗試註冊已存在的用戶名
3. 空用戶名或密碼的驗證
4. 用戶名和密碼格式驗證
5. 密碼哈希和驗證的正確性
6. UUID 的唯一性

### API 測試
1. 註冊 API 端點測試
2. 登錄 API 端點測試
3. JWT token 生成和驗證
4. Token 過期處理
5. 無效 token 處理
6. 認證中間件測試（@require_auth）

### 安全測試
1. 密碼不會以明文形式返回
2. JWT token 簽名驗證
3. Token 過期時間檢查
4. 無效 token 拒絕訪問

## 運行方式

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 啟動服務
```bash
python app.py
```

服務將在 `http://localhost:5001` 啟動。

### 依賴項
- `flask==3.0.0`: HTTP 框架
- `bcrypt==4.0.1`: 密碼哈希
- `PyJWT==2.8.0`: JWT 令牌處理

## 總結

Worker B 的實現遵循了以下原則：
- ✅ 符合 `decision.md` 中 Queen 的決策
- ✅ 使用標準化的技術選擇（UUID、JSON、bcrypt、JWT）
- ✅ 保持演化性，不引入過早約束
- ✅ 清晰的錯誤處理和驗證
- ✅ 模組化設計，易於擴展
- ✅ 完整的 HTTP API 實現
- ✅ JWT token 自動生成和驗證

這個實現為未來的演進保留了充分的空間，不會過早約束系統的發展方向。註冊成功後自動返回 JWT token，方便前端直接使用。
