<template>
  <div class="home">
    <el-row :gutter="20" class="mb-4">
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <el-card class="welcome-card">
          <template #header>
            <div class="card-header">
              <h2>欢迎使用小树家健康管理系统</h2>
              <div class="user-actions">
                <el-dropdown trigger="click">
                  <el-button type="primary" size="small">
                    账户操作 <el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="$router.push('/profile')">
                        <el-icon><User /></el-icon> 个人资料
                      </el-dropdown-item>
                      <el-dropdown-item @click="$router.push('/settings')">
                        <el-icon><Setting /></el-icon> 账号设置
                      </el-dropdown-item>
                      <el-dropdown-item divided @click="logout">
                        <el-icon><SwitchButton /></el-icon> 退出登录
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </template>
          <div class="user-profile-summary">
            <div class="user-info">
              <el-avatar 
                :size="64" 
                :src="userAvatar" 
                :icon="UserIcon" 
                class="user-avatar"
              />
              <div class="user-details">
                <h3>{{ userInfo?.username || '未知用户' }}</h3>
                <p>{{ userInfo?.email || '无邮箱' }}</p>
                <p>{{ userInfo?.phone || '无电话' }}</p>
              </div>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <p class="stat-value">{{ healthStats.medical_records.total }}</p>
                <p class="stat-label">就医记录</p>
              </div>
              <div class="stat-item">
                <p class="stat-value">{{ healthStats.medication_records.total }}</p>
                <p class="stat-label">用药记录</p>
              </div>
              <div class="stat-item">
                <p class="stat-value">{{ healthStats.vaccination_records.total }}</p>
                <p class="stat-label">疫苗记录</p>
              </div>
              <div class="stat-item">
                <p class="stat-value">{{ healthStats.physical_exams.total }}</p>
                <p class="stat-label">体检报告</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card class="announcement-card">
          <template #header>
            <div class="card-header">
              <h3>健康提醒</h3>
            </div>
          </template>
          <div class="announcements">
            <div v-for="(item, index) in healthReminders" :key="index" class="announcement-item">
              <div class="announcement-icon">
                <el-icon :size="24" :color="item.color"><component :is="item.icon" /></el-icon>
              </div>
              <div class="announcement-content">
                <h4>{{ item.title }}</h4>
                <p>{{ item.content }}</p>
                <span class="announcement-time">{{ item.time }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mb-4">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>健康概览</h3>
              <el-button type="primary" size="small" @click="refreshHealthData">刷新数据</el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-wrapper">
            <el-skeleton :rows="3" animated />
          </div>
          <div v-else class="health-overview">
            <div class="health-stats-overview">
              <div class="stat-card">
                <div class="stat-value">{{ healthStats?.medical_records?.total || 0 }}</div>
                <div class="stat-label">就医记录</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ healthStats?.medication_records?.total || 0 }}</div>
                <div class="stat-label">用药记录</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ healthStats?.vaccination_records?.total || 0 }}</div>
                <div class="stat-label">疫苗接种</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ healthStats?.physical_exams?.total || 0 }}</div>
                <div class="stat-label">体检记录</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('medical-records')">
          <template #header>
            <div class="card-header">
              <span>就医记录</span>
              <el-button 
                type="primary" 
                size="small" 
                circle 
                @click.stop="addRecord('medical')"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="feature-content">
            <el-icon :size="40" color="#409EFF"><Briefcase /></el-icon>
            <p>管理就医记录和病历档案</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('medication-records')">
          <template #header>
            <div class="card-header">
              <span>用药记录</span>
              <el-button 
                type="primary" 
                size="small" 
                circle 
                @click.stop="addRecord('medication')"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="feature-content">
            <el-icon :size="40" color="#67C23A"><Notebook /></el-icon>
            <p>管理用药记录和药物信息</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('vaccination-records')">
          <template #header>
            <div class="card-header">
              <span>疫苗接种</span>
              <el-button 
                type="primary" 
                size="small" 
                circle 
                @click.stop="addRecord('vaccination')"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="feature-content">
            <el-icon :size="40" color="#E6A23C"><Stamp /></el-icon>
            <p>管理疫苗接种记录</p>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="feature-card" @click="navigateTo('physical-exams')">
          <template #header>
            <div class="card-header">
              <span>体检报告</span>
              <el-button 
                type="primary" 
                size="small" 
                circle 
                @click.stop="addRecord('physical')"
              >
                <el-icon><Plus /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="feature-content">
            <el-icon :size="40" color="#F56C6C"><Odometer /></el-icon>
            <p>管理体检报告和记录</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加记录对话框 -->
    <el-dialog
      v-model="addRecordDialogVisible"
      :title="getRecordTypeTitle()"
      width="60%"
      destroy-on-close
    >
      <component 
        :is="currentFormComponent" 
        v-if="addRecordDialogVisible"
        @submit="submitRecord"
        @cancel="addRecordDialogVisible = false"
      />
    </el-dialog>

    <!-- 健康趋势图表 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>健康趋势</span>
            </div>
          </template>
          
          <el-tabs>
            <el-tab-pane label="血压">
              <LineChart
                v-if="!loading && healthTrend.dates.length > 0"
                :dates="healthTrend.dates"
                :data="[healthTrend.bloodPressure.systolic, healthTrend.bloodPressure.diastolic]"
                :labels="['收缩压', '舒张压']"
                unit="mmHg"
                title="血压趋势"
              />
              <div v-else class="chart-loading">
                <el-empty v-if="!loading" description="暂无数据" />
                <el-skeleton v-else :rows="5" animated />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="血糖">
              <LineChart
                v-if="!loading && healthTrend.dates.length > 0"
                :dates="healthTrend.dates"
                :data="healthTrend.bloodSugar"
                unit="mmol/L"
                title="血糖趋势"
              />
              <div v-else class="chart-loading">
                <el-empty v-if="!loading" description="暂无数据" />
                <el-skeleton v-else :rows="5" animated />
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="体重">
              <LineChart
                v-if="!loading && healthTrend.dates.length > 0"
                :dates="healthTrend.dates"
                :data="healthTrend.weight"
                unit="kg"
                title="体重趋势"
              />
              <div v-else class="chart-loading">
                <el-empty v-if="!loading" description="暂无数据" />
                <el-skeleton v-else :rows="5" animated />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近健康活动 -->
    <el-row :gutter="20" class="mt-4">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期活动</span>
              <el-button text @click="refreshHealthData">刷新</el-button>
            </div>
          </template>
          
          <el-timeline v-if="!loading && recentActivities.length > 0">
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.date"
              :type="getActivityType(activity.type)"
            >
              <div class="activity-content">
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.description }}</p>
                <el-button 
                  type="primary" 
                  link 
                  size="small" 
                  @click="goToActivityDetail(activity.type, activity.id)"
                >
                  查看详情
                </el-button>
              </div>
            </el-timeline-item>
          </el-timeline>
          
          <div v-else-if="!loading" class="empty-activities">
            <el-empty description="暂无活动记录" />
          </div>
          
          <div v-else class="loading-activities">
            <el-skeleton :rows="5" animated />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Briefcase, Notebook, Stamp, Odometer, 
  Plus, User as UserIcon, ArrowDown, Setting, 
  SwitchButton, Bell, MoreFilled, 
  Calendar, Warning, Check
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import MedicalRecordForm from '@/components/forms/MedicalRecordForm.vue'
import MedicationRecordForm from '@/components/forms/MedicationRecordForm.vue'
import VaccinationRecordForm from '@/components/forms/VaccinationRecordForm.vue'
import PhysicalExamForm from '@/components/forms/PhysicalExamForm.vue'
import { recordsApi } from '@/api/records'
import axios from 'axios'
import LineChart from '@/components/LineChart.vue'
import type { User } from '@/types/auth'
import type { MedicalRecord, MedicationRecord, VaccinationRecord, PhysicalExam, HealthStatistics, HealthTrend, RecentActivity } from '@/api/records'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const router = useRouter()
const authStore = useAuthStore()

// 添加记录对话框控制
const addRecordDialogVisible = ref(false)
const currentRecordType = ref<'medical' | 'medication' | 'vaccination' | 'physical' | null>(null)

// 动态组件处理
const currentFormComponent = computed(() => {
  switch (currentRecordType.value) {
    case 'medical': return MedicalRecordForm
    case 'medication': return MedicationRecordForm
    case 'vaccination': return VaccinationRecordForm
    case 'physical': return PhysicalExamForm
    default: return null
  }
})

// 用户信息
const userInfo = computed(() => authStore.user as User)
const userAvatar = computed(() => {
  return userInfo.value?.avatar || ''
})

// 健康统计信息
const healthStats = ref<HealthStatistics>({
  medical_records: {
    total: 0,
    hospital_count: 0,
    department_count: 0,
    recent: [],
    by_department: []
  },
  medication_records: {
    total: 0,
    active_medications: 0,
    active: 0,
    recent: []
  },
  vaccination_records: {
    total: 0,
    pending_next_dose: 0,
    recent: []
  },
  physical_exams: {
    total: 0,
    abnormal_count: 0,
    abnormal: 0,
    recent: []
  }
})

// 健康提醒
const healthReminders = ref([
  {
    icon: 'Calendar',
    color: '#409EFF',
    title: '年度体检提醒',
    content: '您的年度体检预约日期为2025年4月15日，请准时参加',
    time: '3天后'
  },
  {
    icon: 'Warning',
    color: '#E6A23C',
    title: '血压异常',
    content: '最近记录的血压偏高，建议多休息，减少摄盐',
    time: '今天'
  },
  {
    icon: 'Check',
    color: '#67C23A',
    title: '用药提醒',
    content: '别忘了今晚服用高血压药物',
    time: '今天'
  }
])

// 状态变量
const loading = ref(true)

const latestPhysicalExam = ref<{
  date: string
  result: string
  hospital: string
  items: string[]
} | null>(null)

const latestVaccination = ref<{
  name: string
  date: string
  hospital: string
  nextDose?: string
} | null>(null)

// 健康趋势
const healthTrend = ref<HealthTrend>({
  date: new Date().toISOString().split('T')[0],
  dates: [],
  bloodPressure: {
    systolic: [],
    diastolic: []
  },
  bloodSugar: [],
  weight: []
})

const recentActivities = ref<RecentActivity[]>([])

// 打开添加记录对话框
const addRecord = (type: 'medical' | 'medication' | 'vaccination' | 'physical') => {
  currentRecordType.value = type
  addRecordDialogVisible.value = true
}

// 获取记录类型标题
const getRecordTypeTitle = () => {
  switch (currentRecordType.value) {
    case 'medical': return '添加就医记录'
    case 'medication': return '添加用药记录'
    case 'vaccination': return '添加疫苗接种记录'
    case 'physical': return '添加体检记录'
    default: return '添加记录'
  }
}

// 提交记录表单
const submitRecord = async (formData: any) => {
  try {
    console.log('开始提交记录:', currentRecordType.value, formData)
    
    // 根据记录类型调用相应的API
    switch (currentRecordType.value) {
      case 'medical':
        console.log('提交就医记录', formData)
        // 转换表单数据格式以匹配API期望的格式
        const medicalData: MedicalRecord = {
          visit_date: typeof formData.visitDate === 'string' ? formData.visitDate : formData.visitDate.toISOString().split('T')[0],
          hospital: formData.hospital,
          department: formData.department,
          doctor: formData.doctorName || '',
          chief_complaint: formData.reason || '',  // 主诉字段映射
          diagnosis: formData.diagnosis || '',
          treatment: formData.treatment || formData.prescriptions?.join(', ') || '', // 处理方案
          notes: formData.notes || ''
        }
        
        console.log('医疗记录数据:', medicalData)
        const medicalResult = await recordsApi.createMedicalRecord(medicalData)
        console.log('创建就医记录成功:', medicalResult.data)
        
        // 上传附件（如果有）
        if (formData.attachments && formData.attachments.length > 0) {
          for (const file of formData.attachments) {
            if (file.raw && medicalResult.data && medicalResult.data.id) {
              console.log('上传附件:', file.raw)
              await recordsApi.uploadMedicalRecordAttachment(medicalResult.data.id, file.raw)
            } else {
              console.warn('跳过附件上传: 文件或记录ID缺失', { file, recordId: medicalResult.data?.id })
            }
          }
        }
        
        ElMessage.success('就医记录添加成功')
        break
        
      case 'medication':
        console.log('提交用药记录', formData)
        // 转换为API格式
        const medicationData: MedicationRecord = {
          medical_record: formData.medical_record,
          name: formData.drug_name || '',
          dosage: formData.dosage || '',
          frequency: formData.frequency || 'QD', // 默认每日一次
          purpose: formData.purpose || '',
          start_date: typeof formData.start_date === 'string' ? formData.start_date : formData.start_date.toISOString().split('T')[0],
          end_date: formData.end_date ? (typeof formData.end_date === 'string' ? formData.end_date : formData.end_date.toISOString().split('T')[0]) : undefined,
          side_effects: formData.side_effects || '',
          notes: formData.notes || ''
        }
        
        console.log('用药记录数据:', medicationData)
        const medicationResult = await recordsApi.createMedicationRecord(medicationData)
        console.log('创建用药记录成功:', medicationResult.data)
        
        // 上传图片（如果有）
        if (formData.image && formData.image.raw && medicationResult.data && medicationResult.data.id) {
          console.log('上传药品图片:', formData.image.raw)
          await recordsApi.uploadMedicationImage(medicationResult.data.id, formData.image.raw)
        }
        
        ElMessage.success('用药记录添加成功')
        break
        
      case 'vaccination':
        console.log('提交疫苗接种记录', formData)
        // 转换为API格式
        const vaccinationData: VaccinationRecord = {
          vaccine_name: formData.vaccine_name || '',
          vaccination_date: typeof formData.vaccination_date === 'string' ? formData.vaccination_date : formData.vaccination_date.toISOString().split('T')[0],
          location: formData.hospital || formData.location || '',
          lot_number: formData.batch_number || formData.lot_number || '',
          administered_by: formData.institution || formData.administered_by || '',
          next_due_date: formData.next_due_date ? (typeof formData.next_due_date === 'string' ? formData.next_due_date : formData.next_due_date.toISOString().split('T')[0]) : undefined,
          notes: formData.notes || ''
        }
        
        console.log('疫苗接种数据:', vaccinationData)
        const vaccinationResult = await recordsApi.createVaccinationRecord(vaccinationData)
        console.log('创建疫苗接种记录成功:', vaccinationResult.data)
        
        // 上传证书（如果有）
        if (formData.certificate && formData.certificate.raw && vaccinationResult.data && vaccinationResult.data.id) {
          console.log('上传疫苗证书:', formData.certificate.raw)
          await recordsApi.uploadVaccinationCertificate(vaccinationResult.data.id, formData.certificate.raw)
        }
        
        ElMessage.success('疫苗接种记录添加成功')
        break
        
      case 'physical':
        console.log('提交体检记录', formData)
        // 转换为API格式
        const physicalData: PhysicalExam = {
          exam_date: typeof formData.exam_date === 'string' ? formData.exam_date : formData.exam_date.toISOString().split('T')[0],
          hospital: formData.hospital || '',
          exam_type: formData.exam_type || '常规体检',
          height: formData.height,
          weight: formData.weight,
          blood_pressure: formData.blood_pressure || formData.systolic_pressure + '/' + formData.diastolic_pressure,
          blood_sugar: formData.blood_sugar || formData.blood_glucose,
          heart_rate: formData.heart_rate,
          abnormal_findings: formData.abnormal_findings || formData.abnormal_items?.join(', ') || '',
          doctor_advice: formData.doctor_advice || '',
          next_exam_date: formData.next_exam_date ? (typeof formData.next_exam_date === 'string' ? formData.next_exam_date : formData.next_exam_date.toISOString().split('T')[0]) : undefined
        }
        
        console.log('体检记录数据:', physicalData)
        const physicalResult = await recordsApi.createPhysicalExam(physicalData)
        console.log('创建体检记录成功:', physicalResult.data)
        
        // 上传报告（如果有）
        if (formData.report_file && formData.report_file.raw && physicalResult.data && physicalResult.data.id) {
          console.log('上传体检报告:', formData.report_file.raw)
          await recordsApi.uploadPhysicalExamReport(physicalResult.data.id, formData.report_file.raw)
        }
        
        ElMessage.success('体检记录添加成功')
        break
    }
    
    // 关闭对话框并刷新数据
    addRecordDialogVisible.value = false
    await fetchHealthData()
  } catch (error) {
    console.error('提交记录失败:', error)
    ElMessage.error('记录添加失败，请重试: ' + (error instanceof Error ? error.message : String(error)))
  }
}

// 获取健康数据
const fetchHealthData = async () => {
  try {
    loading.value = true
    
    // 获取健康总览数据
    try {
      const overviewResponse = await recordsApi.getHealthStatistics()
      const overviewData = overviewResponse.data
      
      // 更新统计数据
      healthStats.value = {
        medical_records: {
          total: overviewData.medical_records?.total || 0,
          hospital_count: overviewData.medical_records?.hospital_count || 0,
          department_count: overviewData.medical_records?.department_count || 0,
          recent: overviewData.medical_records?.recent || [],
          by_department: overviewData.medical_records?.by_department || []
        },
        medication_records: {
          total: overviewData.medication_records?.total || 0,
          active_medications: overviewData.medication_records?.active_medications || 0,
          active: overviewData.medication_records?.active || 0,
          recent: overviewData.medication_records?.recent || []
        },
        vaccination_records: {
          total: overviewData.vaccination_records?.total || 0,
          pending_next_dose: overviewData.vaccination_records?.pending_next_dose || 0,
          recent: overviewData.vaccination_records?.recent || []
        },
        physical_exams: {
          total: overviewData.physical_exams?.total || 0,
          abnormal_count: overviewData.physical_exams?.abnormal_count || 0,
          abnormal: overviewData.physical_exams?.abnormal || 0,
          recent: overviewData.physical_exams?.recent || []
        }
      }
      
      // 更新体检数据
      if (overviewData.physical_exams?.recent && overviewData.physical_exams.recent.length > 0) {
        const lastExam = overviewData.physical_exams.recent[0];
        latestPhysicalExam.value = {
          date: lastExam.exam_date || '',
          result: lastExam.result || 'normal',
          hospital: lastExam.hospital || '',
          items: lastExam.exam_items || []
        }
      }
      
      // 更新最近的疫苗接种记录
      if (overviewData.vaccination_records?.recent && overviewData.vaccination_records.recent.length > 0) {
        const latestVaccine = overviewData.vaccination_records.recent[0];
        latestVaccination.value = {
          name: latestVaccine.vaccine_name || '',
          date: latestVaccine.vaccination_date || '',
          hospital: latestVaccine.hospital || '',
          nextDose: latestVaccine.next_dose_date || ''
        }
      }
    } catch (overviewError) {
      console.error('获取健康总览数据失败:', overviewError)
      ElMessage.warning('健康总览数据加载失败')
    }

    // 加载健康趋势数据
    try {
      const [trendsRes, activitiesRes] = await Promise.all([
        recordsApi.getHealthTrends(),
        recordsApi.getRecentActivities()
      ])
      
      // 正确处理健康趋势数据
      if (trendsRes.data && Array.isArray(trendsRes.data)) {
        // 提取日期数组（确保总是返回字符串数组）
        const dates = trendsRes.data.map(item => item.date || '');
        
        // 提取各项指标数据（确保总是返回数字数组）
        const bloodPressureSystolic = trendsRes.data.map(item => {
          if (item.blood_pressure) {
            const parts = item.blood_pressure.split('/');
            return parts.length > 0 ? parseInt(parts[0]) : 0;
          }
          return 0;
        });
        
        const bloodPressureDiastolic = trendsRes.data.map(item => {
          if (item.blood_pressure) {
            const parts = item.blood_pressure.split('/');
            return parts.length > 1 ? parseInt(parts[1]) : 0;
          }
          return 0;
        });
        
        const bloodSugar = trendsRes.data.map(item => {
          return typeof item.blood_sugar === 'number' ? item.blood_sugar : 0;
        });
        
        const weight = trendsRes.data.map(item => {
          return typeof item.weight === 'number' ? item.weight : 0;
        });
        
        // 更新趋势数据（确保数据类型正确）
        healthTrend.value = {
          date: new Date().toISOString().split('T')[0],
          dates: dates,
          bloodPressure: {
            systolic: bloodPressureSystolic,
            diastolic: bloodPressureDiastolic
          },
          bloodSugar: bloodSugar,
          weight: weight
        };
      } else {
        // 如果没有数据，提供默认值
        healthTrend.value = {
          date: new Date().toISOString().split('T')[0],
          dates: ['今天'],
          bloodPressure: {
            systolic: [0],
            diastolic: [0]
          },
          bloodSugar: [0],
          weight: [0]
        };
        console.warn('健康趋势数据格式不正确或为空:', trendsRes.data);
      }
      
      recentActivities.value = activitiesRes.data;
    } catch (error) {
      console.error('获取趋势或活动数据失败:', error)
      ElMessage.warning('部分健康数据加载失败，请稍后刷新')
    }
  } catch (error) {
    console.error('获取健康数据失败:', error)
    ElMessage.error('获取健康数据失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

// 刷新健康数据
const refreshHealthData = () => {
  fetchHealthData()
}

// 页面导航
const navigateTo = (path: string) => {
  router.push(`/${path}`)
}

// 退出登录
const logout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    ElMessage.error('退出登录失败，请重试')
  }
}

// 获取活动类型图标
const getActivityType = (type: string): 'primary' | 'success' | 'warning' | 'danger' => {
  switch (type) {
    case 'medical': return 'primary'
    case 'medication': return 'success'
    case 'vaccination': return 'warning'
    case 'physical': return 'danger'
    default: return 'primary'
  }
}

// 跳转到活动详情页
const goToActivityDetail = (type: string, id: number) => {
  switch (type) {
    case 'medical':
      router.push(`/medical-records/${id}`)
      break
    case 'medication':
      router.push(`/medication-records/${id}`)
      break
    case 'vaccination':
      router.push(`/vaccination-records/${id}`)
      break
    case 'physical':
      router.push(`/physical-exams/${id}`)
      break
    default:
      console.error('未知活动类型')
  }
}

// 初始化
onMounted(() => {
  // 加载初始数据
  fetchHealthData()
})
</script>

<style scoped>
.home {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 24px;
}

.welcome-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.user-profile-summary {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-details {
  flex: 1;
}

.user-details h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.user-details p {
  margin: 0 0 4px;
  color: var(--el-text-color-secondary);
}

.user-stats {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  margin-top: 16px;
}

.stat-item {
  text-align: center;
  flex: 1;
  min-width: 90px;
  padding: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--el-color-primary);
}

.stat-label {
  font-size: 14px;
  margin: 0;
  color: var(--el-text-color-secondary);
}

.announcement-card {
  height: 100%;
}

.announcements {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  display: flex;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.announcement-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.announcement-icon {
  flex-shrink: 0;
  padding-top: 4px;
}

.announcement-content {
  flex: 1;
}

.announcement-content h4 {
  margin: 0 0 8px;
  font-size: 16px;
}

.announcement-content p {
  margin: 0 0 8px;
  color: var(--el-text-color-regular);
}

.announcement-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.body-model-card {
  margin-bottom: 24px;
}

.body-model-wrapper {
  height: 500px;
}

.feature-card {
  cursor: pointer;
  transition: transform 0.3s ease;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 20px 0;
}

.feature-content p {
  margin: 0;
  text-align: center;
  color: var(--el-text-color-regular);
}

@media (max-width: 992px) {
  .user-profile-summary {
    flex-direction: column;
  }
  
  .user-info {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .stat-item {
    margin-bottom: 16px;
  }
  
  .body-model-wrapper {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .body-model-wrapper {
    height: 350px;
  }
}

.mt-4 {
  margin-top: 1rem;
}
</style> 