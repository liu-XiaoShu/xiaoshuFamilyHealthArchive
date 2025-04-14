<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="record-form">
    <el-form-item label="药品名称" prop="medicationName">
      <el-input v-model="form.medicationName" placeholder="输入药品名称" />
    </el-form-item>

    <el-form-item label="药品类型" prop="medicationType">
      <el-select v-model="form.medicationType" placeholder="选择药品类型" style="width: 100%">
        <el-option label="处方药" value="prescription" />
        <el-option label="非处方药" value="otc" />
        <el-option label="中药" value="traditional" />
        <el-option label="保健品" value="supplement" />
        <el-option label="其他" value="other" />
      </el-select>
    </el-form-item>

    <el-form-item label="规格" prop="specification">
      <el-input v-model="form.specification" placeholder="例如：5mg/片" />
    </el-form-item>

    <el-form-item label="用法用量" prop="dosage">
      <el-input v-model="form.dosage" placeholder="例如：每日3次，每次1片" />
    </el-form-item>

    <el-form-item label="开始日期" prop="startDate">
      <el-date-picker
        v-model="form.startDate"
        type="date"
        placeholder="选择开始用药日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="结束日期" prop="endDate">
      <el-date-picker
        v-model="form.endDate"
        type="date"
        placeholder="选择结束用药日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="是否长期用药">
      <el-switch v-model="form.isLongTerm" />
    </el-form-item>

    <el-form-item label="提醒设置" v-if="form.isLongTerm">
      <div class="reminder-settings">
        <el-checkbox-group v-model="form.reminderDays">
          <el-checkbox v-for="day in daysOfWeek" :key="day.value" :label="day.value">
            {{ day.label }}
          </el-checkbox>
        </el-checkbox-group>
        <div class="reminder-times">
          <el-time-picker
            v-for="(time, index) in form.reminderTimes"
            :key="index"
            v-model="form.reminderTimes[index]"
            format="HH:mm"
            placeholder="选择时间"
            class="reminder-time-picker"
          />
          <el-button 
            type="primary" 
            circle 
            size="small" 
            @click="addReminderTime" 
            :disabled="form.reminderTimes.length >= 5"
          >
            <el-icon><Plus /></el-icon>
          </el-button>
          <el-button 
            type="danger" 
            circle 
            size="small" 
            @click="removeReminderTime" 
            :disabled="form.reminderTimes.length <= 1"
          >
            <el-icon><Minus /></el-icon>
          </el-button>
        </div>
      </div>
    </el-form-item>

    <el-form-item label="适应症状" prop="symptoms">
      <el-input 
        v-model="form.symptoms" 
        type="textarea" 
        :rows="2" 
        placeholder="描述药物适应的症状"
      />
    </el-form-item>

    <el-form-item label="不良反应" prop="sideEffects">
      <el-input 
        v-model="form.sideEffects" 
        type="textarea" 
        :rows="2" 
        placeholder="描述可能的不良反应"
      />
    </el-form-item>

    <el-form-item label="备注" prop="notes">
      <el-input 
        v-model="form.notes" 
        type="textarea" 
        :rows="2" 
        placeholder="添加备注"
      />
    </el-form-item>

    <el-form-item label="药品图片">
      <el-upload
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        list-type="picture-card"
      >
        <el-icon><Plus /></el-icon>
      </el-upload>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="submitForm">保存</el-button>
      <el-button @click="cancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Plus, Minus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInstance>()

// 星期几选项
const daysOfWeek = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 0 }
]

// 表单数据
const form = reactive({
  medicationName: '',
  medicationType: '',
  specification: '',
  dosage: '',
  startDate: new Date(),
  endDate: null as Date | null,
  isLongTerm: false,
  reminderDays: [1, 2, 3, 4, 5, 6, 0], // 默认每天提醒
  reminderTimes: [new Date(new Date().setHours(8, 0, 0, 0))], // 默认早上8点提醒
  symptoms: '',
  sideEffects: '',
  notes: '',
  images: [] as UploadFile[]
})

// 验证规则
const rules = {
  medicationName: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  medicationType: [{ required: true, message: '请选择药品类型', trigger: 'change' }],
  dosage: [{ required: true, message: '请输入用法用量', trigger: 'blur' }],
  startDate: [{ required: true, message: '请选择开始用药日期', trigger: 'change' }]
}

// 文件列表
const fileList = ref<UploadFile[]>([])

// 添加提醒时间
const addReminderTime = () => {
  if (form.reminderTimes.length < 5) {
    form.reminderTimes.push(new Date(new Date().setHours(8, 0, 0, 0)))
  }
}

// 移除提醒时间
const removeReminderTime = () => {
  if (form.reminderTimes.length > 1) {
    form.reminderTimes.pop()
  }
}

// 处理文件上传
const handleFileChange = (file: UploadFile) => {
  form.images.push(file)
}

// 提交表单
const submitForm = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      emit('submit', { ...form })
    } else {
      ElMessage.error('请完成必填项')
      return false
    }
  })
}

// 取消操作
const cancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.record-form {
  max-width: 800px;
  margin: 0 auto;
}

.reminder-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reminder-times {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 8px;
}

.reminder-time-picker {
  width: 120px;
}
</style> 