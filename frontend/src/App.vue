<script setup lang="ts">
import { computed, nextTick, provide, ref } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink, RouterView } from 'vue-router'
import AboutDialog from './components/AboutDialog.vue'
import { openAboutKey } from './constants/injectionKeys'
import { logout as logoutSession, updateAccountUsername, username } from './auth/session'
import { apiError } from './api/http'
import { familyNavLabelFromUsername } from './utils/familyNavLabel'

const route = useRoute()
const hideShell = computed(() => route.path === '/login')
const aboutOpen = ref(false)

const navHomeLabel = computed(() => familyNavLabelFromUsername(username.value))

const renameOpen = ref(false)
const renameDraft = ref('')
const renameErr = ref('')
const renameBusy = ref(false)
const renameInputEl = ref<HTMLInputElement | null>(null)

provide(openAboutKey, () => {
  aboutOpen.value = true
})

async function onLogout() {
  await logoutSession()
  window.location.assign('/login')
}

function openRename() {
  renameErr.value = ''
  renameDraft.value = username.value ?? ''
  renameOpen.value = true
  void nextTick(() => {
    renameInputEl.value?.focus({ preventScroll: true })
    renameInputEl.value?.select()
  })
}

function closeRename() {
  renameOpen.value = false
  renameErr.value = ''
  renameBusy.value = false
}

async function submitRename() {
  const next = renameDraft.value.trim()
  if (!next) {
    renameErr.value = '请输入用户名'
    return
  }
  if (next === (username.value ?? '')) {
    closeRename()
    return
  }
  renameErr.value = ''
  renameBusy.value = true
  try {
    await updateAccountUsername(next)
    closeRename()
  } catch (e) {
    renameErr.value = apiError(e)
  } finally {
    renameBusy.value = false
  }
}
</script>

<template>
  <header v-if="!hideShell" class="top">
    <div class="brand">
      <span class="brand-dot" aria-hidden="true" />
      <h1>
        <RouterLink to="/">家庭健康管理</RouterLink>
      </h1>
      <span class="brand-tag" title="局域网 / 本地数据">Health · Local</span>
      <span v-if="username" class="brand-user-wrap muted" aria-live="polite">
        <span class="brand-user">{{ username }}</span>
        <button type="button" class="brand-rename-btn" title="修改登录用户名；保存后导航与首页将显示为「新名的家」" @click="openRename">
          改名
        </button>
      </span>
    </div>
    <div class="top-actions">
      <nav class="nav">
        <RouterLink to="/">{{ navHomeLabel }}</RouterLink>
        <RouterLink to="/indicators">指标编辑</RouterLink>
      </nav>
      <button type="button" class="logout-btn muted" title="退出登录" @click="onLogout">
        退出登录
      </button>
      <button type="button" class="about-btn" aria-label="关于本软件" @click="aboutOpen = true">
        关于
      </button>
    </div>
  </header>
  <Teleport to="body">
    <div v-if="renameOpen" class="rename-root" aria-hidden="false">
      <div class="rename-backdrop" tabindex="-1" @click.self="closeRename" />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="rename-title"
        class="rename-dialog card"
        tabindex="-1"
        @keydown.escape="closeRename"
      >
        <h2 id="rename-title" class="rename-title">修改账户名</h2>
        <p class="rename-hint muted">
          即登录用户名；保存后本页与导航将显示为「<strong>新名</strong>的家」，下次请用新用户名登录。
        </p>
        <label class="rename-label">
          <span class="rename-caption">新用户名</span>
          <input
            ref="renameInputEl"
            v-model="renameDraft"
            type="text"
            class="rename-input"
            maxlength="64"
            autocomplete="username"
            @keydown.enter.prevent="submitRename"
          />
        </label>
        <p v-if="renameErr" class="rename-err">{{ renameErr }}</p>
        <div class="rename-actions">
          <button type="button" class="logout-btn muted" @click="closeRename">取消</button>
          <button type="button" class="rename-save-btn" :disabled="renameBusy" @click="submitRename">
            {{ renameBusy ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
  <main :class="hideShell ? 'wrap wrap--login' : 'wrap'">
    <RouterView />
  </main>
  <AboutDialog v-model="aboutOpen" />
</template>

<style scoped>
.top {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.9rem 1.5rem;
  background: rgba(6, 10, 18, 0.78);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.brand-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(145deg, #22d3ee, #818cf8);
  box-shadow:
    0 0 14px rgba(56, 189, 248, 0.65),
    0 0 28px rgba(129, 140, 248, 0.35);
}

.top h1 {
  margin: 0;
  font-size: 1.12rem;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.top h1 a {
  color: #f8fafc;
  text-decoration: none;
}

.top h1 a:hover {
  color: #bae6fd;
}

.brand-tag {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748b;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.55);
}

.brand-user-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.brand-user {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #94a3b8;
}

.brand-rename-btn {
  padding: 0.2rem 0.52rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 650;
  border: 1px solid rgba(56, 189, 248, 0.32);
  background: rgba(56, 189, 248, 0.08);
  color: #7dd3fc;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
}

.brand-rename-btn:hover {
  border-color: rgba(56, 189, 248, 0.55);
  background: rgba(56, 189, 248, 0.14);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 0.62rem;
  flex-wrap: wrap;
}

.logout-btn {
  padding: 0.38rem 0.82rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(148, 163, 184, 0.06);
  color: #94a3b8;
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    background 0.15s ease,
    color 0.15s ease;
}

.logout-btn:hover {
  color: #f1f5f9;
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.08);
}

.about-btn {
  padding: 0.38rem 0.78rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition:
    color 0.15s ease,
    border-color 0.15s ease,
    background 0.15s ease;
}
.about-btn:hover {
  color: #bae6fd;
  border-color: rgba(56, 189, 248, 0.42);
  background: rgba(56, 189, 248, 0.08);
}

.nav {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.nav a {
  padding: 0.48rem 1rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  border: 1px solid transparent;
  transition:
    color 0.15s ease,
    background 0.15s ease,
    border-color 0.15s ease;
}

.nav a:hover {
  color: #e2e8f0;
  background: rgba(148, 163, 184, 0.08);
}

.nav a.router-link-active {
  color: #f8fafc;
  background: linear-gradient(
    145deg,
    rgba(14, 165, 233, 0.22) 0%,
    rgba(99, 102, 241, 0.18) 100%
  );
  border-color: rgba(56, 189, 248, 0.42);
  box-shadow: 0 2px 14px rgba(14, 165, 233, 0.15);
}

.wrap {
  max-width: 1140px;
  margin: 0 auto;
  padding: 1.5rem 1.35rem 2.5rem;
}

.wrap--login {
  max-width: none;
  padding-left: 0;
  padding-right: 0;
}

.rename-root {
  position: fixed;
  inset: 0;
  z-index: 950;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  box-sizing: border-box;
  pointer-events: none;
}

.rename-root > * {
  pointer-events: auto;
}

.rename-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.rename-dialog {
  position: relative;
  width: min(22rem, 100%);
  margin: 0;
  padding: 1.2rem 1.25rem 1.25rem;
  border-radius: calc(var(--radius-lg, 14px));
}

.rename-title {
  margin: 0 0 0.55rem;
  font-size: 1.05rem;
  font-weight: 750;
}

.rename-hint {
  margin: 0 0 0.95rem;
  font-size: 0.8125rem;
  line-height: 1.5;
}

.rename-hint strong {
  color: #93c5fd;
}

.rename-label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin: 0 0 0.65rem;
}

.rename-caption {
  font-size: 0.75rem;
  font-weight: 650;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94a3b8;
}

.rename-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 0.62rem;
  border-radius: var(--radius-sm, 10px);
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.75);
  color: #f1f5f9;
  font-size: 1rem;
}

.rename-input:focus {
  outline: none;
  border-color: rgba(56, 189, 248, 0.48);
}

.rename-err {
  margin: 0 0 0.62rem;
  font-size: 0.8125rem;
  color: #fca5a5;
}

.rename-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.rename-save-btn {
  padding: 0.42rem 0.92rem;
  border-radius: 999px;
  font-size: 0.825rem;
  font-weight: 650;
  border: 1px solid rgba(56, 189, 248, 0.42);
  background: linear-gradient(145deg, rgba(14, 165, 233, 0.22), rgba(99, 102, 241, 0.16));
  color: #e0f2fe;
  cursor: pointer;
}

.rename-save-btn:hover:not(:disabled) {
  border-color: rgba(56, 189, 248, 0.6);
}

.rename-save-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
