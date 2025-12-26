import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  withCredentials: true,
})

// 添加请求拦截器
api.interceptors.request.use(
  (config: any) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 添加必要的 headers 来处理 CORS
    config.headers['Content-Type'] = 'application/json'
    return config
  },
  (error: any) => {
    return Promise.reject(error)
  }
)

import { ElMessage } from 'element-plus'

// 添加响应拦截器
api.interceptors.response.use(
  (response: any) => {
    const res = response.data
    // 如果后端返回了 code 字段，且不为 0，则视为错误
    if (res && typeof res.code !== 'undefined' && res.code !== 0) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || 'Error'))
    }
    return res
  },
  (error: any) => {
    // 排除登录接口本身的 401 错误，避免死循环
    const isLoginRequest = error.config?.url?.includes('/auth/login/')
    
    if (error.response?.status === 401 && !isLoginRequest) {
      localStorage.removeItem('access_token')
      // 既然没有独立的登录页，就不要跳转了，或者跳转回首页
      // window.location.href = '/'
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default api