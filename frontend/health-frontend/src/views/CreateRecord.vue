<template>
  <div class="create-container">
    <el-form :model="form" label-width="120px">
      <h2>新建健康记录</h2>
      <el-form-item label="指标类型">
        <el-select v-model="form.indicator">
          <el-option label="心率" :value="1" />
          <el-option label="血压" :value="2" />
          <el-option label="血糖" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="检测数值">
        <el-input-number v-model="form.value" />
      </el-form-item>
      <el-form-item label="检测时间">
        <el-date-picker
          v-model="form.check_time"
          type="datetime"
          value-format="YYYY-MM-DDTHH:mm:ssZ"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const form = reactive({
  indicator: 1,
  value: 0,
  check_time: new Date().toISOString()
})

const submitForm = async () => {
  try {
    await api.createRecord(form)
    ElMessage.success('创建成功')
    router.push('/records')
  } catch (error) {
    ElMessage.error('创建失败：' + error.response.data)
  }
}
</script>

