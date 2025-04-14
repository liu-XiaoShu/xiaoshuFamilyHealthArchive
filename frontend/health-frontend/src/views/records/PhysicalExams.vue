<template>
  <div class="physical-exams-container">
    <div class="page-header">
      <div class="page-title">体检记录</div>
      <el-button type="primary" @click="router.push('/records/physical/new')">
        <el-icon><Plus /></el-icon>新增体检记录
      </el-button>
    </div>

    <!-- 搜索过滤 -->
    <div class="app-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
          />
        </el-form-item>
        <el-form-item label="体检类型">
          <el-select v-model="searchForm.examType" placeholder="请选择">
            <el-option label="全部" value="" />
            <el-option label="年度体检" value="annual" />
            <el-option label="入职体检" value="employment" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据列表 -->
    <div class="app-card">
      <el-table
        v-loading="loading"
        :data="examList"
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="exam_date" label="体检日期" sortable="custom" width="120">
          <template #default="{ row }">
            {{ formatDate(row.exam_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="exam_type" label="体检类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTag(row.exam_type)">
              {{ getExamTypeLabel(row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hospital" label="体检医院" />
        <el-table-column prop="summary" label="体检总结" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', row.status]">
              {{ getStatusLabel(row.status) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewExam(row)">
              查看
            </el-button>
            <el-button link type="primary" @click="editExam(row)">
              编辑
            </el-button>
            <el-button link type="success" @click="viewReport(row)">
              查看报告
            </el-button>
            <el-popconfirm
              title="确定要删除这条记录吗？"
              @confirm="deleteExam(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="体检记录详情"
      width="70%"
      class="exam-detail-dialog"
    >
      <div v-if="currentExam" class="exam-detail">
        <div class="detail-section">
          <h3>基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="体检日期">
              {{ formatDate(currentExam.exam_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="体检类型">
              {{ getExamTypeLabel(currentExam.exam_type) }}
            </el-descriptions-item>
            <el-descriptions-item label="体检医院">
              {{ currentExam.hospital }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              {{ getStatusLabel(currentExam.status) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h3>体检指标</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="身高">
              {{ currentExam.height }} cm
            </el-descriptions-item>
            <el-descriptions-item label="体重">
              {{ currentExam.weight }} kg
            </el-descriptions-item>
            <el-descriptions-item label="BMI">
              {{ calculateBMI(currentExam.height, currentExam.weight) }}
            </el-descriptions-item>
            <el-descriptions-item label="血压">
              {{ currentExam.blood_pressure }}
            </el-descriptions-item>
            <el-descriptions-item label="血糖">
              {{ currentExam.blood_sugar }}
            </el-descriptions-item>
            <el-descriptions-item label="心率">
              {{ currentExam.heart_rate }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h3>体检总结</h3>
          <div class="summary-content">{{ currentExam.summary }}</div>
        </div>

        <div class="detail-section">
          <h3>建议</h3>
          <div class="advice-content">{{ currentExam.advice }}</div>
        </div>

        <div v-if="currentExam.attachments?.length" class="detail-section">
          <h3>附件</h3>
          <div class="attachment-list">
            <div
              v-for="file in currentExam.attachments"
              :key="file.id"
              class="attachment-item"
            >
              <el-link :href="file.url" target="_blank" type="primary">
                <el-icon><Document /></el-icon>
                {{ file.name }}
              </el-link>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { format } from 'date-fns'

const router = useRouter()
const loading = ref(false)
const dialogVisible = ref(false)
const currentExam = ref(null)
const examList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 搜索表单
const searchForm = reactive({
  dateRange: [],
  examType: ''
})

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 1)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setMonth(start.getMonth() - 3)
      return [start, end]
    }
  }
]

// 获取体检记录列表
const fetchExamList = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      start_date: searchForm.dateRange[0],
      end_date: searchForm.dateRange[1],
      exam_type: searchForm.examType
    }
    const response = await axios.get('/api/records/physical', { params })
    examList.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取体检记录失败')
    console.error('获取体检记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewExam = (exam: any) => {
  currentExam.value = exam
  dialogVisible.value = true
}

// 编辑记录
const editExam = (exam: any) => {
  router.push(`/records/physical/${exam.id}/edit`)
}

// 删除记录
const deleteExam = async (exam: any) => {
  try {
    await axios.delete(`/api/records/physical/${exam.id}`)
    ElMessage.success('删除成功')
    fetchExamList()
  } catch (error) {
    ElMessage.error('删除失败')
    console.error('删除失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchExamList()
}

// 重置搜索
const resetSearch = () => {
  searchForm.dateRange = []
  searchForm.examType = ''
  handleSearch()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchExamList()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchExamList()
}

// 排序处理
const handleSortChange = ({ prop, order }: any) => {
  // 实现排序逻辑
}

// 格式化日期
const formatDate = (date: string) => {
  return format(new Date(date), 'yyyy-MM-dd')
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

// 获取体检类型标签文本
const getExamTypeLabel = (type: string) => {
  const typeMap: { [key: string]: string } = {
    annual: '年度体检',
    employment: '入职体检',
    other: '其他'
  }
  return typeMap[type] || type
}

// 获取状态标签文本
const getStatusLabel = (status: string) => {
  const statusMap: { [key: string]: string } = {
    normal: '正常',
    abnormal: '异常',
    pending: '待复查'
  }
  return statusMap[status] || status
}

// 计算BMI
const calculateBMI = (height: number, weight: number) => {
  if (!height || !weight) return '-'
  const heightInMeters = height / 100
  const bmi = weight / (heightInMeters * heightInMeters)
  return bmi.toFixed(1)
}

// 查看报告
const viewReport = (row: any) => {
  router.push(`/physical-exams/${row.id}/report`)
}

// 页面加载时获取数据
fetchExamList()
</script>

<style scoped>
.physical-exams-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.exam-detail {
  padding: 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.summary-content,
.advice-content {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

@media screen and (max-width: 768px) {
  .physical-exams-container {
    padding: 10px;
  }

  .search-form {
    flex-direction: column;
  }

  .search-form .el-form-item {
    margin-right: 0;
    width: 100%;
  }
}
</style> 