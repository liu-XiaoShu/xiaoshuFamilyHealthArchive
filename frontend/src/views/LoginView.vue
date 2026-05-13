<script setup lang="ts">
import { inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiError } from '../api/http'
import { login } from '../auth/session'
import { openAboutKey } from '../constants/injectionKeys'
import { postLoginTarget } from '../utils/postLoginRedirect'

const route = useRoute()
const router = useRouter()
const openAbout = inject(openAboutKey, () => {})

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const submitting = ref(false)
const err = ref('')
async function onSubmit() {
  err.value = ''
  submitting.value = true
  try {
    await login(username.value.trim(), password.value)
    const next = postLoginTarget(route.query.redirect)
    await router.replace(next)
  } catch (e) {
    err.value = apiError(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <button type="button" class="login-about-link" aria-label="关于本软件" @click="openAbout">
      关于
    </button>
    <div class="login-card card">
      <header class="login-brand" aria-label="本站名称">
        <div class="login-brand-visual" aria-hidden="true">
          <span class="login-brand-ring" />
          <span class="login-brand-heart">
            <!-- 极简心形轮廓，与医疗健康主题呼应 -->
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient
                  id="login-brand-heart-grad"
                  x1="4"
                  y1="6"
                  x2="20"
                  y2="19"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stop-color="#22d3ee" />
                  <stop offset="0.5" stop-color="#38bdf8" />
                  <stop offset="1" stop-color="#818cf8" />
                </linearGradient>
              </defs>
              <path
                d="M12 20.35l-1.03-.94C6.52 14.94 4 12.61 4 9.73 4 7.32 6.02 5.4 8.71 5.4c1.74 0 3.41.93 4.29 2.43A5.43 5.43 0 0117.29 5.4C19.98 5.4 22 7.32 22 9.73c0 2.88-2.52 5.21-6.97 9.68L12 20.35z"
                stroke="url(#login-brand-heart-grad)"
                stroke-width="1.45"
                stroke-linecap="round"
                stroke-linejoin="round"
                fill="rgba(56,189,248,0.06)"
              />
            </svg>
          </span>
        </div>
        <div class="login-brand-text">
          <p class="login-brand-title">家庭健康管理</p>
          <p class="login-brand-meta">
            <span class="login-brand-chip">本地 · 私密</span>
            <span class="login-brand-dot" aria-hidden="true" />
            <span class="login-brand-en">Family Health Desk</span>
          </p>
        </div>
      </header>
      <div class="login-heading-block">
        <h2 class="login-title">登录</h2>
        <p class="login-sub muted">
          健康数据仅存于本地/局域网服务端，请先登录后继续。
        </p>
      </div>
      <form class="login-form" @submit.prevent="onSubmit">
        <label class="fld">
          <span class="fld-label">账号</span>
          <input
            v-model="username"
            class="fld-input"
            type="text"
            name="username"
            autocomplete="username"
            required
          />
        </label>
        <div class="fld">
          <span class="fld-label" id="pw-label">密码</span>
          <div class="password-wrap">
            <input
              id="pwd"
              v-model="password"
              class="fld-input fld-input-password"
              :type="showPassword ? 'text' : 'password'"
              name="password"
              autocomplete="current-password"
              aria-labelledby="pw-label"
              required
            />
            <button
              type="button"
              class="pw-toggle"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              :aria-pressed="showPassword ? 'true' : 'false'"
              @click="showPassword = !showPassword"
            >
              <!-- 显示明文：睁眼 -->
              <svg
                v-if="!showPassword"
                class="pw-toggle-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
                />
                <path
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <!-- 隐藏：闭眼带斜杠 -->
              <svg
                v-else
                class="pw-toggle-icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"
                />
              </svg>
            </button>
          </div>
        </div>
        <p v-if="err" class="err">{{ err }}</p>
        <button type="submit" class="login-submit" :disabled="submitting">
          {{ submitting ? '登录中…' : '进入系统' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: clamp(2rem, 6vw, 3.5rem) 1rem;
  min-height: min(720px, calc(100vh - 8rem));
  box-sizing: border-box;
}
.login-about-link {
  position: absolute;
  top: clamp(0.85rem, 3vw, 1.25rem);
  right: clamp(0.85rem, 4vw, 1.6rem);
  z-index: 2;
  padding: 0.42rem 0.88rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(10px);
  color: #94a3b8;
  cursor: pointer;
  transition:
    color 0.15s ease,
    border-color 0.15s ease,
    background 0.15s ease,
    box-shadow 0.15s ease;
}
.login-about-link:hover {
  color: #bae6fd;
  border-color: rgba(56, 189, 248, 0.42);
  background: rgba(56, 189, 248, 0.1);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.2);
}
.login-card {
  width: min(420px, 100%);
  padding: 2rem 2rem 1.85rem;
  border-radius: calc(var(--radius-lg) + 6px);
  border: 1px solid rgba(148, 163, 184, 0.18);
  background:
    linear-gradient(
      168deg,
      rgba(56, 189, 248, 0.1) 0%,
      rgba(129, 140, 248, 0.05) 38%,
      rgba(15, 23, 42, 0.82) 100%
    ),
    var(--surface-inner);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.05) inset,
    0 22px 56px rgba(0, 0, 0, 0.32);
}
.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 1.65rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  background: radial-gradient(
    ellipse 80% 60% at 50% -20%,
    rgba(56, 189, 248, 0.14),
    transparent 65%
  );
}
.login-brand-visual {
  position: relative;
  width: 72px;
  height: 72px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-brand-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(56, 189, 248, 0.08) 0%,
    rgba(129, 140, 248, 0.04) 45%,
    transparent 70%
  );
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow:
    0 0 0 1px rgba(56, 189, 248, 0.08),
    0 10px 32px rgba(0, 0, 0, 0.25);
}
.login-brand-heart {
  position: relative;
  z-index: 1;
  display: flex;
  width: 38px;
  height: 38px;
  filter: drop-shadow(0 4px 12px rgba(56, 189, 248, 0.28));
}
.login-brand-heart svg {
  width: 100%;
  height: 100%;
}
.login-brand-text {
  width: 100%;
  max-width: 20rem;
  margin-inline: auto;
}
.login-brand-title {
  margin: 0 0 0.55rem;
  font-size: clamp(1.22rem, 3.8vw, 1.48rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  background: linear-gradient(120deg, #ecfeff 0%, #bae6fd 35%, #c7d2fe 92%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 1px 12px rgba(56, 189, 248, 0.12));
}
.login-brand-meta {
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.4rem 0.55rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: #64748b;
}
.login-brand-chip {
  padding: 0.26rem 0.62rem;
  border-radius: 999px;
  border: 1px solid rgba(56, 189, 248, 0.28);
  background: rgba(15, 23, 42, 0.5);
  color: #a5f3fc;
}
.login-brand-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(129, 140, 248, 0.75);
}
.login-brand-en {
  letter-spacing: 0.14em;
  text-transform: uppercase;
  opacity: 0.85;
  font-weight: 700;
  color: #94a3b8;
}
.login-heading-block {
  text-align: center;
  margin-bottom: 1.35rem;
}
.login-title {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #f8fafc;
}
.login-sub.muted {
  margin: 0 auto 0;
  max-width: 19rem;
  font-size: 0.73rem;
  line-height: 1.52;
  opacity: 0.86;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}
.fld {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.fld-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted, #94a3b8);
}
.fld-input {
  padding: 0.58rem 0.72rem;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.45);
  color: var(--text-primary);
  font-size: 1rem;
}
.fld-input:focus {
  outline: 2px solid rgba(56, 189, 248, 0.45);
  outline-offset: 2px;
  border-color: rgba(56, 189, 248, 0.35);
}
.password-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.fld-input-password {
  flex: 1;
  width: 100%;
  padding-right: 2.85rem;
  box-sizing: border-box;
}
.pw-toggle {
  position: absolute;
  right: 0.4rem;
  top: 50%;
  translate: 0 -50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}
.pw-toggle:hover {
  color: #e2e8f0;
  background: rgba(56, 189, 248, 0.1);
}
.pw-toggle:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.55);
  outline-offset: 2px;
}
.pw-toggle-icon {
  width: 1.28rem;
  height: 1.28rem;
}
.login-submit {
  margin-top: 0.35rem;
  padding: 0.65rem 1rem;
  border-radius: 999px;
  border: none;
  font-weight: 700;
  font-size: 0.94rem;
  cursor: pointer;
  color: #0f172a;
  background: linear-gradient(145deg, #38bdf8, #818cf8);
  box-shadow: 0 4px 22px rgba(56, 189, 248, 0.25);
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.login-submit:hover:not(:disabled) {
  transform: translateY(-1px);
}
.login-submit:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}
</style>
