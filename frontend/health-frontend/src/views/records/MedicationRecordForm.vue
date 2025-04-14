<template>
  <div class="medication-record-form">
    <div class="page-header">
      <h2>{{ isEdit ? '编辑用药记录' : '新建用药记录' }}</h2>
    </div>

    <el-card v-loading="loading">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="药品名称" prop="medication_name">
              <el-input
                v-model="formData.medication_name"
                placeholder="请输入药品名称"
                maxlength="100"
                show-word-limit
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="剂量" prop="dosage">
              <el-input
                v-model="formData.dosage"
                placeholder="请输入用药剂量，如：5mg/次"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服用频率" prop="frequency">
              <el-input
                v-model="formData.frequency"
                placeholder="请输入服用频率，如：每日三次"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="formData.start_date"
                type="date"
                placeholder="请选择开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="formData.end_date"
                type="date"
                placeholder="请选择结束日期（可选）"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <div class="form-actions">
          <el-button @click="$router.back()">取消</el-button>
          <el-button type="primary" native-type="submit" :loading="submitting">
            保存
          </el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecordsStore } from '@/stores/records'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const route = useRoute()
const router = useRouter()
const recordsStore = useRecordsStore()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)
const recordId = computed(() => Number(route.params.id))

const formData = reactive({
  medication_name: '',
  dosage: '',
  frequency: '',
  start_date: '',
  end_date: '',
  notes: '',
  user: authStore.user?.id
})

const rules = {
  medication_name: [
    { required: true, message: '请输入药品名称', trigger: 'blur' },
    { max: 100, message: '药品名称不能超过100个字符', trigger: 'blur' }
  ],
  dosage: [
    { required: true, message: '请输入用药剂量', trigger: 'blur' }
  ],
  frequency: [
    { required: true, message: '请输入服用频率', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ]
}

const fetchRecord = async () => {
  if (!isEdit.value) return
  
  loading.value = true
  try {
    const record = recordsStore.getMedicationRecordById(recordId.value)
    if (record) {
      Object.assign(formData, record)
    }
  } catch (error) {
    ElMessage.error('获取记录失败')
    router.push('/records/medication')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      await recordsStore.updateMedicationRecord(recordId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await recordsStore.createMedicationRecord(formData)
      ElMessage.success('创建成功')
    }
    
    router.push('/records/medication')
  } catch (error: any) {
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchRecord()
})
</script>

<style scoped>
.medication-record-form {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 