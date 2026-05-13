<script setup lang="ts">
import { useId } from 'vue'

const sid = useId().replace(/[^a-zA-Z0-9_-]/g, '') || 'x'
const strokeId = `rpt-det-stroke-${sid}`
const panelId = `rpt-det-panel-${sid}`
</script>

<template>
  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient
        :id="strokeId"
        x1="7"
        y1="9"
        x2="18.85"
        y2="18.85"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#22d3ee" />
        <stop offset="0.48" stop-color="#38bdf8" />
        <stop offset="1" stop-color="#a5b4fc" />
      </linearGradient>
      <linearGradient
        :id="panelId"
        x1="12"
        y1="5.92"
        x2="12"
        y2="20.18"
        gradientUnits="userSpaceOnUse"
      >
        <stop stop-color="#38bdf8" stop-opacity="0.2" />
        <stop offset="1" stop-color="#6366f1" stop-opacity="0.07" />
      </linearGradient>
    </defs>
    <rect
      x="6.75"
      y="6.07"
      width="13.5"
      height="15.86"
      rx="2.1"
      ry="2.1"
      :fill="`url(#${panelId})`"
      stroke="rgba(100,116,139,0.42)"
      stroke-width="1.05"
      stroke-linejoin="round"
    />
    <path
      d="M8.92 9.12h8.45"
      :stroke="`url(#${strokeId})`"
      stroke-width="1.88"
      stroke-linecap="round"
    />
    <path
      d="M8.92 13.88h10.38"
      :stroke="`url(#${strokeId})`"
      stroke-width="1.32"
      stroke-linecap="round"
      opacity="0.9"
    />
    <path
      d="M8.92 17.78h6.45"
      :stroke="`url(#${strokeId})`"
      stroke-width="1.32"
      stroke-linecap="round"
      opacity="0.78"
    />
  </svg>
</template>
