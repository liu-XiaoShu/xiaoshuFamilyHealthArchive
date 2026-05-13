import { ref, shallowRef } from 'vue'
import { http } from '../api/http'

/** 最近一次拉取的登录状态（用户名仅用于顶部展示）；未就绪前为 null */
export const sessionReady = shallowRef(false)
export const authenticated = ref(false)
export const username = ref<string | null>(null)

export interface AuthMe {
  authenticated: boolean
  user: { username: string } | null
}

export async function refreshSession(): Promise<void> {
  try {
    const { data } = await http.get<AuthMe>('/api/auth/me')
    authenticated.value = data.authenticated
    username.value = data.user?.username ?? null
  } catch {
    authenticated.value = false
    username.value = null
  } finally {
    sessionReady.value = true
  }
}

export async function login(username_: string, password: string): Promise<void> {
  await http.post('/api/auth/login', { username: username_, password })
  await refreshSession()
}

export async function logout(): Promise<void> {
  try {
    await http.post('/api/auth/logout')
  } finally {
    authenticated.value = false
    username.value = null
  }
}

export async function updateAccountUsername(nextUsername: string): Promise<void> {
  await http.patch('/api/auth/profile', { username: nextUsername.trim() })
  await refreshSession()
}
