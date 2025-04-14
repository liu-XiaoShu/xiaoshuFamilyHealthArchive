<template>
  <div class="chart-container" ref="chartContainer"></div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption, LineSeriesOption } from 'echarts'

interface LineChartProps {
  title?: string
  subtext?: string
  xAxis?: string[]
  series?: Array<{
    name: string
    data: number[]
    type?: 'line'
    smooth?: boolean
    lineStyle?: any
    itemStyle?: any
    areaStyle?: any
  }>
  height?: string
  legendPosition?: 'top' | 'bottom' | 'left' | 'right'
}

const props = withDefaults(defineProps<LineChartProps>(), {
  title: '',
  subtext: '',
  xAxis: () => [],
  series: () => [],
  height: '300px',
  legendPosition: 'right'
})

// 创建一个DOM引用
const chartContainer = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 计算图表选项
const chartOptions = computed(() => {
  const option: EChartsOption = {
    title: {
      text: props.title,
      subtext: props.subtext
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      orient: props.legendPosition === 'top' || props.legendPosition === 'bottom' ? 'horizontal' : 'vertical',
      left: props.legendPosition === 'right' ? 'right' : props.legendPosition === 'left' ? 'left' : 'center',
      top: props.legendPosition === 'top' ? 'top' : props.legendPosition === 'bottom' ? 'bottom' : 'middle'
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
      data: props.xAxis
    },
    yAxis: {
      type: 'value'
    },
    series: props.series.map(item => ({
      name: item.name,
      type: 'line',
      stack: 'Total',
      data: item.data,
      smooth: item.smooth !== undefined ? item.smooth : true,
      lineStyle: item.lineStyle || {},
      itemStyle: item.itemStyle || {},
      areaStyle: item.areaStyle || undefined
    }))
  }
  return option
})

// 初始化图表
const initChart = () => {
  if (chartContainer.value) {
    chart = echarts.init(chartContainer.value)
    chart.setOption(chartOptions.value)
    
    // 添加窗口大小改变监听
    window.addEventListener('resize', handleResize)
  }
}

// 处理图表更新
const updateChart = () => {
  if (chart) {
    chart.setOption(chartOptions.value)
  }
}

// 处理窗口大小改变
const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

// 组件挂载时初始化图表
onMounted(() => {
  initChart()
})

// 当props改变时更新图表
watch(
  [() => props.xAxis, () => props.series, () => props.title, () => props.subtext],
  () => {
    updateChart()
  },
  { deep: true }
)

// 销毁组件时移除事件监听
const dispose = () => {
  if (chart) {
    chart.dispose()
    chart = null
    window.removeEventListener('resize', handleResize)
  }
}

// 暴露方法
defineExpose({
  updateChart,
  dispose
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style> 