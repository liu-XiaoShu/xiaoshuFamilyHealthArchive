<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="record-form">
    <el-form-item label="就医日期" prop="visitDate">
      <el-date-picker
        v-model="form.visitDate"
        type="date"
        placeholder="选择就医日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="医院名称" prop="hospital">
      <el-input v-model="form.hospital" placeholder="输入医院名称" />
    </el-form-item>

    <el-form-item label="科室" prop="department">
      <el-input v-model="form.department" placeholder="输入科室名称" />
    </el-form-item>

    <el-form-item label="医生姓名" prop="doctorName">
      <el-input v-model="form.doctorName" placeholder="输入医生姓名" />
    </el-form-item>
    
    <el-form-item label="就诊原因" prop="reason">
      <el-input 
        v-model="form.reason" 
        type="textarea" 
        :rows="3" 
        placeholder="描述就诊原因"
      />
    </el-form-item>

    <el-form-item label="诊断结果" prop="diagnosis">
      <el-input 
        v-model="form.diagnosis" 
        type="textarea" 
        :rows="3" 
        placeholder="输入医生诊断"
      />
    </el-form-item>

    <el-form-item label="处方药物" prop="prescriptions">
      <el-tag
        v-for="(tag, index) in form.prescriptions"
        :key="index"
        closable
        @close="removePrescription(index)"
        class="prescription-tag"
      >
        {{ tag }}
      </el-tag>
      <el-input
        v-if="prescriptionInputVisible"
        ref="prescriptionInputRef"
        v-model="prescriptionInputValue"
        @keyup.enter="addPrescription"
        @blur="addPrescription"
        class="prescription-input"
      />
      <el-button v-else size="small" @click="showPrescriptionInput">
        + 添加药物
      </el-button>
    </el-form-item>

    <el-form-item label="备注" prop="notes">
      <el-input 
        v-model="form.notes" 
        type="textarea" 
        :rows="2" 
        placeholder="添加备注"
      />
    </el-form-item>

    <el-form-item label="上传附件">
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
import { ref, reactive, nextTick, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  visitDate: new Date(),
  hospital: '',
  department: '',
  doctorName: '',
  reason: '',
  diagnosis: '',
  prescriptions: [] as string[],
  notes: '',
  attachments: [] as UploadFile[]
})

// 验证规则
const rules = {
  visitDate: [{ required: true, message: '请选择就医日期', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入医院名称', trigger: 'blur' }],
  department: [{ required: true, message: '请输入科室名称', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入就诊原因', trigger: 'blur' }]
}

// 处理处方药物输入
const prescriptionInputVisible = ref(false)
const prescriptionInputValue = ref('')
const prescriptionInputRef = ref()
const fileList = ref<UploadFile[]>([])

// 显示处方药物输入框
const showPrescriptionInput = () => {
  prescriptionInputVisible.value = true
  nextTick(() => {
    prescriptionInputRef.value.focus()
  })
}

// 添加处方药物
const addPrescription = () => {
  if (prescriptionInputValue.value) {
    form.prescriptions.push(prescriptionInputValue.value)
    prescriptionInputValue.value = ''
  }
  prescriptionInputVisible.value = false
}

// 移除处方药物
const removePrescription = (index: number) => {
  form.prescriptions.splice(index, 1)
}

// 处理文件上传
const handleFileChange = (file: UploadFile) => {
  form.attachments.push(file)
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

onMounted(() => {
  // 可以在这里添加初始化逻辑，例如从API获取医院列表
})
</script>

<style scoped>
.record-form {
  max-width: 800px;
  margin: 0 auto;
}

.prescription-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.prescription-input {
  width: 100px;
  margin-right: 8px;
  vertical-align: top;
}
</style> 