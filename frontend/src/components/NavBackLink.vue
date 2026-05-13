<script setup lang="ts">
/**
 * 「返回」导航：无箭头，配简洁线性图标。
 * home：家庭成员列表；member：当前成员档案。
 */
defineProps<{
  to: string
  label: string
  variant?: 'home' | 'member'
}>()
</script>

<template>
  <RouterLink :to="to" class="btn secondary nav-back-link">
    <span class="nav-back-icon" aria-hidden="true">
      <!-- 家庭成员 / 首页列表 -->
      <svg
        v-if="(variant ?? 'member') === 'home'"
        class="nav-back-svg"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M4 10.5 12 4 20 10.5V20h-4.5v-6h-7v6H4V10.5z"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linejoin="round"
        />
      </svg>
      <!-- 成员档案 -->
      <svg
        v-else
        class="nav-back-svg"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="12" cy="9" r="3.25" stroke="currentColor" stroke-width="1.5" />
        <path
          d="M6.2 19.3c.65-2.85 3.15-5 5.8-5 2.65 0 5.15 2.15 5.8 5"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
        />
      </svg>
    </span>
    <span>{{ label }}</span>
  </RouterLink>
</template>

<style scoped>
.nav-back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  text-decoration: none;
  vertical-align: middle;
}

.nav-back-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 1.15rem;
  height: 1.15rem;
  opacity: 0.92;
}

.nav-back-svg {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
