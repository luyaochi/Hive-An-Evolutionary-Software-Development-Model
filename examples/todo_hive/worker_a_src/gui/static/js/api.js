/**
 * Worker A API Client
 * 處理與 Worker A 後端 API 的所有通信
 */

class WorkerAApi {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('worker_a_token') || null;
    }

    /**
     * 設置認證令牌
     */
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('worker_a_token', token);
        } else {
            localStorage.removeItem('worker_a_token');
        }
    }

    /**
     * 清除認證令牌
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('worker_a_token');
    }

    /**
     * 獲取認證 headers
     */
    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    /**
     * 處理 API 響應
     */
    async handleResponse(response) {
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    }

    /**
     * 登錄用戶
     * @param {string} username - 用戶名
     * @param {string} password - 密碼
     * @returns {Promise<Object>} 包含用戶資訊和令牌的對象
     */
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await this.handleResponse(response);
        
        // 保存令牌
        if (data.token) {
            this.setToken(data.token);
        }
        
        return data;
    }

    /**
     * 獲取當前用戶資訊
     * @returns {Promise<Object>} 用戶資訊
     */
    async getCurrentUser() {
        const response = await fetch(`${this.baseUrl}/api/me`, {
            method: 'GET',
            headers: this.getAuthHeaders()
        });

        return await this.handleResponse(response);
    }

    /**
     * 創建待辦事項
     * @param {string} content - 待辦事項內容
     * @returns {Promise<Object>} 創建的待辦事項
     */
    async createTodo(content) {
        const response = await fetch(`${this.baseUrl}/api/todos`, {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({ content })
        });

        return await this.handleResponse(response);
    }

    /**
     * 獲取所有待辦事項
     * @returns {Promise<Array>} 待辦事項列表
     */
    async listTodos() {
        const response = await fetch(`${this.baseUrl}/api/todos`, {
            method: 'GET',
            headers: this.getAuthHeaders()
        });

        const data = await this.handleResponse(response);
        return data.todos || [];
    }

    /**
     * 驗證令牌是否有效
     * @returns {Promise<boolean>} 令牌是否有效
     */
    async verifyToken() {
        if (!this.token) {
            return false;
        }

        try {
            await this.getCurrentUser();
            return true;
        } catch (error) {
            this.clearToken();
            return false;
        }
    }
}

// 創建全局 API 實例
const api = new WorkerAApi();