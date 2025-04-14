<template>
  <div class="medical-record-detail">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>返回
        </el-button>
        <h2>就医记录详情</h2>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleEdit">
          <el-icon><Edit /></el-icon>编辑
        </el-button>
        <el-popconfirm
          title="确定要删除这条记录吗？"
          @confirm="handleDelete"
          width="220"
        >
          <template #reference>
            <el-button type="danger">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <div class="detail-content" v-loading="loading">
      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="就诊日期">
            {{ record.visitDate }}
          </el-descriptions-item>
          <el-descriptions-item label="医院">
            {{ record.hospital }}
          </el-descriptions-item>
          <el-descriptions-item label="科室">
            {{ record.department }}
          </el-descriptions-item>
          <el-descriptions-item label="医生">
            {{ record.doctor }}
          </el-descriptions-item>
          <el-descriptions-item label="主诉" :span="2">
            {{ record.chiefComplaint }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <span>诊疗信息</span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="诊断结果" :span="2">
            {{ record.diagnosis }}
          </el-descriptions-item>
          <el-descriptions-item label="处理方案" :span="2">
            {{ record.treatment }}
          </el-descriptions-item>
          <el-descriptions-item label="复诊日期">
            {{ record.followUpDate || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="费用">
            ¥{{ record.cost?.toFixed(2) || '0.00' }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ record.notes || '无' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <span>附件</span>
          </div>
        </template>

        <el-empty v-if="!record.attachments?.length" description="暂无附件" />
        <el-table
          v-else
          :data="record.attachments"
          style="width: 100%"
        >
          <el-table-column prop="name" label="文件名" />
          <el-table-column prop="size" label="大小" width="120">
            <template #default="{ row }">
              {{ formatFileSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="uploadTime" label="上传时间" width="180" />
          <el-table-column fixed="right" label="操作" width="120">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                @click="downloadFile(row)"
              >
                下载
              </el-button>
              <el-button
                type="primary"
                link
                @click="previewFile(row)"
              >
                预览
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

// 记录数据
const record = ref<{
  id?: number
  visitDate: string
  hospital: string
  department: string
  doctor: string
  chiefComplaint: string
  diagnosis: string
  treatment: string
  followUpDate?: string
  cost?: number
  notes?: string
  attachments?: Array<{
    id: number
    name: string
    size: number
    url: string
    uploadTime: string
  }>
}>({
  visitDate: '',
  hospital: '',
  department: '',
  doctor: '',
  chiefComplaint: '',
  diagnosis: '',
  treatment: ''
})

// 获取记录详情
const fetchRecordDetail = async () => {
  loading.value = true
  try {
    const response = await fetch(`/api/records/medical/${route.params.id}`)
    const data = await response.json()
    
    if (data.success) {
      record.value = data.data
    } else {
      ElMessage.error(data.message || '获取记录详情失败')
      router.back()
    }
  } catch (error) {
    console.error('获取记录详情失败:', error)
    ElMessage.error('获取记录详情失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 处理编辑
const handleEdit = () => {
  router.push(`/records/medical/edit/${route.params.id}`)
}

// 处理删除
const handleDelete = async () => {
  try {
    const response = await fetch(`/api/records/medical/${route.params.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success('删除成功')
      router.back()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 下载文件
const downloadFile = async (file: typeof record.value.attachments[0]) => {
  try {
    const response = await fetch(file.url)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

// 预览文件
const previewFile = (file: typeof record.value.attachments[0]) => {
  window.open(file.url, '_blank')
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchRecordDetail()
})
</script>

<style scoped>
.medical-record-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media screen and (max-width: 768px) {
  .medical-record-detail {
    padding: 10px;
  }

  .header-left h2 {
    font-size: 20px;
  }

  .header-left {
    gap: 8px;
  }

  .header-actions {
    gap: 8px;
  }
}
</style> 