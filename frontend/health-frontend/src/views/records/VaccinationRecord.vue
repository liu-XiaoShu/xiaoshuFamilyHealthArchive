<template>
  <div class="vaccination-record">
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <h2>疫苗接种记录管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>新增记录
          </el-button>
        </div>
      </template>

      <!-- 记录列表 -->
      <el-table v-loading="loading" :data="records" style="width: 100%">
        <el-table-column prop="vaccine_type" label="疫苗类型" width="120">
          <template #default="{ row }">
            {{ getVaccineTypeLabel(row.vaccine_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="dose_number" label="剂次" width="80" />
        <el-table-column prop="vaccination_date" label="接种日期" width="120" sortable />
        <el-table-column prop="next_due_date" label="下次接种日期" width="120" />
        <el-table-column prop="institution" label="接种机构" />
        <el-table-column prop="batch_number" label="疫苗批号" width="120" />
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
      :title="dialogType === 'add' ? '新增疫苗接种记录' : '编辑疫苗接种记录'"
      width="60%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        label-position="right"
      >
        <el-form-item label="疫苗类型" prop="vaccine_type">
          <el-select v-model="form.vaccine_type" placeholder="请选择疫苗类型" style="width: 100%">
            <el-option
              v-for="item in vaccineTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="剂次" prop="dose_number">
          <el-input-number
            v-model="form.dose_number"
            :min="1"
            :max="10"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="接种日期" prop="vaccination_date">
          <el-date-picker
            v-model="form.vaccination_date"
            type="date"
            placeholder="选择接种日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="下次接种日期" prop="next_due_date">
          <el-date-picker
            v-model="form.next_due_date"
            type="date"
            placeholder="选择下次接种日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="接种机构" prop="institution">
          <el-input v-model="form.institution" placeholder="请输入接种机构" />
        </el-form-item>
        <el-form-item label="疫苗批号" prop="batch_number">
          <el-input v-model="form.batch_number" placeholder="请输入疫苗批号" />
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
import type { VaccinationRecord, PaginatedResponse } from '@/types/records'

export default defineComponent({
  name: 'VaccinationRecord',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const records = ref<VaccinationRecord[]>([])
    const total = ref(0)
    const page = ref(1)
    const pageSize = ref(10)
    const dialogVisible = ref(false)
    const dialogType = ref<'add' | 'edit'>('add')
    const formRef = ref<FormInstance>()
    const form = ref<Partial<VaccinationRecord>>({})

    const vaccineTypeOptions = [
      { value: 'CV', label: '新冠疫苗' },
      { value: 'FL', label: '流感疫苗' },
      { value: 'HPV', label: 'HPV疫苗' },
      { value: 'HB', label: '乙肝疫苗' }
    ]

    const rules = {
      vaccine_type: [{ required: true, message: '请选择疫苗类型', trigger: 'change' }],
      dose_number: [{ required: true, message: '请输入剂次', trigger: 'blur' }],
      vaccination_date: [{ required: true, message: '请选择接种日期', trigger: 'change' }],
      institution: [{ required: true, message: '请输入接种机构', trigger: 'blur' }],
      batch_number: [{ required: true, message: '请输入疫苗批号', trigger: 'blur' }]
    }

    const fetchRecords = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/records/vaccination/', {
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
        vaccine_type: '',
        dose_number: 1,
        vaccination_date: '',
        next_due_date: '',
        institution: '',
        batch_number: ''
      }
      dialogVisible.value = true
    }

    const showEditDialog = (row: VaccinationRecord) => {
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
              await axios.post('/api/records/vaccination/', form.value)
              ElMessage.success('添加成功')
            } else {
              await axios.put(`/api/records/vaccination/${form.value.id}/`, form.value)
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

    const handleDelete = async (row: VaccinationRecord) => {
      try {
        await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
          type: 'warning'
        })
        await axios.delete(`/api/records/vaccination/${row.id}/`)
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

    const getVaccineTypeLabel = (value: string) => {
      const option = vaccineTypeOptions.find(opt => opt.value === value)
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
      vaccineTypeOptions,
      showAddDialog,
      showEditDialog,
      handleSubmit,
      handleDelete,
      handleSizeChange,
      handleCurrentChange,
      getVaccineTypeLabel
    }
  }
})
</script>

<style scoped>
.vaccination-record {
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