<script setup lang="ts">
/**
 * 折叠/展开：小号文字 + chevron，与指标编辑「关联器官」一致，全站复用。
 * expanded = true：内容已全部展开。
 */
withDefaults(
  defineProps<{
    expanded: boolean
    /** 折叠态文案（点击进入展开） */
    labelCollapsed: string
    /** 展开态文案（点击进入折叠） */
    labelExpanded: string
    /** 可选：小号灰色附注（如「42 项」），两态均显示 */
    meta?: string
    /** inline：居中窄条（表单内）；block：占满宽度，内容居中（表格行内） */
    variant?: 'inline' | 'block'
  }>(),
  { variant: 'inline', meta: undefined },
)

const emit = defineEmits<{ toggle: [] }>()
</script>

<template>
  <button
    type="button"
    class="collapse-text-toggle"
    :class="{
      'collapse-text-toggle--expanded': expanded,
      'collapse-text-toggle--block': variant === 'block',
    }"
    :aria-expanded="expanded"
    @click="emit('toggle')"
  >
    <span class="collapse-text-toggle-label">{{ expanded ? labelExpanded : labelCollapsed }}</span>
    <span v-if="meta" class="muted collapse-text-toggle-meta">{{ meta }}</span>
    <svg
      class="collapse-text-toggle-icon"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M7 10l5 5 5-5"
        stroke="currentColor"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </button>
</template>

<style scoped>
.collapse-text-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.22rem 0.4rem;
  font: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #94a3b8;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition:
    color 0.18s ease,
    background 0.18s ease;
}

.collapse-text-toggle--block {
  display: flex;
  width: fit-content;
  max-width: min(20rem, 100%);
  margin-inline: auto;
  justify-content: center;
  flex-wrap: wrap;
  row-gap: 0.2rem;
}

.collapse-text-toggle--block .collapse-text-toggle-label {
  flex: 0 1 auto;
  min-width: 0;
  text-align: center;
}

.collapse-text-toggle:not(.collapse-text-toggle--block) {
  align-self: center;
  width: fit-content;
  max-width: 100%;
}

.collapse-text-toggle:hover {
  color: #bae6fd;
  background: rgba(56, 189, 248, 0.08);
}

.collapse-text-toggle:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.45);
  outline-offset: 2px;
}

.collapse-text-toggle-icon {
  flex-shrink: 0;
  width: 0.8125rem;
  height: 0.8125rem;
  color: currentColor;
  opacity: 0.88;
  transition: transform 0.22s ease;
}

.collapse-text-toggle--expanded .collapse-text-toggle-icon {
  transform: rotate(180deg);
}

.collapse-text-toggle-label {
  text-align: center;
  line-height: 1.35;
}

.collapse-text-toggle-meta {
  font-size: 0.6875rem;
  font-weight: 500;
  opacity: 0.88;
}

@media (prefers-reduced-motion: reduce) {
  .collapse-text-toggle-icon {
    transition: none;
  }
}
</style>
