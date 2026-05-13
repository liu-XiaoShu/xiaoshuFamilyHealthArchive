<script setup lang="ts">
import { nextTick, onUnmounted, ref, useId, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    /** 可多行文案 */
    message: string
  }>(),
  { title: '提示' },
)

const emit = defineEmits<{ close: [] }>()

const baseId = useId()
const titleId = `${baseId}-title`
const bodyId = `${baseId}-body`

const panelRef = ref<HTMLElement | null>(null)

function onKeydown(ev: KeyboardEvent) {
  if (ev.key === 'Escape') {
    ev.preventDefault()
    emit('close')
  }
}

watch(
  () => props.open,
  (v) => {
    if (v) {
      void nextTick(() => panelRef.value?.focus({ preventScroll: true }))
      document.addEventListener('keydown', onKeydown)
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
)

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="message-dlg-overlay"
      role="presentation"
      @click.self="$emit('close')"
    >
      <div
        ref="panelRef"
        class="message-dlg card"
        role="alertdialog"
        aria-modal="true"
        tabindex="-1"
        :aria-labelledby="titleId"
        :aria-describedby="bodyId"
      >
        <h3 :id="titleId" class="message-dlg-title">
          {{ title }}
        </h3>
        <p :id="bodyId" class="message-dlg-body">{{ message }}</p>
        <div class="message-dlg-actions">
          <button type="button" @click="$emit('close')">知道了</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.message-dlg-overlay {
  position: fixed;
  inset: 0;
  z-index: 10085;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1.25rem 1rem 2rem;
  overflow-y: auto;
  background: rgba(6, 10, 18, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.message-dlg {
  width: min(26rem, 100%);
  margin-top: min(14vh, 5rem);
  margin-bottom: 2rem;
  outline: none;
}

.message-dlg-title {
  margin: 0 0 0.72rem;
  font-size: 1.06rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.message-dlg-body {
  margin: 0 0 1.15rem;
  font-size: 0.903rem;
  line-height: 1.58;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-dlg-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
