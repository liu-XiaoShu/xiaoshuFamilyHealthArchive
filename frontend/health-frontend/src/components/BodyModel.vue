<template>
  <div class="body-model-container">
    <!-- 使用SVG人体模型替代Three.js模型 -->
    <div class="model-container">
      <div class="svg-container">
        <img ref="svgModel" src="/images/human_body.svg" class="body-svg" />
        
        <!-- 器官标记 -->
        <div 
          v-for="organ in abnormalOrgans" 
          :key="organ.name" 
          class="organ-marker"
          :class="getMarkerClass(organ.severity)"
          :style="{
            top: `${organ.position.y}%`,
            left: `${organ.position.x}%`
          }"
          @click="focusOrgan(organ)"
        >
          <div class="marker-pulse" :style="{ backgroundColor: organ.color }"></div>
          <div class="marker-label">{{ organ.name }}</div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    
    <div v-if="abnormalOrgans.length > 0" class="abnormal-organs">
      <h3>异常器官</h3>
      <el-tag
        v-for="organ in abnormalOrgans"
        :key="organ.name"
        :type="getTagType(organ.severity)"
        class="organ-tag"
        @click="focusOrgan(organ)"
      >
        {{ organ.name }}
        <el-tooltip :content="organ.description" placement="top">
          <el-icon class="info-icon"><InfoFilled /></el-icon>
        </el-tooltip>
      </el-tag>
    </div>

    <!-- 器官详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedOrgan?.name || '器官详情'"
      width="80%"
      :close-on-click-modal="true"
      class="organ-details-dialog"
    >
      <div v-if="selectedOrgan" class="organ-detail">
        <h4>异常级别：
          <el-tag :type="getTagType(selectedOrgan.severity)">
            {{ getSeverityLabel(selectedOrgan.severity) }}
          </el-tag>
        </h4>
        <p>{{ selectedOrgan.description }}</p>
        <div class="organ-actions">
          <el-button type="primary" @click="viewHistory">查看历史记录</el-button>
          <el-button type="success" @click="viewReport">查看相关报告</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, InfoFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { recordsApi } from '@/api/records'

interface AbnormalOrgan {
  id: number
  name: string
  status: 'normal' | 'warning' | 'danger'
  description: string
}

interface Organ {
  name: string
  severity: 'low' | 'medium' | 'high'
  description: string
  position: {
    x: number
    y: number
  }
  color: string
}

const router = useRouter()
const svgModel = ref<HTMLImageElement>()
const loading = ref(true)
const abnormalOrgans = ref<Organ[]>([])

// 弹窗显示控制
const dialogVisible = ref(false)
const selectedOrgan = ref<Organ | null>(null)

// 获取异常器官数据
const fetchAbnormalOrgans = async () => {
  try {
    const response = await recordsApi.getAbnormalOrgans()
    abnormalOrgans.value = response.map((organ: AbnormalOrgan) => ({
      name: organ.name,
      severity: organ.status === 'danger' ? 'high' : organ.status === 'warning' ? 'medium' : 'low',
      description: organ.description,
      position: getOrganPosition(organ.name),
      color: organ.status === 'danger' ? '#ff5555' : organ.status === 'warning' ? '#ffaa33' : '#55aaff'
    }))
  } catch (error) {
    console.error('获取异常器官数据失败:', error)
    ElMessage.error('获取异常器官数据失败')
  }
}

// 获取器官位置
const getOrganPosition = (organName: string) => {
  const positions: Record<string, { x: number, y: number }> = {
    '心脏': { x: 50, y: 30 },
    '肝脏': { x: 40, y: 40 },
    '肺部': { x: 62, y: 28 },
    '胃': { x: 50, y: 45 },
    '肾脏': { x: 45, y: 50 },
    '脾脏': { x: 55, y: 42 }
  }
  return positions[organName] || { x: 50, y: 50 }
}

// 聚焦到指定器官
const focusOrgan = (organ: Organ) => {
  selectedOrgan.value = organ
  dialogVisible.value = true
  
  // 高亮显示选中的器官
  const markers = document.querySelectorAll('.organ-marker')
  markers.forEach(marker => {
    marker.classList.remove('active')
  })
  
  // 找到对应的标记并添加高亮
  const organIndex = abnormalOrgans.value.findIndex(o => o.name === organ.name)
  if (organIndex !== -1) {
    const marker = document.querySelectorAll('.organ-marker')[organIndex]
    if (marker) {
      marker.classList.add('active')
      
      // 确保标记在视口内
      marker.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}

// 获取标记样式类
const getMarkerClass = (severity: string) => {
  switch (severity) {
    case 'high':
      return 'severity-high'
    case 'medium':
      return 'severity-medium'
    case 'low':
      return 'severity-low'
    default:
      return ''
  }
}

// 获取标签类型
const getTagType = (severity: string) => {
  switch (severity) {
    case 'high':
      return 'danger'
    case 'medium':
      return 'warning'
    case 'low':
      return 'info'
    default:
      return ''
  }
}

// 获取严重程度标签
const getSeverityLabel = (severity: string) => {
  switch (severity) {
    case 'high':
      return '严重'
    case 'medium':
      return '中度'
    case 'low':
      return '轻微'
    default:
      return '未知'
  }
}

// 查看历史记录
const viewHistory = () => {
  if (selectedOrgan.value) {
    router.push(`/records/medical?organ=${selectedOrgan.value.name}`)
  }
}

// 查看相关报告
const viewReport = () => {
  if (selectedOrgan.value) {
    router.push(`/records/physical?organ=${selectedOrgan.value.name}`)
  }
}

// 生命周期钩子
onMounted(async () => {
  loading.value = true
  try {
    // 获取异常器官数据
    await fetchAbnormalOrgans()
    
    // 加载SVG模型
    if (svgModel.value) {
      await new Promise<void>((resolve) => {
        svgModel.value!.onload = () => resolve()
      })
    }
  } catch (error) {
    console.error('初始化人体模型失败:', error)
    ElMessage.error('初始化人体模型失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.body-model-container {
  position: relative;
  width: 100%;
  height: 600px;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.model-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.svg-container {
  position: relative;
  height: 90%;
  display: flex;
  justify-content: center;
}

.body-svg {
  height: 100%;
  object-fit: contain;
}

.organ-marker {
  position: absolute;
  width: 20px;
  height: 20px;
  cursor: pointer;
  transform: translate(-50%, -50%);
  z-index: 10;
}

.marker-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.marker-label {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 12px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.organ-marker:hover .marker-label {
  opacity: 1;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0.7);
  }
  
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(255, 82, 82, 0);
  }
  
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 82, 82, 0);
  }
}

.severity-high .marker-pulse {
  background-color: #ff5252;
}

.severity-medium .marker-pulse {
  background-color: #ffa726;
}

.severity-low .marker-pulse {
  background-color: #4caf50;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.loading-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.abnormal-organs {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.organ-tag {
  margin: 5px;
  cursor: pointer;
}

.info-icon {
  margin-left: 5px;
  font-size: 14px;
}

.organ-detail {
  padding: 20px;
}

.organ-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style> 