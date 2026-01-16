/**
 * Worker A GUI 主應用程式
 * 處理用戶界面邏輯和狀態管理，包含認證和待辦事項管理
 */

class WorkerAApp {
    constructor() {
        this.currentView = 'login'; // 'login', 'register', 'dashboard'
        this.currentUser = null;
        this.todos = [];
        this.init();
    }

    /**
     * 初始化應用
     */
    async init() {
        // 檢查是否已有登錄令牌
        const token = api.getToken();
        if (token) {
            try {
                const backendType = api.getBackendType();

                if (backendType === 'worker_a') {
                    // Worker A: 嘗試獲取待辦事項來驗證令牌
                    const todosData = await api.getTodos();
                    if (todosData && todosData.todos !== undefined) {
                        this.todos = todosData.todos;
                        // 從第一個待辦事項獲取用戶名（如果有的話）
                        if (this.todos.length > 0) {
                            this.currentUser = this.todos[0].user_id;
                        }
                        this.showDashboard();
                        return;
                    }
                } else if (backendType === 'worker_b') {
                    // Worker B: 嘗試獲取用戶資訊來驗證令牌
                    const userData = await api.getCurrentUser();
                    if (userData && userData.user) {
                        this.currentUser = userData.user.username;
                        this.showDashboard();
                        return;
                    }
                }
            } catch (error) {
                // 令牌無效，清除並顯示登錄頁面
                console.error('Token validation failed:', error);
                api.clearToken();
            }
        }

        this.showLogin();
        this.setupEventListeners();
    }

    /**
     * 設置事件監聽器
     */
    setupEventListeners() {
        // 登錄表單
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // 註冊表單
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // 表單切換
        const showRegisterLink = document.getElementById('showRegister');
        if (showRegisterLink) {
            showRegisterLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRegister();
            });
        }

        const showLoginLink = document.getElementById('showLogin');
        if (showLoginLink) {
            showLoginLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.showLogin();
            });
        }

        // 登出按鈕
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // 創建待辦事項表單
        const todoForm = document.getElementById('todoForm');
        if (todoForm) {
            todoForm.addEventListener('submit', (e) => this.handleCreateTodo(e));
        }

        // 刷新待辦事項按鈕
        const refreshTodosBtn = document.getElementById('refreshTodosBtn');
        if (refreshTodosBtn) {
            refreshTodosBtn.addEventListener('click', () => this.loadTodos());
        }
    }

    /**
     * 顯示登錄頁面
     */
    showLogin() {
        this.currentView = 'login';
        document.getElementById('loginView').classList.remove('hidden');
        document.getElementById('registerView').classList.add('hidden');
        document.getElementById('dashboardView').classList.add('hidden');
        this.clearAlerts();
    }

    /**
     * 顯示註冊頁面
     */
    showRegister() {
        this.currentView = 'register';
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('registerView').classList.remove('hidden');
        document.getElementById('dashboardView').classList.add('hidden');
        this.clearAlerts();
    }

    /**
     * 顯示儀表板
     */
    async showDashboard() {
        this.currentView = 'dashboard';
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('registerView').classList.add('hidden');
        document.getElementById('dashboardView').classList.remove('hidden');

        // 檢查後台類型
        const backendType = api.getBackendType();
        const supportsTodos = api.supportsTodos();

        // 顯示/隱藏待辦事項功能（Worker B 不支持）
        const todoSection = document.querySelector('.todo-section');
        if (todoSection) {
            todoSection.style.display = supportsTodos ? 'block' : 'none';
        }

        // 顯示用戶名
        if (this.currentUser) {
            const usernameElement = document.getElementById('dashboardUsername');
            if (usernameElement) {
                usernameElement.textContent = this.currentUser;
            }
            const headerUsername = document.getElementById('headerUsername');
            if (headerUsername) {
                headerUsername.textContent = this.currentUser;
            }
        } else {
            // Worker B: 嘗試從 API 獲取用戶資訊
            if (backendType === 'worker_b') {
                try {
                    const userData = await api.getCurrentUser();
                    if (userData && userData.user) {
                        this.currentUser = userData.user.username;
                        const usernameElement = document.getElementById('dashboardUsername');
                        if (usernameElement) {
                            usernameElement.textContent = this.currentUser;
                        }
                        const headerUsername = document.getElementById('headerUsername');
                        if (headerUsername) {
                            headerUsername.textContent = this.currentUser;
                        }
                    }
                } catch (error) {
                    console.error('Failed to get user info:', error);
                }
            }
        }

        // 顯示標題欄用戶資訊
        const headerUserInfo = document.getElementById('headerUserInfo');
        if (headerUserInfo) {
            headerUserInfo.style.display = 'flex';
        }

        // 只有在 Worker A 時才載入待辦事項
        if (supportsTodos) {
            await this.loadTodos();
        }
    }

    /**
     * 處理登錄
     */
    async handleLogin(e) {
        e.preventDefault();
        this.clearAlerts();

        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;

        if (!username || !password) {
            this.showAlert('請輸入用戶名和密碼', 'error');
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoading(submitBtn, true);

        try {
            const response = await api.login(username, password);

            if (response.token) {
                // 已由 api.login() 設置 token
                // Worker B 返回 user 對象，Worker A 只有 token
                if (response.user) {
                    // Worker B 格式
                    this.currentUser = response.user.username;
                } else {
                    // Worker A 格式
                    this.currentUser = username;
                }

                this.showAlert('登錄成功！', 'success');

                // 延遲顯示儀表板，讓用戶看到成功訊息
                setTimeout(() => {
                    this.showDashboard();
                }, 1000);
            }
        } catch (error) {
            this.showAlert(error.message || '登錄失敗，請檢查用戶名和密碼', 'error');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    /**
     * 處理註冊
     */
    async handleRegister(e) {
        e.preventDefault();
        this.clearAlerts();

        const username = document.getElementById('registerUsername').value.trim();
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('registerConfirmPassword').value;

        // 驗證輸入
        if (!username || !password) {
            this.showAlert('請輸入用戶名和密碼', 'error');
            return;
        }

        if (username.length < 3 || username.length > 50) {
            this.showAlert('用戶名長度必須在 3-50 字符之間', 'error');
            return;
        }

        if (password.length < 6 || password.length > 100) {
            this.showAlert('密碼長度必須在 6-100 字符之間', 'error');
            return;
        }

        if (password !== confirmPassword) {
            this.showAlert('兩次輸入的密碼不一致', 'error');
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoading(submitBtn, true);

        try {
            const response = await api.register(username, password);

            // Worker B 註冊後直接返回 token，可以直接登錄
            if (response.token) {
                // Worker B 格式：已自動設置 token
                this.currentUser = response.user ? response.user.username : username;
                this.showAlert('註冊成功！', 'success');

                // 延遲顯示儀表板
                setTimeout(() => {
                    this.showDashboard();
                }, 1000);
            } else {
                // Worker A 格式：只有成功訊息，需要登錄
                this.showAlert('註冊成功！請登錄', 'success');

                // 延遲顯示登錄頁面
                setTimeout(() => {
                    this.showLogin();
                    // 預填用戶名
                    document.getElementById('loginUsername').value = username;
                }, 1500);
            }
        } catch (error) {
            this.showAlert(error.message || '註冊失敗，用戶名可能已存在', 'error');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    /**
     * 處理登出
     */
    handleLogout() {
        api.clearToken();
        this.currentUser = null;
        this.todos = [];
        this.showLogin();
        this.showAlert('已成功登出', 'info');
    }

    /**
     * 載入待辦事項
     */
    async loadTodos() {
        try {
            const todosData = await api.getTodos();
            if (todosData && todosData.todos) {
                this.todos = todosData.todos;
                this.renderTodos();
            }
        } catch (error) {
            console.error('Failed to load todos:', error);
            this.showAlert('無法載入待辦事項', 'error');
        }
    }

    /**
     * 處理創建待辦事項
     */
    async handleCreateTodo(e) {
        e.preventDefault();
        this.clearAlerts();

        const contentInput = document.getElementById('todoContent');
        const content = contentInput.value.trim();

        if (!content) {
            this.showAlert('請輸入待辦事項內容', 'error');
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoading(submitBtn, true);

        try {
            const newTodo = await api.createTodo(content);
            this.showAlert('待辦事項創建成功！', 'success');
            contentInput.value = '';

            // 重新載入待辦事項列表
            await this.loadTodos();
        } catch (error) {
            this.showAlert(error.message || '創建待辦事項失敗', 'error');
        } finally {
            this.setLoading(submitBtn, false);
        }
    }

    /**
     * 渲染待辦事項列表
     */
    renderTodos() {
        const todosContainer = document.getElementById('todosList');
        if (!todosContainer) return;

        // 更新計數
        const todosCount = document.getElementById('todosCount');
        if (todosCount) {
            todosCount.textContent = `${this.todos.length} 項`;
        }

        if (this.todos.length === 0) {
            todosContainer.innerHTML = `
                <div class="empty-state">
                    <p>📝 還沒有待辦事項</p>
                    <p class="empty-hint">創建您的第一個待辦事項吧！</p>
                </div>
            `;
            return;
        }

        // 按創建時間倒序排列
        const sortedTodos = [...this.todos].sort((a, b) => {
            return new Date(b.created_at) - new Date(a.created_at);
        });

        todosContainer.innerHTML = sortedTodos.map(todo => {
            const date = new Date(todo.created_at);
            const formattedDate = date.toLocaleString('zh-TW');

            return `
                <div class="todo-item">
                    <div class="todo-content">
                        <p class="todo-text">${this.escapeHtml(todo.content)}</p>
                        <span class="todo-date">${formattedDate}</span>
                    </div>
                    <div class="todo-id">ID: ${todo.id.substring(0, 8)}...</div>
                </div>
            `;
        }).join('');
    }

    /**
     * HTML 轉義，防止 XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 顯示提示訊息
     */
    showAlert(message, type = 'info') {
        this.clearAlerts();

        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;

        alertContainer.appendChild(alert);

        // 3 秒後自動清除
        setTimeout(() => {
            alert.remove();
        }, 3000);
    }

    /**
     * 清除所有提示訊息
     */
    clearAlerts() {
        const alertContainer = document.getElementById('alertContainer');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }
    }

    /**
     * 設置按鈕加載狀態
     */
    setLoading(button, loading) {
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> 處理中...';
        } else {
            button.disabled = false;
            // 恢復原始文本
            if (button.closest('#loginForm')) {
                button.innerHTML = '登錄';
            } else if (button.closest('#registerForm')) {
                button.innerHTML = '註冊';
            } else if (button.closest('#todoForm')) {
                button.innerHTML = '添加';
            }
        }
    }
}

// 當頁面加載完成時初始化應用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorkerAApp();
});
