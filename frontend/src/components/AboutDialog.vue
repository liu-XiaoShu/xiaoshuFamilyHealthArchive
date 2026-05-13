<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'

const APP_VERSION = 'v1.0.0'
const AUTHOR = 'liu-xiaoshu'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [v: boolean] }>()

function close() {
  emit('update:modelValue', false)
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) {
    close()
    e.preventDefault()
  }
}

watch(
  () => props.modelValue,
  (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
  },
)

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="about-fade">
      <div v-if="modelValue" class="about-root" aria-hidden="false">
        <div class="about-backdrop" tabindex="-1" @click.self="close" />
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="about-title"
          class="about-dialog"
        >
          <button type="button" class="about-close" aria-label="关闭" @click="close">
            ✕
          </button>
          <h2 id="about-title" class="about-title">关于</h2>
          <dl class="about-meta">
            <div class="about-row">
              <dt>版本</dt>
              <dd>
                <code class="about-code">{{ APP_VERSION }}</code>
              </dd>
            </div>
            <div class="about-row">
              <dt>作者</dt>
              <dd>{{ AUTHOR }}</dd>
            </div>
          </dl>
          <section class="about-story" aria-label="缘起">
            <h3 class="about-story-heading">做这个软件的初衷</h3>
            <p>
              大家越来越在意自己的身体状况，一年中往往既有门诊化验，又有机构体检——可报告形态各异，
              纸质、电子版散在不同医院与公司平台里，想对比趋势、给家里老人留一份全貌，反而不容易。
            </p>
            <p>
              本系统面向<strong>家庭或可信小范围局域网</strong>，希望能把就医与体检的检查结果<strong>结构化地收拢到一处</strong>：
              便于录入与修正、便于按人与时间查阅、必要时再导出备份。把「关心健康」从翻找单据里解放出来，
              多留一点给真正的生活与照护。
            </p>
          </section>
          <footer class="about-footer">
            <button type="button" class="about-ok" @click="close">知道了</button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.about-root {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  box-sizing: border-box;
  pointer-events: none;
}

.about-root > * {
  pointer-events: auto;
}

.about-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.about-dialog {
  position: relative;
  width: min(400px, 100%);
  max-height: min(88vh, 520px);
  overflow: auto;
  padding: 1.45rem 1.5rem 1.35rem;
  border-radius: calc(var(--radius-lg) + 4px);
  border: 1px solid rgba(148, 163, 184, 0.22);
  background:
    linear-gradient(165deg, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 0.96) 45%),
    var(--surface-inner, rgba(15, 23, 42, 0.98));
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.06) inset,
    0 24px 64px rgba(0, 0, 0, 0.45);
  color: var(--text-primary, #f1f5f9);
}

.about-close {
  position: absolute;
  top: 0.72rem;
  right: 0.72rem;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}
.about-close:hover {
  color: #f8fafc;
  background: rgba(248, 113, 113, 0.12);
}

.about-title {
  margin: 0 2rem 1rem 0;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.about-meta {
  margin: 0 0 1.15rem;
}
.about-row {
  display: grid;
  grid-template-columns: 3.25rem 1fr;
  gap: 0.5rem 0.85rem;
  align-items: baseline;
  padding: 0.35rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  font-size: 0.9rem;
}
.about-row:last-of-type {
  border-bottom: none;
}
.about-row dt {
  margin: 0;
  font-weight: 700;
  color: #94a3b8;
}
.about-row dd {
  margin: 0;
  color: #e2e8f0;
}
.about-code {
  font-size: 0.88em;
  padding: 0.12rem 0.45rem;
  border-radius: 6px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #7dd3fc;
}

.about-story-heading {
  margin: 0 0 0.55rem;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #64748b;
}
.about-story p {
  margin: 0 0 0.65rem;
  font-size: 0.885rem;
  line-height: 1.62;
  color: #cbd5e1;
}
.about-story p:last-child {
  margin-bottom: 0;
}
.about-story strong {
  font-weight: 700;
  color: #bae6fd;
}

.about-footer {
  margin-top: 1.2rem;
  display: flex;
  justify-content: flex-end;
}
.about-ok {
  padding: 0.52rem 1.15rem;
  border-radius: 999px;
  border: 1px solid rgba(56, 189, 248, 0.35);
  background: rgba(56, 189, 248, 0.12);
  color: #bae6fd;
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  transition:
    background 0.15s ease,
    border-color 0.15s ease;
}
.about-ok:hover {
  background: rgba(56, 189, 248, 0.22);
  border-color: rgba(56, 189, 248, 0.5);
}

.about-fade-enter-active,
.about-fade-leave-active {
  transition: opacity 0.2s ease;
}
.about-fade-enter-active .about-dialog,
.about-fade-leave-active .about-dialog {
  transition:
    opacity 0.2s ease,
    transform 0.2s cubic-bezier(0.34, 1.35, 0.64, 1);
}
.about-fade-enter-from,
.about-fade-leave-to {
  opacity: 0;
}
.about-fade-enter-from .about-dialog,
.about-fade-leave-to .about-dialog {
  opacity: 0;
  transform: scale(0.96) translateY(8px);
}
</style>
