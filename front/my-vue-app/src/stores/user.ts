import { defineStore } from 'pinia'
import api from '../services/api'

export type User = {
  id: string
  username: string
  email: string
  site: string | null
  site_id?: number | null
  can_edit_own_site: boolean
  can_view_all_sites: boolean
  can_manage_users: boolean
  name?: string | null
  token?: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    selectedStationId: null as string | null
  }),
  actions: {
    async fetchMe() {
      try {
        // 检查是否存在访问令牌
        const token = localStorage.getItem('access_token')
        if (!token) {
          throw new Error('No access token found')
        }
        
        // 调用后端API获取当前用户信息
        const response = await api.get('/auth/me/')
        // @ts-ignore
        this.user = response
        // 默认选中用户所属场站，便于下游页面直接拉取备件数据
        if (!this.selectedStationId) {
          // @ts-ignore
          this.selectedStationId = this.user?.site ?? null
        }
        return this.user
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        // 清除无效的令牌
        localStorage.removeItem('access_token')
        throw error
      }
    },
    
    async login(credentials: { username: string; password: string }) {
      try {
        // 调用后端登录接口
        const response = await api.post('/auth/login/', credentials, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
        // @ts-ignore
        const { access } = response
        
        // 保存token
        localStorage.setItem('access_token', access)
        
        // 登录接口不返回stationId，需要调用/auth/me获取完整信息
        await this.fetchMe()
        
        return this.user
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    
    async logout() {
      try {
        // 调用后端登出接口
        await api.post('/auth/logout/')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        // 清除本地状态
        this.user = null
        this.selectedStationId = null
        localStorage.removeItem('access_token')
      }
    },
    
    setUser(user: User) {
      this.user = user
      if (!this.selectedStationId) {
        this.selectedStationId = user.site ?? null
      }
    },
    
    setSelectedStation(stationId: string | null) {
      this.selectedStationId = stationId
    },
    
    getCurrentViewType() {
      if (this.user?.site && this.selectedStationId === this.user.site) {
        return 'own'
      }
      return 'other'
    }
  }
})
