export const getImageUrl = (path: string | null | undefined) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  
  // 获取 API Base URL，默认为 http://localhost:8000/api
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  
  // 提取域名部分 (http://localhost:8000)
  // 假设 apiBaseUrl 总是以 /api 结尾，或者我们只需要它的 origin
  try {
    // 如果是完整 URL
    if (apiBaseUrl.startsWith('http')) {
      const url = new URL(apiBaseUrl)
      return `${url.origin}${path}`
    }
    // 如果是相对路径 (虽然不太可能，但在某些部署场景下)
    return path
  } catch (e) {
    // Fallback
    return `http://localhost:8000${path}`
  }
}
