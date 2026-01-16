/**
 * Worker B GUI 主應用程式
 * 處理用戶界面邏輯和狀態管理
 */

class WorkerBApp {
    constructor() {
        this.currentView = 'login'; // 'login', 'register', 'dashboard'
        this.currentUser = null;
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
                // 驗證令牌是否有效
                const userData = await api.getCurrentUser();
                if (userData && userData.user) {
                    this.currentUser = userData.user;
                    this.showDashboard();
                    return;
                }
            } catch (error) {
                // 令牌無效，清除並顯示登錄頁面
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

        // 複製令牌按鈕
        const copyTokenBtn = document.getElementById('copyTokenBtn');
        if (copyTokenBtn) {
            copyTokenBtn.addEventListener('click', () => this.copyToken());
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

        // 更新用戶資訊
        await this.updateUserInfo();
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

            if (response.token && response.user) {
                api.setToken(response.token);
                this.currentUser = response.user;
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

            if (response.token && response.user) {
                api.setToken(response.token);
                this.currentUser = response.user;
                this.showAlert('註冊成功！', 'success');

                // 延遲顯示儀表板
                setTimeout(() => {
                    this.showDashboard();
                }, 1000);
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
        this.showLogin();
        this.showAlert('已成功登出', 'info');
    }

    /**
     * 更新用戶資訊
     */
    async updateUserInfo() {
        try {
            const userData = await api.getCurrentUser();
            if (userData && userData.user) {
                this.currentUser = userData.user;
                this.renderUserInfo();
            }
        } catch (error) {
            console.error('Failed to fetch user info:', error);
            this.showAlert('無法獲取用戶資訊', 'error');
        }
    }

    /**
     * 渲染用戶資訊
     */
    renderUserInfo() {
        if (!this.currentUser) return;

        // 更新標題中的用戶名
        const usernameElement = document.getElementById('dashboardUsername');
        if (usernameElement) {
            usernameElement.textContent = this.currentUser.username;
        }

        // 更新用戶卡片
        const userIdElement = document.getElementById('userId');
        if (userIdElement) {
            userIdElement.textContent = this.currentUser.id;
        }

        const usernameCardElement = document.getElementById('usernameCard');
        if (usernameCardElement) {
            usernameCardElement.textContent = this.currentUser.username;
        }

        const createdAtElement = document.getElementById('createdAt');
        if (createdAtElement) {
            const date = new Date(this.currentUser.created_at);
            createdAtElement.textContent = date.toLocaleString('zh-TW');
        }

        // 更新令牌顯示
        const tokenElement = document.getElementById('tokenDisplay');
        if (tokenElement) {
            const token = api.getToken();
            tokenElement.textContent = token || '無令牌';
        }

        // 更新標題欄用戶名
        const headerUsername = document.getElementById('headerUsername');
        if (headerUsername) {
            headerUsername.textContent = this.currentUser.username;
        }
    }

    /**
     * 複製令牌到剪貼板
     */
    async copyToken() {
        const token = api.getToken();
        if (!token) {
            this.showAlert('沒有可複製的令牌', 'error');
            return;
        }

        try {
            await navigator.clipboard.writeText(token);
            this.showAlert('令牌已複製到剪貼板', 'success');
        } catch (error) {
            // 降級方案
            const textArea = document.createElement('textarea');
            textArea.value = token;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showAlert('令牌已複製到剪貼板', 'success');
        }
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
            // 恢復原始文本（需要根據按鈕類型設置）
            if (button.closest('#loginForm')) {
                button.innerHTML = '登錄';
            } else if (button.closest('#registerForm')) {
                button.innerHTML = '註冊';
            }
        }
    }
}

// 當頁面加載完成時初始化應用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new WorkerBApp();
});
