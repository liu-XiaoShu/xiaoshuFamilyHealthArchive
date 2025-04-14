<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="record-form">
    <el-form-item label="体检日期" prop="examDate">
      <el-date-picker
        v-model="form.examDate"
        type="date"
        placeholder="选择体检日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="体检医院" prop="hospital">
      <el-input v-model="form.hospital" placeholder="输入体检医院" />
    </el-form-item>

    <el-form-item label="体检类型" prop="examType">
      <el-select v-model="form.examType" placeholder="选择体检类型" style="width: 100%">
        <el-option label="常规体检" value="regular" />
        <el-option label="入职体检" value="employment" />
        <el-option label="婚前体检" value="premarital" />
        <el-option label="孕前体检" value="prepregnancy" />
        <el-option label="老年人体检" value="elderly" />
        <el-option label="儿童体检" value="children" />
        <el-option label="其他" value="other" />
      </el-select>
    </el-form-item>

    <el-divider content-position="center">基本指标</el-divider>

    <el-row :gutter="20">
      <el-col :xs="24" :sm="12">
        <el-form-item label="身高(cm)" prop="height">
          <el-input-number v-model="form.height" :min="0" :max="300" :precision="1" />
        </el-form-item>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-form-item label="体重(kg)" prop="weight">
          <el-input-number v-model="form.weight" :min="0" :max="500" :precision="1" />
        </el-form-item>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-form-item label="BMI">
          <el-input :value="calculateBMI" disabled />
        </el-form-item>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-form-item label="血压(mmHg)" prop="bloodPressure">
          <div class="bp-input-group">
            <el-input v-model="form.systolicPressure" placeholder="收缩压">
              <template #prefix>高</template>
            </el-input>
            <span class="bp-separator">/</span>
            <el-input v-model="form.diastolicPressure" placeholder="舒张压">
              <template #prefix>低</template>
            </el-input>
          </div>
        </el-form-item>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-form-item label="心率(次/分)" prop="heartRate">
          <el-input-number v-model="form.heartRate" :min="0" :max="300" />
        </el-form-item>
      </el-col>
      
      <el-col :xs="24" :sm="12">
        <el-form-item label="体温(°C)" prop="temperature">
          <el-input-number v-model="form.temperature" :min="20" :max="45" :precision="1" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="center">体检项目</el-divider>

    <el-form-item label="体检项目">
      <el-checkbox-group v-model="form.examItems">
        <el-checkbox label="bloodRoutine">血常规</el-checkbox>
        <el-checkbox label="urineRoutine">尿常规</el-checkbox>
        <el-checkbox label="liverFunction">肝功能</el-checkbox>
        <el-checkbox label="kidneyFunction">肾功能</el-checkbox>
        <el-checkbox label="bloodLipids">血脂</el-checkbox>
        <el-checkbox label="bloodGlucose">血糖</el-checkbox>
        <el-checkbox label="electrocardiogram">心电图</el-checkbox>
        <el-checkbox label="chestXRay">胸部X光</el-checkbox>
        <el-checkbox label="ultrasound">B超</el-checkbox>
        <el-checkbox label="tumorMarker">肿瘤标志物</el-checkbox>
        <el-checkbox label="thyroidFunction">甲状腺功能</el-checkbox>
      </el-checkbox-group>
    </el-form-item>

    <el-form-item label="检查结果" prop="result">
      <el-radio-group v-model="form.result">
        <el-radio label="normal">正常</el-radio>
        <el-radio label="abnormal">异常</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item v-if="form.result === 'abnormal'" label="异常项目">
      <div class="abnormal-items">
        <div v-for="(item, index) in form.abnormalItems" :key="index" class="abnormal-item">
          <el-input 
            v-model="form.abnormalItems[index].name" 
            placeholder="异常项目名称"
            class="abnormal-name" 
          />
          <el-input 
            v-model="form.abnormalItems[index].value" 
            placeholder="检测值"
            class="abnormal-value" 
          />
          <el-input 
            v-model="form.abnormalItems[index].reference" 
            placeholder="参考范围"
            class="abnormal-reference" 
          />
          <el-button 
            type="danger" 
            circle 
            size="small" 
            @click="removeAbnormalItem(index)"
            :disabled="form.abnormalItems.length <= 1"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <el-button type="primary" size="small" @click="addAbnormalItem">
          添加异常项目
        </el-button>
      </div>
    </el-form-item>

    <el-form-item label="医生建议" prop="doctorAdvice">
      <el-input 
        v-model="form.doctorAdvice" 
        type="textarea" 
        :rows="3" 
        placeholder="医生建议内容"
      />
    </el-form-item>

    <el-form-item label="下次体检时间">
      <el-date-picker
        v-model="form.nextExamDate"
        type="date"
        placeholder="选择下次体检日期"
        style="width: 100%"
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

    <el-form-item label="上传报告">
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
import { ref, reactive, computed, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  examDate: new Date(),
  hospital: '',
  examType: 'regular',
  height: 170,
  weight: 60,
  systolicPressure: '120',
  diastolicPressure: '80',
  heartRate: 75,
  temperature: 36.5,
  examItems: ['bloodRoutine', 'urineRoutine', 'electrocardiogram'] as string[],
  result: 'normal',
  abnormalItems: [
    { name: '', value: '', reference: '' }
  ],
  doctorAdvice: '',
  nextExamDate: null as Date | null,
  notes: '',
  reports: [] as UploadFile[]
})

// 验证规则
const rules = {
  examDate: [{ required: true, message: '请选择体检日期', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入体检医院', trigger: 'blur' }],
  examType: [{ required: true, message: '请选择体检类型', trigger: 'change' }],
  height: [{ required: true, message: '请输入身高', trigger: 'blur' }],
  weight: [{ required: true, message: '请输入体重', trigger: 'blur' }],
  systolicPressure: [{ required: true, message: '请输入收缩压', trigger: 'blur' }],
  diastolicPressure: [{ required: true, message: '请输入舒张压', trigger: 'blur' }]
}

// 计算BMI
const calculateBMI = computed(() => {
  if (form.height && form.weight) {
    const heightInMeters = form.height / 100
    const bmi = form.weight / (heightInMeters * heightInMeters)
    return bmi.toFixed(1)
  }
  return ''
})

// 文件列表
const fileList = ref<UploadFile[]>([])

// 添加异常项目
const addAbnormalItem = () => {
  form.abnormalItems.push({ name: '', value: '', reference: '' })
}

// 移除异常项目
const removeAbnormalItem = (index: number) => {
  if (form.abnormalItems.length > 1) {
    form.abnormalItems.splice(index, 1)
  }
}

// 处理文件上传
const handleFileChange = (file: UploadFile) => {
  form.reports.push(file)
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

// 监视检查结果，如果是正常，则清空异常项目
watch(
  () => form.result,
  (newVal) => {
    if (newVal === 'normal') {
      form.abnormalItems = [{ name: '', value: '', reference: '' }]
    }
  }
)
</script>

<style scoped>
.record-form {
  max-width: 800px;
  margin: 0 auto;
}

.bp-input-group {
  display: flex;
  align-items: center;
}

.bp-separator {
  margin: 0 8px;
  font-size: 18px;
  font-weight: bold;
}

.abnormal-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.abnormal-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.abnormal-name {
  flex: 2;
}

.abnormal-value, .abnormal-reference {
  flex: 1;
}

@media (max-width: 768px) {
  .abnormal-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .abnormal-name, .abnormal-value, .abnormal-reference {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style> 