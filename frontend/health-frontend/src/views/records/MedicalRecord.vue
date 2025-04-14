<template>
  <div class="medical-record">
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <h2>就医记录管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>新增记录
          </el-button>
        </div>
      </template>

      <!-- 记录列表 -->
      <el-table v-loading="loading" :data="records" style="width: 100%">
        <el-table-column prop="visit_date" label="就诊日期" width="120" sortable />
        <el-table-column prop="hospital" label="医院" width="180" />
        <el-table-column prop="department" label="科室" width="120">
          <template #default="{ row }">
            {{ getDepartmentLabel(row.department) }}
          </template>
        </el-table-column>
        <el-table-column prop="doctor" label="医生" width="120" />
        <el-table-column prop="diagnosis" label="诊断结果" show-overflow-tooltip />
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
      :title="dialogType === 'add' ? '新增就医记录' : '编辑就医记录'"
      width="60%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <el-form-item label="就诊日期" prop="visit_date">
          <el-date-picker
            v-model="form.visit_date"
            type="date"
            placeholder="选择就诊日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="医院" prop="hospital">
          <el-input v-model="form.hospital" placeholder="请输入医院名称" />
        </el-form-item>
        <el-form-item label="科室" prop="department">
          <el-select v-model="form.department" placeholder="请选择科室" style="width: 100%">
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="医生" prop="doctor">
          <el-input v-model="form.doctor" placeholder="请输入医生姓名" />
        </el-form-item>
        <el-form-item label="主诉" prop="chief_complaint">
          <el-input
            v-model="form.chief_complaint"
            type="textarea"
            rows="2"
            placeholder="请输入主诉"
          />
        </el-form-item>
        <el-form-item label="诊断结果" prop="diagnosis">
          <el-input
            v-model="form.diagnosis"
            type="textarea"
            rows="3"
            placeholder="请输入诊断结果"
          />
        </el-form-item>
        <el-form-item label="处理方案" prop="treatment">
          <el-input
            v-model="form.treatment"
            type="textarea"
            rows="3"
            placeholder="请输入处理方案"
          />
        </el-form-item>
        <el-form-item label="复诊日期" prop="follow_up_date">
          <el-date-picker
            v-model="form.follow_up_date"
            type="date"
            placeholder="选择复诊日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="费用" prop="cost">
          <el-input-number
            v-model="form.cost"
            :precision="2"
            :step="100"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            rows="2"
            placeholder="请输入备注信息"
          />
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
import { defineComponent, ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import axios from '@/utils/axios'
import type { MedicalRecord, PaginatedResponse } from '@/types/records'

export default defineComponent({
  name: 'MedicalRecord',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const records = ref<MedicalRecord[]>([])
    const total = ref(0)
    const page = ref(1)
    const pageSize = ref(10)
    const dialogVisible = ref(false)
    const dialogType = ref<'add' | 'edit'>('add')
    const formRef = ref<FormInstance>()
    const form = ref<Partial<MedicalRecord>>({})
    const rules = {
      visit_date: [{ required: true, message: '请选择就诊日期', trigger: 'blur' }],
      hospital: [{ required: true, message: '请输入医院名称', trigger: 'blur' }],
      department: [{ required: true, message: '请选择科室', trigger: 'blur' }],
      doctor: [{ required: true, message: '请输入医生姓名', trigger: 'blur' }],
      chief_complaint: [{ required: true, message: '请输入主诉', trigger: 'blur' }],
      diagnosis: [{ required: true, message: '请输入诊断结果', trigger: 'blur' }],
      treatment: [{ required: true, message: '请输入治疗方案', trigger: 'blur' }],
      cost: [{ required: true, message: '请输入费用', trigger: 'blur' }]
    }

    const departmentOptions = [
      { value: 'IM', label: '内科' },
      { value: 'SG', label: '外科' },
      { value: 'GY', label: '妇科' },
      { value: 'PE', label: '儿科' },
      { value: 'DE', label: '皮肤科' },
      { value: 'EN', label: '耳鼻喉科' },
      { value: 'OP', label: '眼科' },
      { value: 'ST', label: '口腔科' },
      { value: 'OT', label: '其他' }
    ]

    const fetchRecords = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/records/medical/', {
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
        visit_date: '',
        hospital: '',
        department: '',
        doctor: '',
        chief_complaint: '',
        diagnosis: '',
        treatment: '',
        follow_up_date: '',
        cost: 0,
        notes: ''
      }
      dialogVisible.value = true
    }

    const showEditDialog = (row: MedicalRecord) => {
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
              await axios.post('/api/records/medical/', form.value)
              ElMessage.success('添加成功')
            } else {
              await axios.put(`/api/records/medical/${form.value.id}/`, form.value)
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

    const handleDelete = async (row: MedicalRecord) => {
      try {
        await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
          type: 'warning'
        })
        await axios.delete(`/api/records/medical/${row.id}/`)
        ElMessage.success('删除成功')
        fetchRecords()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败')
        }
      }
    }

    const handleSizeChange = (val: number) => {
      pageSize.value = val
      fetchRecords()
    }

    const handleCurrentChange = (val: number) => {
      page.value = val
      fetchRecords()
    }

    const getDepartmentLabel = (value: string) => {
      const option = departmentOptions.find(opt => opt.value === value)
      return option ? option.label : value
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
      departmentOptions,
      showAddDialog,
      showEditDialog,
      handleSubmit,
      handleDelete,
      handleSizeChange,
      handleCurrentChange,
      getDepartmentLabel
    }
  }
})
</script>

<style scoped>
.medical-record {
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
</style> 