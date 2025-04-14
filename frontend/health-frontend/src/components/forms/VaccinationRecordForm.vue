<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="record-form">
    <el-form-item label="疫苗名称" prop="vaccineName">
      <el-input v-model="form.vaccineName" placeholder="输入疫苗名称" />
    </el-form-item>

    <el-form-item label="疫苗类型" prop="vaccineType">
      <el-select v-model="form.vaccineType" placeholder="选择疫苗类型" style="width: 100%">
        <el-option label="新冠疫苗" value="covid19" />
        <el-option label="流感疫苗" value="influenza" />
        <el-option label="乙肝疫苗" value="hepatitisB" />
        <el-option label="肺炎疫苗" value="pneumonia" />
        <el-option label="狂犬病疫苗" value="rabies" />
        <el-option label="其他" value="other" />
      </el-select>
    </el-form-item>

    <el-form-item label="接种医院" prop="hospital">
      <el-input v-model="form.hospital" placeholder="输入接种医院" />
    </el-form-item>

    <el-form-item label="接种日期" prop="vaccinationDate">
      <el-date-picker
        v-model="form.vaccinationDate"
        type="date"
        placeholder="选择接种日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="接种剂次" prop="doseNumber">
      <el-input-number v-model="form.doseNumber" :min="1" :max="10" />
    </el-form-item>

    <el-form-item label="疫苗批号" prop="batchNumber">
      <el-input v-model="form.batchNumber" placeholder="输入疫苗批号" />
    </el-form-item>

    <el-form-item label="制造商" prop="manufacturer">
      <el-input v-model="form.manufacturer" placeholder="输入疫苗制造商" />
    </el-form-item>

    <el-form-item label="接种部位" prop="site">
      <el-radio-group v-model="form.site">
        <el-radio label="leftArm">左上臂</el-radio>
        <el-radio label="rightArm">右上臂</el-radio>
        <el-radio label="leftThigh">左大腿</el-radio>
        <el-radio label="rightThigh">右大腿</el-radio>
        <el-radio label="buttock">臀部</el-radio>
        <el-radio label="other">其他</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="下次接种日期">
      <el-date-picker
        v-model="form.nextDoseDate"
        type="date"
        placeholder="选择下次接种日期"
        style="width: 100%"
      />
    </el-form-item>

    <el-form-item label="接种后反应" prop="reactions">
      <el-checkbox-group v-model="form.reactions">
        <el-checkbox label="none">无</el-checkbox>
        <el-checkbox label="pain">接种部位疼痛</el-checkbox>
        <el-checkbox label="redness">红肿</el-checkbox>
        <el-checkbox label="fever">发热</el-checkbox>
        <el-checkbox label="fatigue">乏力</el-checkbox>
        <el-checkbox label="headache">头痛</el-checkbox>
        <el-checkbox label="allergy">过敏反应</el-checkbox>
      </el-checkbox-group>
      <el-input
        v-if="form.reactions.includes('allergy')"
        v-model="form.allergyDetails"
        type="textarea"
        :rows="2"
        placeholder="请描述过敏反应详情"
        class="mt-2"
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

    <el-form-item label="接种凭证">
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
import { ref, reactive, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadFile } from 'element-plus'

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  vaccineName: '',
  vaccineType: '',
  hospital: '',
  vaccinationDate: new Date(),
  doseNumber: 1,
  batchNumber: '',
  manufacturer: '',
  site: 'leftArm',
  nextDoseDate: null as Date | null,
  reactions: ['none'] as string[],
  allergyDetails: '',
  notes: '',
  certificates: [] as UploadFile[]
})

// 验证规则
const rules = {
  vaccineName: [{ required: true, message: '请输入疫苗名称', trigger: 'blur' }],
  vaccineType: [{ required: true, message: '请选择疫苗类型', trigger: 'change' }],
  hospital: [{ required: true, message: '请输入接种医院', trigger: 'blur' }],
  vaccinationDate: [{ required: true, message: '请选择接种日期', trigger: 'change' }],
  doseNumber: [{ required: true, message: '请输入接种剂次', trigger: 'change' }]
}

// 文件列表
const fileList = ref<UploadFile[]>([])

// 处理文件上传
const handleFileChange = (file: UploadFile) => {
  form.certificates.push(file)
}

// 监听反应选项，如果选了"无"，就清空其他选项
watch(
  () => form.reactions,
  (newVal) => {
    if (newVal.includes('none') && newVal.length > 1) {
      // 如果选了"无"，则清空其他选项
      form.reactions = ['none']
    } else if (newVal.includes('allergy') === false) {
      // 如果没有选择过敏反应，清空过敏详情
      form.allergyDetails = ''
    }
  }
)

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

.mt-2 {
  margin-top: 8px;
}
</style> 