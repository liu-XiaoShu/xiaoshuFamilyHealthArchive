<template>
  <div class="health-chart-container">
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  LineChart,
  BarChart
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import * as echarts from 'echarts/core'
import type { EChartsOption } from 'echarts'
import { ElMessage } from 'element-plus'

// 注册必需的组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
])

const props = defineProps<{
  type: 'line' | 'bar'
  data: {
    categories: string[]
    series: Array<{
      name: string
      data: number[]
      type?: string
      color?: string
    }>
  }
}>()

const chartContainer = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  chart = echarts.init(chartContainer.value)
  updateChart()

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

// 更新图表数据
const updateChart = () => {
  if (!chart) return

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: props.data.series.map(item => item.name)
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.data.categories,
      axisLine: {
        lineStyle: {
          color: '#909399'
        }
      },
      axisLabel: {
        color: '#606266'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#909399'
        }
      },
      axisLabel: {
        color: '#606266'
      },
      splitLine: {
        lineStyle: {
          color: '#E4E7ED'
        }
      }
    },
    series: props.data.series.map(item => ({
      name: item.name,
      type: props.type,
      data: item.data,
      itemStyle: {
        color: item.color
      },
      lineStyle: item.color ? {
        color: item.color
      } : undefined,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      emphasis: {
        focus: 'series'
      }
    })),
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ]
  }

  try {
    chart.setOption(option)
  } catch (error) {
    console.error('更新图表失败:', error)
    ElMessage.error('更新图表失败')
  }
}

// 处理窗口大小变化
const handleResize = () => {
  chart?.resize()
}

// 监听数据变化
watch(
  () => props.data,
  () => {
    updateChart()
  },
  { deep: true }
)

// 生命周期钩子
onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
    chart = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.health-chart-container {
  width: 100%;
  height: 100%;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style> 