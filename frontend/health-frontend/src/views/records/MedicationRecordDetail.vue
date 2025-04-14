<template>
  <div class="medication-record-detail">
    <div class="page-header">
      <h2>用药记录详情</h2>
      <div class="header-actions">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <el-button type="primary" @click="router.push(`/records/medication/${id}/edit`)">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag :type="getStatusType(record.status)">{{ getStatusLabel(record.status) }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="开始日期">
          {{ record.startDate }}
        </el-descriptions-item>
        <el-descriptions-item label="结束日期">
          {{ record.endDate || '持续中' }}
        </el-descriptions-item>
        <el-descriptions-item label="药品名称">
          {{ record.medicationName }}
        </el-descriptions-item>
        <el-descriptions-item label="剂量">
          {{ record.dosage }}
        </el-descriptions-item>
        <el-descriptions-item label="服用频率">
          {{ record.frequency }}
        </el-descriptions-item>
        <el-descriptions-item label="用药目的">
          {{ record.purpose }}
        </el-descriptions-item>
        <el-descriptions-item label="处方医生" :span="2">
          {{ record.prescribedBy || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="副作用" :span="2">
          {{ record.sideEffects || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ record.notes || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit } from '@element-plus/icons-vue'
import type { MedicationRecord } from '@/types/records'

const router = useRouter()
const route = useRoute()
const id = route.params.id as string
const loading = ref(false)
const record = ref<MedicationRecord>({} as MedicationRecord)

// 获取记录详情
const fetchRecord = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/medication-records/${id}`)
    if (!response.ok) throw new Error('获取记录失败')
    record.value = await response.json()
  } catch (error) {
    ElMessage.error('获取用药记录失败')
  } finally {
    loading.value = false
  }
}

// 获取状态对应的类型
const getStatusType = (status: MedicationRecord['status']) => {
  const types: Record<string, string> = {
    'active': 'success',
    'completed': 'info',
    'discontinued': 'warning'
  }
  return types[status] || 'info'
}

// 获取状态标签文本
const getStatusLabel = (status: MedicationRecord['status']) => {
  const labels: Record<string, string> = {
    'active': '进行中',
    'completed': '已完成',
    'discontinued': '已停用'
  }
  return labels[status] || '未知'
}

onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.medication-record-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media screen and (max-width: 768px) {
  .medication-record-detail {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style> 