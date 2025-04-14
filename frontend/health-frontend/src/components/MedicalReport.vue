<template>
  <div class="medical-report">
    <!-- 报告头部 -->
    <div class="report-header">
      <div class="back-button" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
      </div>
      <div class="title">体检报告</div>
      <div class="actions">
        <el-icon><More /></el-icon>
        <el-icon class="record-icon"><VideoCamera /></el-icon>
      </div>
    </div>
    
    <!-- 用户信息 -->
    <div class="user-info">
      <h2>{{ report.userName || '用户姓名' }}</h2>
      <div class="report-id">
        检查号：{{ report.examId || '000000000000000' }}
      </div>
      <div class="report-date">
        体检日期：{{ formatDate(report.examDate) || '0000-00-00' }}
      </div>
    </div>
    
    <!-- 下载报告按钮 -->
    <div class="download-section">
      <el-button type="success" plain class="download-btn">
        <el-icon><Download /></el-icon>
        下载报告
      </el-button>
      <el-button type="primary" plain class="more-btn">
        更多
      </el-button>
    </div>
    
    <!-- 人体异常区域显示 -->
    <div class="body-abnormal">
      <div class="body-image">
        <object type="image/svg+xml" data="/images/human_body.svg" class="body-model">
          人体模型图片无法加载
        </object>
        
        <!-- 异常标记 -->
        <div v-for="(issue, index) in abnormalIssues" :key="index"
          class="abnormal-marker" 
          :class="issue.severity"
          :style="{
            top: `${issue.position.top}%`,
            left: `${issue.position.left}%`
          }"
        >
          <div class="marker-label">{{ issue.name }}</div>
        </div>
      </div>
      
      <!-- 指标信息 -->
      <div class="metrics">
        <div class="metric-item" v-for="metric in metrics" :key="metric.name">
          <div class="metric-label">{{ metric.label }}</div>
          <div class="metric-value" :class="{ 'abnormal': metric.isAbnormal }">
            {{ metric.value }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 分页指示器 -->
    <div class="pagination-dots">
      <div class="dot active"></div>
      <div class="dot"></div>
    </div>
    
    <!-- 异常结果与建议 -->
    <div class="results-section">
      <div class="section-header">
        <h3>异常结果与建议</h3>
        <span class="issue-count">{{ abnormalIssues.length }}项</span>
      </div>
      
      <div class="results-list">
        <div v-for="(issue, index) in abnormalIssues" :key="index" class="result-item">
          <div class="result-title">【{{ index + 1 }}】 {{ issue.name }}。</div>
          <div class="result-detail" v-if="issue.description">
            {{ issue.description }}
          </div>
          <div class="result-suggestion" v-if="issue.suggestion">
            建议{{ issue.suggestion }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 完整报告按钮 -->
    <div class="full-report">
      <el-button type="primary" class="full-report-btn">
        完整报告
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineProps, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, More, VideoCamera, Download } from '@element-plus/icons-vue'
import { format } from 'date-fns'
import { recordsApi } from '@/api/records'

const props = defineProps<{
  reportId: string
}>()

const router = useRouter()

interface AbnormalIssue {
  name: string
  severity: 'mild' | 'moderate' | 'severe'
  description: string
  suggestion: string
  position: {
    top: number
    left: number
  }
}

// 模拟数据
const report = ref({
  id: '123456',
  examId: '039121240427364',
  examDate: new Date('2024-04-27'),
  userName: '刘述瑶',
  age: 32,
  gender: '女'
})

// 身体指标数据
const metrics = ref([
  {
    label: '身高',
    value: '163.5(cm)',
    isAbnormal: false
  },
  {
    label: '体重',
    value: '57.3(kg)',
    isAbnormal: false
  },
  {
    label: '舒张压',
    value: '68(mmHg)',
    isAbnormal: false
  },
  {
    label: '收缩压',
    value: '107(mmHg)',
    isAbnormal: false
  }
])

// 异常项
const abnormalIssues = ref<AbnormalIssue[]>([
  {
    name: '嗜酸性粒细胞值偏高',
    severity: 'mild',
    description: '',
    suggestion: '定期复查血常规。',
    position: { top: 25, left: 30 }
  },
  {
    name: '肝囊肿',
    severity: 'moderate',
    description: '',
    suggestion: '定期复查肝脏彩超。',
    position: { top: 45, left: 25 }
  },
  {
    name: '脂肪肝',
    severity: 'moderate',
    description: '总胆固醇值偏高(5.23mmol/L)(参考值≤5.2)。',
    suggestion: '控制饮食和健康的生活方式，心内科随诊。',
    position: { top: 45, left: 68 }
  },
  {
    name: '窦性心动过缓',
    severity: 'mild',
    description: '',
    suggestion: '心内科随诊。',
    position: { top: 35, left: 58 }
  },
  {
    name: '血脂异常',
    severity: 'moderate',
    description: '血脂异常是一类较常见的疾病，是人体内脂蛋白的代谢异常，主要包括总胆固醇和低密度脂蛋白胆固醇、甘油三酯升高和或高密度脂蛋白胆固醇降低等。血脂异常是导致动脉粥样硬化的重要因素之一，是冠心病和缺血性脑卒中的独立危险因素。',
    suggestion: '控制饮食和健康的生活方式。',
    position: { top: 55, left: 32 }
  }
])

// 格式化日期
const formatDate = (date: Date | string | undefined) => {
  if (!date) return ''
  return format(new Date(date), 'yyyy-MM-dd')
}

// 加载报告数据
const loadReportData = async () => {
  if (!props.reportId) return
  
  try {
    // 从API获取数据
    const data = await recordsApi.getPhysicalExamReport(props.reportId)
    
    // 更新报告数据
    report.value = {
      id: data.id,
      examId: data.exam_id || data.id,
      examDate: new Date(data.exam_date),
      userName: data.user_name || '用户',
      age: data.age || 30,
      gender: data.gender || '未知'
    }
    
    // 更新指标数据
    metrics.value = [
      {
        label: '身高',
        value: `${data.height}(cm)`,
        isAbnormal: false
      },
      {
        label: '体重',
        value: `${data.weight}(kg)`,
        isAbnormal: false
      },
      {
        label: '舒张压',
        value: data.blood_pressure ? data.blood_pressure.split('/')[1] + '(mmHg)' : '--',
        isAbnormal: false
      },
      {
        label: '收缩压',
        value: data.blood_pressure ? data.blood_pressure.split('/')[0] + '(mmHg)' : '--',
        isAbnormal: false
      }
    ]
    
    // 如果有异常数据，更新异常项
    if (data.abnormal_items && data.abnormal_items.length) {
      abnormalIssues.value = data.abnormal_items.map((item: any) => ({
        name: item.name,
        severity: item.severity || 'moderate',
        description: item.description || '',
        suggestion: item.suggestion || '请咨询医生获取专业建议。',
        position: item.position || { top: Math.random() * 60 + 20, left: Math.random() * 60 + 20 }
      }))
    }
    
  } catch (error) {
    console.error('获取报告数据失败:', error)
    ElMessage.error('获取报告数据失败')
  }
}

// 监听reportId变化
watch(() => props.reportId, (newId) => {
  if (newId) {
    loadReportData()
  }
}, { immediate: true })

onMounted(() => {
  if (props.reportId) {
    loadReportData()
  }
})
</script>

<style scoped>
.medical-report {
  max-width: 100%;
  background-color: #f5f7fa;
  min-height: 100vh;
  padding-bottom: 20px;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #2C8D63;
  color: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-button {
  font-size: 24px;
  cursor: pointer;
}

.title {
  font-size: 18px;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 16px;
  font-size: 20px;
}

.record-icon {
  background-color: white;
  color: #2C8D63;
  border-radius: 50%;
  padding: 5px;
  font-size: 16px;
}

.user-info {
  padding: 20px 16px;
  background: white;
  margin-bottom: 10px;
}

.user-info h2 {
  font-size: 24px;
  margin: 0 0 10px 0;
}

.report-id, .report-date {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.download-section {
  display: flex;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 15px;
}

.download-btn {
  flex: 3;
  margin-right: 10px;
}

.more-btn {
  flex: 1;
}

.body-abnormal {
  position: relative;
  background: white;
  padding: 20px 16px;
  margin-bottom: 15px;
}

.body-image {
  position: relative;
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.body-model {
  width: 100%;
  height: 450px;
  object-fit: contain;
}

.abnormal-marker {
  position: absolute;
  background-color: #f56c6c;
  color: white;
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 2;
}

.abnormal-marker.mild {
  background-color: #e6a23c;
}

.abnormal-marker.moderate {
  background-color: #f56c6c;
}

.abnormal-marker.severe {
  background-color: #f56c6c;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: space-around;
}

.metric-item {
  background-color: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 20px;
  padding: 5px 15px;
  text-align: center;
  min-width: 140px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
}

.metric-value {
  color: #67c23a;
  font-weight: 500;
}

.metric-value.abnormal {
  color: #f56c6c;
}

.pagination-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 15px 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #dcdfe6;
}

.dot.active {
  background-color: #409eff;
  width: 20px;
  border-radius: 4px;
}

.results-section {
  background: white;
  padding: 20px 16px;
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  font-size: 18px;
  margin: 0;
  font-weight: 500;
}

.issue-count {
  background-color: #f56c6c;
  color: white;
  border-radius: 15px;
  padding: 2px 10px;
  font-size: 14px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.result-item {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
}

.result-title {
  font-weight: 500;
  margin-bottom: 10px;
}

.result-detail {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.5;
}

.result-suggestion {
  font-size: 14px;
  color: #409eff;
}

.full-report {
  padding: 0 16px;
  margin-top: 20px;
}

.full-report-btn {
  width: 100%;
}

@media (max-width: 768px) {
  .body-model {
    height: 300px;
  }
  
  .metrics {
    flex-direction: column;
    align-items: center;
  }
  
  .metric-item {
    width: 100%;
    max-width: 300px;
  }
}
</style> 