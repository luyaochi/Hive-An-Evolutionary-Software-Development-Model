/**
 * Worker A API Client
 * 提供與後端 API 通信的客戶端功能
 * 支援 Worker A 和 Worker B 兩種後台格式
 */

class WorkerAApi {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('auth_token') || null;
        // 檢測後台類型（Worker A 或 Worker B）
        this.backendType = this.detectBackendType();
    }

    /**
     * 檢測後台類型
     * 通過檢查 API 響應格式來判斷是 Worker A 還是 Worker B
     */
    detectBackendType() {
        // 優先使用存儲的類型，否則根據端口推測
        const storedType = localStorage.getItem('backend_type');
        if (storedType) {
            return storedType;
        }
        // 根據端口推測：5000=Worker A, 5001=Worker B
        if (this.baseUrl.includes(':5001')) {
            return 'worker_b';
        }
        return 'worker_a';
    }

    /**
     * 設置後台類型
     */
    setBackendType(type) {
        this.backendType = type;
        localStorage.setItem('backend_type', type);
    }

    /**
     * 設置認證令牌
     */
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('auth_token', token);
        } else {
            localStorage.removeItem('auth_token');
        }
    }

    /**
     * 獲取認證令牌
     */
    getToken() {
        return this.token || localStorage.getItem('auth_token');
    }

    /**
     * 清除認證令牌
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    /**
     * 發送 HTTP 請求
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // 如果有令牌，添加到請求頭
        const token = this.getToken();
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * 註冊新用戶
     * 適配 Worker A 和 Worker B 的不同響應格式
     */
    async register(username, password) {
        const response = await this.request('/api/register', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        // Worker B 返回 {user, token}，Worker A 返回 {message}
        if (response.token) {
            // Worker B 格式：直接返回 token
            this.setToken(response.token);
            this.setBackendType('worker_b');
            return response;
        } else if (response.message) {
            // Worker A 格式：只有成功訊息，需要登錄獲取 token
            this.setBackendType('worker_a');
            return response;
        }

        return response;
    }

    /**
     * 用戶登錄
     * 適配 Worker A 和 Worker B 的不同響應格式
     */
    async login(username, password) {
        const response = await this.request('/api/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        // Worker B 返回 {user, token}，Worker A 返回 {token}
        if (response.token) {
            this.setToken(response.token);

            // 檢測後台類型
            if (response.user) {
                // Worker B 格式：包含 user 對象
                this.setBackendType('worker_b');
            } else {
                // Worker A 格式：只有 token
                this.setBackendType('worker_a');
            }

            return response;
        }

        return response;
    }

    /**
     * 獲取當前用戶資訊（僅 Worker B 支持）
     */
    async getCurrentUser() {
        try {
            return await this.request('/api/me', {
                method: 'GET'
            });
        } catch (error) {
            // Worker A 沒有這個端點，返回 null
            return null;
        }
    }

    /**
     * 創建待辦事項（僅 Worker A 支持）
     */
    async createTodo(content) {
        // Worker B 沒有待辦事項功能
        if (this.backendType === 'worker_b') {
            throw new Error('待辦事項功能僅在 Worker A 後台中可用');
        }

        return await this.request('/api/todos', {
            method: 'POST',
            body: JSON.stringify({ content })
        });
    }

    /**
     * 獲取所有待辦事項（僅 Worker A 支持）
     */
    async getTodos() {
        // Worker B 沒有待辦事項功能
        if (this.backendType === 'worker_b') {
            throw new Error('待辦事項功能僅在 Worker A 後台中可用');
        }

        return await this.request('/api/todos', {
            method: 'GET'
        });
    }

    /**
     * 檢查是否支持待辦事項功能
     */
    supportsTodos() {
        return this.backendType === 'worker_a';
    }

    /**
     * 獲取後台類型
     */
    getBackendType() {
        return this.backendType;
    }

    /**
     * 健康檢查
     */
    async healthCheck() {
        return await this.request('/health', {
            method: 'GET'
        });
    }
}

// 創建全局 API 實例
const api = new WorkerAApi();
