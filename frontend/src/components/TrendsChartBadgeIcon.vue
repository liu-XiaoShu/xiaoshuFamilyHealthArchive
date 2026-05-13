<script setup lang="ts">
import { useId } from 'vue'

const sid = useId().replace(/[^a-zA-Z0-9_-]/g, '') || 'x'
const strokeId = `trn-chart-stroke-${sid}`
const areaId = `trn-chart-area-${sid}`
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient
        :id="strokeId"
        x1="5"
        y1="17"
        x2="21"
        y2="9"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#22d3ee" />
        <stop offset="0.45" stop-color="#38bdf8" />
        <stop offset="1" stop-color="#a5b4fc" />
      </linearGradient>
      <linearGradient
        :id="areaId"
        x1="12"
        y1="8.75"
        x2="12"
        y2="19.7"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#38bdf8" stop-opacity="0.35" />
        <stop offset="1" stop-color="#6366f1" stop-opacity="0.07" />
      </linearGradient>
    </defs>
    <path
      d="M4.25 19.55V7.1"
      stroke="rgba(100,116,139,0.42)"
      stroke-width="1.05"
      stroke-linecap="round"
    />
    <path
      d="M3.9 19.55h17.4"
      stroke="rgba(100,116,139,0.42)"
      stroke-width="1.05"
      stroke-linecap="round"
    />
    <path
      :fill="`url(#${areaId})`"
      d="M4.52 16.45 L8.85 13.48 L11.98 14.94 L15.68 9.52 L19.92 9.65 L21.92 13.93 L21.92 19.72 L4 19.72 Z"
    />
    <path
      class="pst-trends-line"
      d="M4.52 16.45 L8.85 13.48 L11.98 14.94 L15.68 9.52 L19.92 9.65"
      :stroke="`url(#${strokeId})`"
      stroke-width="2.2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <circle
      cx="19.92"
      cy="9.65"
      r="1.12"
      class="pst-trends-endcap"
      :stroke="`url(#${strokeId})`"
      stroke-width="0.88"
    />
  </svg>
</template>

<style scoped>
.pst-trends-endcap {
  fill: rgba(248, 250, 252, 0.96);
}
</style>
