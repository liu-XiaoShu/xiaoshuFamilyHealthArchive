import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

/** dev / preview 均需代理 /api，否则上传等 POST 会打到静态服务器返回 405 */
const apiProxy = {
  '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
} as const

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    proxy: apiProxy,
  },
  preview: {
    host: true,
    proxy: apiProxy,
  },
})
