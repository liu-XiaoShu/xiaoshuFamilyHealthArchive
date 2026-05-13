import axios from 'axios'

export const http = axios.create({
  baseURL: '',
  withCredentials: true,
})

/** GET 默认要求中间层重新校验，减轻浏览器磁盘缓存导致的陈旧成员摘要（如当前异常项数） */
http.interceptors.request.use((config) => {
  if ((config.method ?? 'get').toLowerCase() === 'get') {
    config.headers.set('Cache-Control', 'no-cache')
    config.headers.set('Pragma', 'no-cache')
  }
  return config
})

/** 会话过期或未登录访问受保护 API 时跳转到登录页 */
http.interceptors.response.use(undefined, async (error) => {
  if (
    axios.isAxiosError(error) &&
    error.response?.status === 401 &&
    typeof window !== 'undefined'
  ) {
    const reqUrl = error.config?.url ?? ''
    if (
      !reqUrl.includes('/api/auth/login') &&
      !reqUrl.includes('/api/auth/me')
    ) {
      const here = `${window.location.pathname}${window.location.search}`
      window.location.assign(`/login?redirect=${encodeURIComponent(here)}`)
    }
  }
  return Promise.reject(error)
})

export function apiError(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const status = e.response?.status
    const d = e.response?.data as { detail?: string | Array<{ msg?: string }> } | undefined
    if (status === 405) {
      return 'HTTP 405：浏览器发出了 POST，但当前站点没有把请求转到后端 API（常见于运行了「vite preview」却未配置 preview 代理，或用静态服务器单独打开了前端）。请任选其一：① 开发时用 npm run dev；② preview 时已在本仓库 vite.config 配置 preview.proxy，且后端在 127.0.0.1:8000；③ 局域网只用后端 uvicorn 打开的 http://本机:8000（推荐）。若在地址栏直接打开了上传接口链接也会 405，请只用本页的「上传并导入」。'
    }
    if (typeof d?.detail === 'string') {
      if (
        status === 404 &&
        (d.detail === 'Not Found' || d.detail.toLowerCase() === 'not found')
      ) {
        return '接口不存在（404）：请确认后端已部署最新代码并已重启服务'
      }
      return d.detail
    }
    if (Array.isArray(d?.detail)) {
      return d.detail
        .map((x) => {
          if (typeof x === 'string') return x
          const o = x as { msg?: string }
          return o.msg ?? JSON.stringify(x)
        })
        .join('; ')
    }
    return e.message
  }
  return String(e)
}
