<template>
  <div class="medication-record">
    <el-card class="record-card">
      <template #header>
        <div class="card-header">
          <h2>用药记录管理</h2>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon>新增记录
          </el-button>
        </div>
      </template>

      <!-- 记录列表 -->
      <el-table v-loading="loading" :data="records" style="width: 100%">
        <el-table-column prop="drug_name" label="药品名称" width="180" />
        <el-table-column prop="dosage" label="剂量规格" width="120" />
        <el-table-column prop="frequency" label="用药频率" width="120">
          <template #default="{ row }">
            {{ getFrequencyLabel(row.frequency) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" width="120" sortable />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column prop="reminder_enabled" label="提醒" width="80">
          <template #default="{ row }">
            <el-tag :type="row.reminder_enabled ? 'success' : 'info'">
              {{ row.reminder_enabled ? '开启' : '关闭' }}
            </el-tag>
          </template>
        </el-table-column>
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
      :title="dialogType === 'add' ? '新增用药记录' : '编辑用药记录'"
      width="60%"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="right"
      >
        <el-form-item label="药品名称" prop="drug_name">
          <el-input v-model="form.drug_name" placeholder="请输入药品名称" />
        </el-form-item>
        <el-form-item label="剂量规格" prop="dosage">
          <el-input v-model="form.dosage" placeholder="例如：500mg/片" />
        </el-form-item>
        <el-form-item label="用药频率" prop="frequency">
          <el-select v-model="form.frequency" placeholder="请选择用药频率" style="width: 100%">
            <el-option
              v-for="item in frequencyOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="启用提醒" prop="reminder_enabled">
          <el-switch v-model="form.reminder_enabled" />
        </el-form-item>
        <el-form-item
          label="提醒时间"
          prop="reminder_time"
          v-if="form.reminder_enabled"
        >
          <el-time-picker
            v-model="form.reminder_time"
            placeholder="选择提醒时间"
            style="width: 100%"
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
import type { MedicationRecord, PaginatedResponse } from '@/types/records'

export default defineComponent({
  name: 'MedicationRecord',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const records = ref<MedicationRecord[]>([])
    const total = ref(0)
    const page = ref(1)
    const pageSize = ref(10)
    const dialogVisible = ref(false)
    const dialogType = ref<'add' | 'edit'>('add')
    const formRef = ref<FormInstance>()
    const form = ref<Partial<MedicationRecord>>({})

    const frequencyOptions = [
      { value: 'QD', label: '每日一次' },
      { value: 'BID', label: '每日两次' },
      { value: 'TID', label: '每日三次' },
      { value: 'QW', label: '每周一次' },
      { value: 'PRN', label: '按需服用' }
    ]

    const rules = {
      drug_name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
      dosage: [{ required: true, message: '请输入剂量规格', trigger: 'blur' }],
      frequency: [{ required: true, message: '请选择用药频率', trigger: 'change' }],
      start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
      reminder_time: [{ required: true, message: '请选择提醒时间', trigger: 'change' }]
    }

    const fetchRecords = async () => {
      loading.value = true
      try {
        const response = await axios.get('/api/records/medication/', {
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
        drug_name: '',
        dosage: '',
        frequency: 'QD',
        start_date: '',
        end_date: '',
        reminder_enabled: false,
        reminder_time: null
      }
      dialogVisible.value = true
    }

    const showEditDialog = (row: MedicationRecord) => {
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
              await axios.post('/api/records/medication/', form.value)
              ElMessage.success('添加成功')
            } else {
              await axios.put(`/api/records/medication/${form.value.id}/`, form.value)
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

    const handleDelete = async (row: MedicationRecord) => {
      try {
        await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
          type: 'warning'
        })
        await axios.delete(`/api/records/medication/${row.id}/`)
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

    const getFrequencyLabel = (value: string) => {
      const option = frequencyOptions.find(opt => opt.value === value)
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
      frequencyOptions,
      showAddDialog,
      showEditDialog,
      handleSubmit,
      handleDelete,
      handleSizeChange,
      handleCurrentChange,
      getFrequencyLabel
    }
  }
})
</script>

<style scoped>
.medication-record {
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