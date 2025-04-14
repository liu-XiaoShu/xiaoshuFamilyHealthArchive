<template>
  <div class="records-container">
    <div class="records-header">
      <h2>健康记录列表</h2>
      <el-button type="primary" @click="$router.push('/records/create')">
        新建记录
      </el-button>
    </div>

    <el-card v-loading="recordsStore.loading">
      <el-table :data="recordsStore.recordsList" style="width: 100%">
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="record_type" label="记录类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.record_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="记录日期" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                type="primary"
                :icon="Edit"
                @click="$router.push(`/records/${row.id}`)"
                text
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                :icon="Delete"
                @click="handleDelete(row)"
                text
              >
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRecordsStore } from '@/stores/records'
import { Edit, Delete } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const recordsStore = useRecordsStore()

onMounted(async () => {
  try {
    await recordsStore.getRecords()
  } catch (error: any) {
    ElMessage.error(error || '获取记录列表失败')
  }
})

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning'
    })
    await recordsStore.deleteRecord(row.id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error || '删除失败')
    }
  }
}
</script>

<style scoped>
.records-container {
  padding: 20px;
}

.records-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.records-header h2 {
  margin: 0;
}
</style> 