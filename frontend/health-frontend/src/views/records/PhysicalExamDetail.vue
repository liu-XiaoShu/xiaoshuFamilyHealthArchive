<template>
  <div class="physical-exam-detail">
    <div class="page-header">
      <div class="page-title">体检记录详情</div>
      <div class="page-actions">
        <el-button @click="router.back()">返回</el-button>
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
        <el-button type="danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>删除
        </el-button>
      </div>
    </div>

    <div v-loading="loading">
      <!-- 基本信息 -->
      <div class="app-card">
        <div class="card-header">
          <h3>基本信息</h3>
        </div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="体检日期">
            {{ formatDate(examData.exam_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="体检类型">
            <el-tag :type="getExamTypeTag(examData.exam_type)">
              {{ getExamTypeLabel(examData.exam_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="体检医院">
            {{ examData.hospital }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(examData.status)">
              {{ getStatusLabel(examData.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(examData.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(examData.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 体检指标 -->
      <div class="app-card">
        <div class="card-header">
          <h3>体检指标</h3>
        </div>
        <div class="metrics-grid">
          <div class="metric-item" :class="{ warning: isBMIAbnormal }">
            <div class="metric-icon">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ calculateBMI }}</div>
              <div class="metric-label">BMI</div>
              <div class="metric-detail">
                身高: {{ examData.height }}cm<br>
                体重: {{ examData.weight }}kg
              </div>
            </div>
          </div>

          <div class="metric-item" :class="{ warning: isBloodPressureAbnormal }">
            <div class="metric-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ examData.blood_pressure }}</div>
              <div class="metric-label">血压 (mmHg)</div>
              <div class="metric-detail">
                {{ getBloodPressureStatus(examData.blood_pressure) }}
              </div>
            </div>
          </div>

          <div class="metric-item" :class="{ warning: isBloodSugarAbnormal }">
            <div class="metric-icon">
              <el-icon><View /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ examData.blood_sugar }}</div>
              <div class="metric-label">血糖 (mmol/L)</div>
              <div class="metric-detail">
                {{ getBloodSugarStatus(examData.blood_sugar) }}
              </div>
            </div>
          </div>

          <div class="metric-item" :class="{ warning: isHeartRateAbnormal }">
            <div class="metric-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ examData.heart_rate }}</div>
              <div class="metric-label">心率 (次/分)</div>
              <div class="metric-detail">
                {{ getHeartRateStatus(examData.heart_rate) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 体检结果 -->
      <div class="app-card">
        <div class="card-header">
          <h3>体检结果</h3>
        </div>
        <div class="result-section">
          <div class="result-item">
            <div class="result-label">体检总结</div>
            <div class="result-content">{{ examData.summary || '暂无总结' }}</div>
          </div>
          <div class="result-item">
            <div class="result-label">医生建议</div>
            <div class="result-content">{{ examData.advice || '暂无建议' }}</div>
          </div>
        </div>
      </div>

      <!-- 附件 -->
      <div v-if="examData.attachments?.length" class="app-card">
        <div class="card-header">
          <h3>附件</h3>
        </div>
        <div class="attachment-list">
          <div
            v-for="file in examData.attachments"
            :key="file.id"
            class="attachment-item"
          >
            <el-link :href="file.url" target="_blank" type="primary">
              <el-icon><Document /></el-icon>
              {{ file.name }}
            </el-link>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="30%"
      center
    >
      <span>确定要删除这条体检记录吗？此操作不可恢复。</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="confirmDelete" :loading="deleting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit,
  Delete,
  Document,
  DataLine,
  CircleCheck,
  View,
  Timer
} from '@element-plus/icons-vue'
import { format } from 'date-fns'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const deleteDialogVisible = ref(false)
const deleting = ref(false)

// 体检数据
const examData = reactive({
  exam_date: '',
  exam_type: '',
  hospital: '',
  height: 0,
  weight: 0,
  blood_pressure: '',
  blood_sugar: 0,
  heart_rate: 0,
  summary: '',
  advice: '',
  status: '',
  attachments: [],
  created_at: '',
  updated_at: ''
})

// 获取记录详情
const fetchExamDetail = async () => {
  loading.value = true
  try {
    const response = await axios.get(`/api/records/physical/${route.params.id}`)
    Object.assign(examData, response.data)
  } catch (error) {
    ElMessage.error('获取记录详情失败')
    console.error('获取记录详情失败:', error)
    router.back()
  } finally {
    loading.value = false
  }
}

// 编辑记录
const handleEdit = () => {
  router.push(`/records/physical/${route.params.id}/edit`)
}

// 删除记录
const handleDelete = () => {
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    await axios.delete(`/api/records/physical/${route.params.id}`)
    ElMessage.success('删除成功')
    router.push('/records/physical')
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  } finally {
    deleting.value = false
    deleteDialogVisible.value = false
  }
}

// 格式化日期
const formatDate = (date: string) => {
  return date ? format(new Date(date), 'yyyy-MM-dd') : '-'
}

const formatDateTime = (date: string) => {
  return date ? format(new Date(date), 'yyyy-MM-dd HH:mm:ss') : '-'
}

// 获取体检类型标签
const getExamTypeTag = (type: string) => {
  const typeMap: { [key: string]: string } = {
    annual: '',
    employment: 'success',
    other: 'info'
  }
  return typeMap[type] || ''
}

const getExamTypeLabel = (type: string) => {
  const typeMap: { [key: string]: string } = {
    annual: '年度体检',
    employment: '入职体检',
    other: '其他'
  }
  return typeMap[type] || type
}

// 获取状态标签
const getStatusTag = (status: string) => {
  const statusMap: { [key: string]: string } = {
    normal: 'success',
    abnormal: 'danger',
    pending: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const statusMap: { [key: string]: string } = {
    normal: '正常',
    abnormal: '异常',
    pending: '待复查'
  }
  return statusMap[status] || status
}

// 计算BMI
const calculateBMI = computed(() => {
  if (!examData.height || !examData.weight) return '-'
  const heightInMeters = examData.height / 100
  const bmi = examData.weight / (heightInMeters * heightInMeters)
  return bmi.toFixed(1)
})

// 判断指标是否异常
const isBMIAbnormal = computed(() => {
  const bmi = Number(calculateBMI.value)
  return bmi < 18.5 || bmi > 24.9
})

const isBloodPressureAbnormal = computed(() => {
  if (!examData.blood_pressure) return false
  const [systolic, diastolic] = examData.blood_pressure.split('/').map(Number)
  return systolic > 140 || systolic < 90 || diastolic > 90 || diastolic < 60
})

const isBloodSugarAbnormal = computed(() => {
  return examData.blood_sugar > 6.1 || examData.blood_sugar < 3.9
})

const isHeartRateAbnormal = computed(() => {
  return examData.heart_rate > 100 || examData.heart_rate < 60
})

// 获取指标状态说明
const getBloodPressureStatus = (bp: string) => {
  if (!bp) return '未测量'
  const [systolic, diastolic] = bp.split('/').map(Number)
  if (systolic > 140 || diastolic > 90) return '偏高'
  if (systolic < 90 || diastolic < 60) return '偏低'
  return '正常'
}

const getBloodSugarStatus = (sugar: number) => {
  if (!sugar) return '未测量'
  if (sugar > 6.1) return '偏高'
  if (sugar < 3.9) return '偏低'
  return '正常'
}

const getHeartRateStatus = (rate: number) => {
  if (!rate) return '未测量'
  if (rate > 100) return '偏快'
  if (rate < 60) return '偏慢'
  return '正常'
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

// 页面加载时获取数据
onMounted(() => {
  fetchExamDetail()
})
</script>

<style scoped>
.physical-exam-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-actions {
  display: flex;
  gap: 10px;
}

.app-card {
  margin-bottom: 20px;
}

.card-header {
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.metric-item {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.metric-item.warning {
  background: #fdf6ec;
}

.metric-icon {
  font-size: 24px;
  color: #409eff;
  margin-right: 16px;
}

.warning .metric-icon {
  color: #e6a23c;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-detail {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
}

.result-section {
  padding: 20px;
}

.result-item {
  margin-bottom: 24px;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-label {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.result-content {
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
}

.attachment-list {
  padding: 20px;
}

.attachment-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.attachment-item:last-child {
  margin-bottom: 0;
}

.file-size {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

@media screen and (max-width: 768px) {
  .physical-exam-detail {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  .page-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  :deep(.el-descriptions) {
    padding: 0 10px;
  }

  :deep(.el-descriptions__cell) {
    padding: 12px 8px;
  }
}
</style> 