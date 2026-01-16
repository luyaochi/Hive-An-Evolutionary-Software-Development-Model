/**
 * Worker A GUI Application
 * 主應用邏輯，管理狀態和 UI 控制
 */

class WorkerAApp {
    constructor() {
        this.currentView = 'login';
        this.currentUser = null;
        this.todos = [];
        
        // DOM 元素引用
        this.elements = {
            // Views
            loginView: document.getElementById('login-view'),
            dashboardView: document.getElementById('dashboard-view'),
            
            // Login form
            loginForm: document.getElementById('login-form'),
            loginUsername: document.getElementById('login-username'),
            loginPassword: document.getElementById('login-password'),
            loginBtn: document.getElementById('login-btn'),
            
            // User info
            userInfo: document.getElementById('user-info'),
            usernameDisplay: document.getElementById('username-display'),
            logoutBtn: document.getElementById('logout-btn'),
            
            // Todo form
            addTodoForm: document.getElementById('add-todo-form'),
            todoContent: document.getElementById('todo-content'),
            addTodoBtn: document.getElementById('add-todo-btn'),
            charCount: document.getElementById('char-count'),
            
            // Todos list
            todosList: document.getElementById('todos-list'),
            emptyState: document.getElementById('empty-state'),
            refreshTodosBtn: document.getElementById('refresh-todos-btn'),
            
            // Alert container
            alertContainer: document.getElementById('alert-container')
        };

        this.init();
    }

    /**
     * 初始化應用
     */
    async init() {
        // 綁定事件監聽器
        this.bindEvents();

        // 檢查是否有有效的令牌
        const hasValidToken = await api.verifyToken();
        
        if (hasValidToken) {
            await this.loadUserInfo();
            this.showDashboard();
        } else {
            this.showLogin();
        }

        // 監聽字符計數
        this.elements.todoContent.addEventListener('input', () => {
            this.updateCharCount();
        });
    }

    /**
     * 綁定事件監聽器
     */
    bindEvents() {
        // 登錄表單
        this.elements.loginForm.addEventListener('submit', (e) => {
            this.handleLogin(e);
        });

        // 登出按鈕
        this.elements.logoutBtn.addEventListener('click', () => {
            this.handleLogout();
        });

        // 新增待辦事項表單
        this.elements.addTodoForm.addEventListener('submit', (e) => {
            this.handleAddTodo(e);
        });

        // 刷新待辦事項
        this.elements.refreshTodosBtn.addEventListener('click', () => {
            this.loadTodos();
        });
    }

    /**
     * 處理登錄
     */
    async handleLogin(e) {
        e.preventDefault();
        
        const username = this.elements.loginUsername.value.trim();
        const password = this.elements.loginPassword.value;

        if (!username || !password) {
            this.showAlert('請輸入用戶名和密碼', 'error');
            return;
        }

        // 設置按鈕加載狀態
        this.setButtonLoading(this.elements.loginBtn, true);

        try {
            const response = await api.login(username, password);
            
            this.currentUser = response.user;
            this.showAlert('登錄成功！', 'success');
            
            // 延遲切換視圖以顯示成功訊息
            setTimeout(async () => {
                await this.loadUserInfo();
                await this.loadTodos();
                this.showDashboard();
            }, 500);

        } catch (error) {
            this.showAlert(error.message || '登錄失敗，請檢查用戶名和密碼', 'error');
        } finally {
            this.setButtonLoading(this.elements.loginBtn, false);
        }
    }

    /**
     * 處理登出
     */
    handleLogout() {
        api.clearToken();
        this.currentUser = null;
        this.todos = [];
        
        // 清空表單
        this.elements.loginForm.reset();
        this.elements.addTodoForm.reset();
        
        this.showLogin();
        this.showAlert('已成功登出', 'info');
    }

    /**
     * 處理新增待辦事項
     */
    async handleAddTodo(e) {
        e.preventDefault();
        
        const content = this.elements.todoContent.value.trim();

        if (!content) {
            this.showAlert('請輸入待辦事項內容', 'error');
            return;
        }

        if (content.length > 1000) {
            this.showAlert('待辦事項內容不能超過 1000 字符', 'error');
            return;
        }

        // 設置按鈕加載狀態
        this.setButtonLoading(this.elements.addTodoBtn, true);

        try {
            const response = await api.createTodo(content);
            
            this.showAlert('待辦事項新增成功！', 'success');
            this.elements.todoContent.value = '';
            this.updateCharCount();
            
            // 重新載入待辦事項列表
            await this.loadTodos();

        } catch (error) {
            this.showAlert(error.message || '新增待辦事項失敗', 'error');
        } finally {
            this.setButtonLoading(this.elements.addTodoBtn, false);
        }
    }

    /**
     * 載入用戶資訊
     */
    async loadUserInfo() {
        try {
            const response = await api.getCurrentUser();
            this.currentUser = response.user;
            this.elements.usernameDisplay.textContent = this.currentUser.username;
        } catch (error) {
            console.error('Failed to load user info:', error);
            this.handleLogout();
        }
    }

    /**
     * 載入待辦事項列表
     */
    async loadTodos() {
        try {
            this.todos = await api.listTodos();
            this.renderTodos();
        } catch (error) {
            this.showAlert(error.message || '載入待辦事項失敗', 'error');
            console.error('Failed to load todos:', error);
        }
    }

    /**
     * 渲染待辦事項列表
     */
    renderTodos() {
        const { todosList, emptyState } = this.elements;

        // 清空列表
        todosList.innerHTML = '';

        if (this.todos.length === 0) {
            emptyState.style.display = 'block';
            todosList.style.display = 'none';
        } else {
            emptyState.style.display = 'none';
            todosList.style.display = 'block';

            // 渲染每個待辦事項
            this.todos.forEach(todo => {
                const li = document.createElement('li');
                li.className = 'todo-item';
                
                const content = document.createElement('div');
                content.className = 'todo-content';
                content.textContent = todo.content;
                
                const meta = document.createElement('div');
                meta.className = 'todo-meta';
                
                const id = document.createElement('span');
                id.className = 'todo-id';
                id.textContent = `ID: ${todo.id.substring(0, 8)}...`;
                
                const date = document.createElement('span');
                date.className = 'todo-date';
                date.textContent = this.formatDate(todo.created_at);
                
                meta.appendChild(id);
                meta.appendChild(date);
                
                li.appendChild(content);
                li.appendChild(meta);
                
                todosList.appendChild(li);
            });
        }
    }

    /**
     * 格式化日期
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    /**
     * 更新字符計數
     */
    updateCharCount() {
        const length = this.elements.todoContent.value.length;
        this.elements.charCount.textContent = `${length}/1000`;
    }

    /**
     * 顯示登錄頁面
     */
    showLogin() {
        this.currentView = 'login';
        this.elements.loginView.style.display = 'block';
        this.elements.dashboardView.style.display = 'none';
        this.elements.userInfo.style.display = 'none';
    }

    /**
     * 顯示儀表板（待辦事項管理）
     */
    async showDashboard() {
        this.currentView = 'dashboard';
        this.elements.loginView.style.display = 'none';
        this.elements.dashboardView.style.display = 'block';
        this.elements.userInfo.style.display = 'flex';
        
        // 確保已載入待辦事項
        if (this.todos.length === 0) {
            await this.loadTodos();
        }
    }

    /**
     * 顯示提示訊息
     */
    showAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'alert-close';
        closeBtn.textContent = '×';
        closeBtn.addEventListener('click', () => {
            alert.remove();
        });
        
        alert.appendChild(messageSpan);
        alert.appendChild(closeBtn);
        
        this.elements.alertContainer.appendChild(alert);
        
        // 自動移除（成功訊息 3 秒，錯誤訊息 5 秒）
        const timeout = type === 'success' ? 3000 : 5000;
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, timeout);
    }

    /**
     * 設置按鈕加載狀態
     */
    setButtonLoading(button, loading) {
        if (loading) {
            button.classList.add('loading');
            button.disabled = true;
        } else {
            button.classList.remove('loading');
            button.disabled = false;
        }
    }
}

// 當 DOM 加載完成後初始化應用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorkerAApp();
});