// 管理令牌的工具函数

const TOKEN_KEY = 'health_app_token'

// 获取令牌
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

// 设置令牌
export function setToken(token) {
  return localStorage.setItem(TOKEN_KEY, token)
}

// 移除令牌
export function removeToken() {
  return localStorage.removeItem(TOKEN_KEY)
}

// 检查是否已登录
export function isLoggedIn() {
  return !!getToken()
} 