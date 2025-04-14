// 登录数据类型
export interface LoginData {
  username: string
  password: string
  remember?: boolean
}

// 注册数据类型
export interface RegisterData {
  username: string
  password: string
  password2: string
  confirmPassword?: string // 用于表单验证的别名
  email: string
  phone: string
}

// 用户信息类型
export interface User {
  id: number
  username: string
  email: string
  phone: string
  gender?: string
  avatar?: string
  birth_date?: string
  blood_type?: string
  hobbies?: string[]
  emergency_contact?: {
    name: string
    phone: string
    relationship: string
  }
  allergies?: string[]
  medical_history?: string[]
  created_at?: string
  updated_at?: string
}

// 认证状态类型
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
} 