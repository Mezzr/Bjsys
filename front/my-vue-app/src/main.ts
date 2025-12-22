import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'

// 引入 Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入 axios
import axios from 'axios'

const app = createApp(App)
app.use(createPinia())
app.use(router)
// 使用 Element Plus
app.use(ElementPlus)

// 设置默认 axios 配置
axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
axios.defaults.withCredentials = true

// 启用 DevTools（开发环境）
if (import.meta.env.DEV) {
  app.config.devtools = true
}

app.mount('#app')