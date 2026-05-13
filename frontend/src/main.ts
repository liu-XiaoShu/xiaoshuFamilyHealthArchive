import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { refreshSession } from './auth/session'
import './style.css'

async function boot() {
  await refreshSession()
  createApp(App).use(router).mount('#app')
}

void boot()
