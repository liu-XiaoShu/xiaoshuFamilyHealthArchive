<template>
  <div class="vaccination-record-detail">
    <div class="page-header">
      <h2>疫苗接种记录详情</h2>
      <div class="header-actions">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <el-button type="primary" @click="router.push(`/records/vaccination/${id}/edit`)">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
      </div>
    </div>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>基本信息</span>
          <el-tag v-if="record.nextDueDate" type="warning">
            下次接种日期：{{ record.nextDueDate }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="接种日期">
          {{ record.vaccinationDate }}
        </el-descriptions-item>
        <el-descriptions-item label="疫苗名称">
          {{ record.vaccineName }}
        </el-descriptions-item>
        <el-descriptions-item label="生产厂家">
          {{ record.manufacturer }}
        </el-descriptions-item>
        <el-descriptions-item label="批次号">
          {{ record.batchNumber }}
        </el-descriptions-item>
        <el-descriptions-item label="接种剂次">
          第{{ record.doseNumber }}剂
        </el-descriptions-item>
        <el-descriptions-item label="接种地点">
          {{ record.location }}
        </el-descriptions-item>
        <el-descriptions-item label="不良反应" :span="2">
          {{ record.sideEffects || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ record.notes || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 附件列表 -->
      <div v-if="record.attachments?.length" class="section">
        <div class="section-title">相关附件</div>
        <el-table :data="record.attachments" border stripe>
          <el-table-column prop="name" label="文件名称" />
          <el-table-column prop="type" label="文件类型" width="150" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="downloadAttachment(row)">
                <el-icon><Download /></el-icon>下载
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Download } from '@element-plus/icons-vue'
import type { VaccinationRecord } from '@/types/records'

const router = useRouter()
const route = useRoute()
const id = route.params.id as string
const loading = ref(false)
const record = ref<VaccinationRecord>({} as VaccinationRecord)

// 获取记录详情
const fetchRecord = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/vaccination-records/${id}`)
    if (!response.ok) throw new Error('获取记录失败')
    record.value = await response.json()
  } catch (error) {
    ElMessage.error('获取疫苗接种记录失败')
  } finally {
    loading.value = false
  }
}

// 下载附件
const downloadAttachment = async (attachment: { id: number; url: string }) => {
  try {
    const response = await fetch(attachment.url)
    if (!response.ok) throw new Error('下载失败')
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = attachment.url.split('/').pop() || 'download'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载附件失败')
  }
}

onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.vaccination-record-detail {
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

.section {
  margin-top: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}

@media screen and (max-width: 768px) {
  .vaccination-record-detail {
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