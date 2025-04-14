<template>
  <div class="medication-records-container">
    <div class="page-header">
      <h2>用药记录</h2>
      <el-button type="primary" @click="$router.push('/medication/new')">
        <el-icon><Plus /></el-icon>新增记录
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="药品名称">
          <el-input v-model="searchForm.drugName" placeholder="请输入药品名称" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 记录列表 -->
    <el-table
      v-loading="loading"
      :data="records"
      style="width: 100%"
      border
    >
      <el-table-column prop="startDate" label="开始日期" width="120" />
      <el-table-column prop="endDate" label="结束日期" width="120" />
      <el-table-column prop="drugName" label="药品名称" width="200" />
      <el-table-column prop="dosage" label="剂量" width="120" />
      <el-table-column prop="frequency" label="服用频率" width="120" />
      <el-table-column prop="purpose" label="用药目的" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTag(row.status)">{{ row.statusText }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button type="primary" link @click="viewRecord(row.id)">
              查看
            </el-button>
            <el-button type="primary" link @click="editRecord(row.id)">
              编辑
            </el-button>
            <el-button type="danger" link @click="deleteRecord(row.id)">
              删除
            </el-button>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const loading = ref(false)
const records = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const searchForm = ref({
  dateRange: [],
  drugName: ''
})

// 获取记录列表
const fetchRecords = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/medication-records', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        start_date: searchForm.value.dateRange[0],
        end_date: searchForm.value.dateRange[1],
        drug_name: searchForm.value.drugName
      }
    })
    records.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取记录失败')
  } finally {
    loading.value = false
  }
}

// 获取状态对应的标签类型
const getStatusTag = (status: string) => {
  const statusMap: Record<string, string> = {
    'active': 'success',
    'completed': '',
    'discontinued': 'warning',
    'on_hold': 'info'
  }
  return statusMap[status] || ''
}

// 查看记录
const viewRecord = (id: number) => {
  // TODO: 实现查看详情功能
}

// 编辑记录
const editRecord = (id: number) => {
  // TODO: 跳转到编辑页面
}

// 删除记录
const deleteRecord = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`/api/medication-records/${id}`)
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchRecords()
}

// 重置搜索
const resetSearch = () => {
  searchForm.value = {
    dateRange: [],
    drugName: ''
  }
  handleSearch()
}

// 分页
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchRecords()
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.medication-records-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-bar {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

@media screen and (max-width: 768px) {
  .medication-records-container {
    padding: 10px;
  }

  .search-bar {
    padding: 10px;
  }

  .el-form--inline .el-form-item {
    margin-right: 0;
    width: 100%;
  }
}
</style> 