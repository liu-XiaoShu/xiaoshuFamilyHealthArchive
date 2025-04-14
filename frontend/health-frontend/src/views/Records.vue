<template>
  <div class="records-container">
    <div class="header">
      <h2>健康记录管理</h2>
      <el-button type="primary" @click="$router.push('/create')">新建记录</el-button>
    </div>

    <el-table :data="records" style="width: 100%">
      <el-table-column prop="indicator_name" label="指标" />
      <el-table-column prop="value" label="数值" />
      <el-table-column prop="check_time" label="检测时间" />
      <el-table-column prop="is_abnormal" label="异常状态">
        <template #default="{row}">
          <el-tag :type="row.is_abnormal ? 'danger' : 'success'">
            {{ row.is_abnormal ? '异常' : '正常' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const records = ref([])

onMounted(async () => {
  try {
    const res = await api.getRecords()
    records.value = res.data.results
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
})
</script>

