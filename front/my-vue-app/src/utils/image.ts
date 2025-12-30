export const getImageUrl = (path: string | null | undefined) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  // 获取 API Base URL
  // 统一使用 /api，配合 Vite 代理或 Nginx 转发
  const defaultBaseUrl = '/api'
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || defaultBaseUrl
  
  // 提取域名部分
  try {
    // 如果是完整 URL
    if (apiBaseUrl.startsWith('http')) {
      const url = new URL(apiBaseUrl)
      return `${url.origin}${path}`
    }
    // 如果是相对路径，直接返回 path
    return path
  } catch (e) {
    // Fallback
    return path
  }
}
