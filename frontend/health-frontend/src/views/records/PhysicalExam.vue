<template>
  <div class="physical-exam">
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <h2>体检报告管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>新增记录
          </el-button>
        </div>
      </template>

      <!-- 记录列表 -->
      <el-table v-loading="loading" :data="records" style="width: 100%">
        <el-table-column prop="exam_date" label="体检日期" width="120" sortable />
        <el-table-column prop="height" label="身高(cm)" width="100" />
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column prop="blood_pressure" label="血压(mmHg)" width="120" />
        <el-table-column prop="heart_rate" label="心率(bpm)" width="100" />
        <el-table-column label="BMI" width="100">
          <template #default="{ row }">
            {{ calculateBMI(row.height, row.weight) }}
          </template>
        </el-table-column>
        <el-table-column prop="blood_glucose" label="血糖(mmol/L)" width="120" />
        <el-table-column prop="cholesterol" label="胆固醇(mmol/L)" width="120" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" type="primary" @click="showEditDialog(row)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增体检报告' : '编辑体检报告'"
      width="60%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="体检日期" prop="exam_date">
          <el-date-picker
            v-model="form.exam_date"
            type="date"
            placeholder="选择体检日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="身高(cm)" prop="height">
          <el-input-number
            v-model="form.height"
            :precision="1"
            :step="0.1"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="体重(kg)" prop="weight">
          <el-input-number
            v-model="form.weight"
            :precision="1"
            :step="0.1"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="血压(mmHg)" prop="blood_pressure">
          <el-input
            v-model="form.blood_pressure"
            placeholder="格式：收缩压/舒张压 如：120/80"
          />
        </el-form-item>
        <el-form-item label="心率(bpm)" prop="heart_rate">
          <el-input-number
            v-model="form.heart_rate"
            :min="0"
            :max="300"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="血糖(mmol/L)" prop="blood_glucose">
          <el-input-number
            v-model="form.blood_glucose"
            :precision="1"
            :step="0.1"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="胆固醇(mmol/L)" prop="cholesterol">
          <el-input-number
            v-model="form.cholesterol"
            :precision="1"
            :step="0.1"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="体检报告PDF" prop="report_pdf">
          <el-upload
            class="upload-demo"
            action="/api/records/physical-exam/upload/"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            accept=".pdf"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                只能上传PDF文件，且不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, UploadProps } from 'element-plus'
import axios from '@/utils/axios'
import type { PhysicalExam, PaginatedResponse } from '@/types/records'

export default defineComponent({
  name: 'PhysicalExam',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const records = ref<PhysicalExam[]>([])
    const total = ref(0)
    const page = ref(1)
    const pageSize = ref(10)
    const dialogVisible = ref(false)
    const dialogType = ref<'add' | 'edit'>('add')
    const formRef = ref<FormInstance>()
    const form = ref<Partial<PhysicalExam>>({})
    const rules = {
      exam_date: [{ required: true, message: '请选择体检日期', trigger: 'blur' }],
      height: [{ required: true, message: '请输入身高', trigger: 'blur' }],
      weight: [{ required: true, message: '请输入体重', trigger: 'blur' }],
      blood_pressure: [{ required: true, message: '请输入血压', trigger: 'blur' }],
      heart_rate: [{ required: true, message: '请输入心率', trigger: 'blur' }]
    }

    const calculateBMI = (height: number, weight: number) => {
      if (!height || !weight) return '-'
      const heightInMeters = height / 100
      return (weight / (heightInMeters * heightInMeters)).toFixed(1)
    }

    const fetchRecords = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/records/physical-exam/', {
          params: {
            page: page.value,
            page_size: pageSize.value
          }
        })
        records.value = response.data.results
        total.value = response.data.count
      } catch (error) {
        ElMessage.error('获取记录列表失败')
      } finally {
        loading.value = false
      }
    }

    const showAddDialog = () => {
      dialogType.value = 'add'
      form.value = {
        exam_date: '',
        height: 0,
        weight: 0,
        blood_pressure: '',
        heart_rate: 0,
        blood_glucose: null,
        cholesterol: null,
        report_pdf: ''
      }
      dialogVisible.value = true
    }

    const showEditDialog = (row: PhysicalExam) => {
      dialogType.value = 'edit'
      form.value = { ...row }
      dialogVisible.value = true
    }

    const handleSubmit = async () => {
      if (!formRef.value) return
      
      await formRef.value.validate(async (valid) => {
        if (valid) {
          try {
            if (dialogType.value === 'add') {
              await axios.post('/api/records/physical-exam/', form.value)
              ElMessage.success('添加成功')
            } else {
              await axios.put(`/api/records/physical-exam/${form.value.id}/`, form.value)
              ElMessage.success('更新成功')
            }
            dialogVisible.value = false
            fetchRecords()
          } catch (error) {
            ElMessage.error(dialogType.value === 'add' ? '添加失败' : '更新失败')
          }
        }
      })
    }

    const handleDelete = async (row: PhysicalExam) => {
      try {
        await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
          type: 'warning'
        })
        await axios.delete(`/api/records/physical-exam/${row.id}/`)
        ElMessage.success('删除成功')
        fetchRecords()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }

    const beforeUpload: UploadProps['beforeUpload'] = (file) => {
      const isPDF = file.type === 'application/pdf'
      if (!isPDF) {
        ElMessage.error('只能上传PDF文件！')
        return false
      }
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        ElMessage.error('文件大小不能超过10MB！')
        return false
      }
      return true
    }

    const handleUploadSuccess = (response: any) => {
      form.value.report_pdf = response.data.url
      ElMessage.success('文件上传成功')
    }

    const handleUploadError = () => {
      ElMessage.error('文件上传失败')
    }

    const handleSizeChange = (val: number) => {
      pageSize.value = val
      fetchRecords()
    }

    const handleCurrentChange = (val: number) => {
      page.value = val
      fetchRecords()
    }

    onMounted(() => {
      fetchRecords()
    })

    return {
      loading,
      records,
      total,
      page,
      pageSize,
      dialogVisible,
      dialogType,
      formRef,
      form,
      rules,
      calculateBMI,
      showAddDialog,
      showEditDialog,
      handleSubmit,
      handleDelete,
      beforeUpload,
      handleUploadSuccess,
      handleUploadError,
      handleSizeChange,
      handleCurrentChange
    }
  }
})
</script>

<style scoped>
.physical-exam {
  padding: 20px;
}

.record-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.upload-demo {
  width: 100%;
}

.el-upload__tip {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
}
</style> 