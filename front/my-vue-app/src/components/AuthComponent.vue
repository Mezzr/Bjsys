<template>
  <div class="auth-component">
    <!-- 登录按钮 (未登录时显示) -->
    <button 
      v-if="!userStore.user" 
      @click="showLogin = true" 
      class="login-toggle-btn"
    >
      登录
    </button>

    <!-- 登出按钮 (登录后显示) -->
    <button v-else @click="handleLogout" class="logout-btn">登出</button>

    <!-- 登录弹窗 (Modal) -->
    <div v-if="showLogin" class="modal-overlay" @click.self="showLogin = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>用户登录</h3>
          <button class="close-btn" @click="showLogin = false">&times;</button>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label>用户名</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              placeholder="请输入用户名" 
              required 
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>密码</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              required 
              class="form-input"
            />
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <div class="form-actions">
            <button type="submit" class="btn login-btn" :disabled="loading">
              {{ loading ? '登录中...' : '登录' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const router = useRouter()

const showLogin = ref(false)
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    error.value = '请输入用户名和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    // 登录成功后重置表单并关闭弹窗
    loginForm.username = ''
    loginForm.password = ''
    showLogin.value = false
    
    // 跳转到主页
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/')
}
</script>

<style scoped>
.auth-component {
  display: flex;
  align-items: center;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: modal-slide-in 0.3s ease-out;
}

@keyframes modal-slide-in {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-actions {
  margin-top: 1.5rem;
}

.btn {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.login-btn {
  background-color: #1890ff;
  color: white;
}

.login-btn:hover {
  background-color: #40a9ff;
}

.login-btn:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}

.logout-btn, .login-toggle-btn {
  padding: 0.5rem 1.2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  color: white;
  white-space: nowrap;
  transition: opacity 0.2s;
}

.login-toggle-btn {
  background-color: #1890ff;
}

.login-toggle-btn:hover {
  opacity: 0.9;
}

.logout-btn {
  background-color: #ff4d4f;
}

.logout-btn:hover {
  opacity: 0.9;
}

.error-message {
  color: #ff4d4f;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  background-color: #fff1f0;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ffccc7;
}
</style>