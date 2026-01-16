"""
使用範例：演示如何使用 Worker B 的認證服務

這個腳本展示了如何：
1. 註冊新用戶並獲取 JWT token
2. 登錄用戶並獲取 JWT token
3. 驗證 JWT token
4. 使用 token 獲取用戶資訊
"""

from auth import AuthService


def main():
    # 初始化認證服務
    auth_service = AuthService(storage_file="users_b.json")

    print("=== Worker B 認證服務使用範例 ===\n")

    # 1. 註冊新用戶
    print("1. 註冊新用戶...")
    success, response_data, error = auth_service.register("demo_user", "demo_password123")

    if success:
        user = response_data['user']
        token = response_data['token']
        print(f"   ✓ 註冊成功！")
        print(f"   - 用戶 ID: {user['id']}")
        print(f"   - 用戶名: {user['username']}")
        print(f"   - 創建時間: {user['created_at']}")
        print(f"   - JWT Token: {token[:50]}...")
    else:
        print(f"   ✗ 註冊失敗: {error}")

    print()

    # 2. 嘗試登錄
    print("2. 登錄用戶...")
    success, response_data, error = auth_service.login("demo_user", "demo_password123")

    if success:
        user = response_data['user']
        token = response_data['token']
        print(f"   ✓ 登錄成功！")
        print(f"   - 用戶名: {user['username']}")
        print(f"   - JWT Token: {token[:50]}...")
    else:
        print(f"   ✗ 登錄失敗: {error}")

    print()

    # 3. 驗證 token
    if success:
        print("3. 驗證 JWT token...")
        user_info = auth_service.verify_token(token)
        if user_info:
            print(f"   ✓ Token 有效！")
            print(f"   - 用戶 ID: {user_info['user_id']}")
            print(f"   - 用戶名: {user_info['username']}")
        else:
            print(f"   ✗ Token 無效或已過期")

        print()

        # 4. 使用 token 獲取用戶資訊
        print("4. 使用 token 獲取完整用戶資訊...")
        user = auth_service.get_user_by_token(token)
        if user:
            print(f"   ✓ 獲取成功！")
            print(f"   - 用戶 ID: {user['id']}")
            print(f"   - 用戶名: {user['username']}")
            print(f"   - 創建時間: {user['created_at']}")
        else:
            print(f"   ✗ 獲取失敗")

    print("\n=== 範例完成 ===")
    print("\n提示：")
    print("- 可以使用 HTTP API 測試：python app.py")
    print("- 然後使用 curl 或 Postman 測試 API 端點")
    print("- 詳細文檔請參考 README.md 和 DESIGN.md")


if __name__ == '__main__':
    main()
