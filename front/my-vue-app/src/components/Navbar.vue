<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <router-link to="/parts" class="navbar-logo">主页</router-link>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
          <!-- 其他导航项可以放在这里 -->
        </div>
        <div class="navbar-end">
          <div v-if="userStore.user" class="navbar-item user-info">
            <span>欢迎, {{ userStore.user.username }}</span>
            
            <span v-if="userStore.user.site" class="station-info">({{ userStore.user.site }})</span>
          </div>
          <AuthComponent />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useUserStore } from '../stores/user';
import AuthComponent from './AuthComponent.vue';

const userStore = useUserStore();
</script>

<style scoped>
.navbar {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  flex-wrap: nowrap;
  min-width: 0;
  width: 100%;
}

.navbar-brand {
  flex-shrink: 0;
  white-space: nowrap;
}

/* //   font-weight: 600;
//   font-size: 1.25rem;
//   text-decoration: none;
//   color: #1890ff;
//   padding: 1rem 0;
//   display: block;
// }

//   color: #0050b3;
// } */

.navbar-logo {
  font-weight: 800;
  font-size: 1.25rem;
  text-decoration: none;
  color: #1890ff;
  padding: 1rem 1.5rem;
  display: inline-block;
  min-width: 80px;
  text-align: center;
  white-space: nowrap;
}

.navbar-logo:hover {
  color: #0050b3;
  background-color: #f0f8ff;
  border-radius: 4px;
}

.navbar-menu {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  justify-content: flex-end;
}

.navbar-start {
  flex-grow: 1;
}

.navbar-end {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-shrink: 0;
  white-space: nowrap;
}

.navbar-item.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  flex-shrink: 0;
  white-space: nowrap;
}

.station-info {
  background-color: #e6f7ff;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: #1890ff;
  font-weight: 500;
}

/* 移动端适配 - 保持水平排列 */
@media (max-width: 768px) {
  .navbar-container {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
  }
  
  .navbar-menu {
    flex: 1;
    min-width: 0;
  }
  
  .navbar-end {
    gap: 0.75rem;
  }
  
  .navbar-item.user-info {
    font-size: 0.8rem;
  }
  
  .navbar-logo {
    padding: 0.75rem 1rem;
    min-width: 60px;
    font-size: 1.1rem;
  }
  
  .login-toggle-btn,
  .logout-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style>
