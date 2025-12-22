<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from './stores/user'
import Navbar from './components/Navbar.vue'

const userStore = useUserStore()

onMounted(async () => {
  // 只有在存在访问令牌时才获取用户信息
  const token = localStorage.getItem('access_token')
  if (token) {
    await userStore.fetchMe()
  }
})
</script>

<template>
  <Navbar />
  <div style="max-width:1200px;margin:0 auto;padding:12px">
    <!-- <header style="display:flex;align-items:center;gap:1rem;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid #ddd">
      <nav>
        <router-link to="/parts" style="text-decoration:none;color:blue;margin-right:16px">备件</router-link>
      </nav>
      <div style="margin-left:auto;font-size:14px;color:#666">
        当前用户：{{ userStore.user?.name }} | 场站：{{ userStore.user?.stationId }}
      </div>
    </header> -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
body { 
  font-family: system-ui, -apple-system, "Helvetica Neue", Arial;
  margin: 0;
  padding: 0;
  background: #f5f5f5;
}
table { 
  width:100%; 
  border-collapse: collapse;
  background: white;
}
th, td { 
  padding:12px; 
  border: 1px solid #ddd;
  text-align: left;
}
th {
  background: #f0f0f0;
  font-weight: bold;
}
tr:hover {
  background: #fafafa;
}
button {
  padding: 6px 12px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
}
button:hover {
  background: #0050b3;
}
input, textarea {
  border: 1px solid #ddd;
  border-radius: 2px;
}
input:focus, textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
</style>
