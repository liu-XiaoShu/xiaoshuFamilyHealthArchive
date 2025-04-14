<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <h2>欢迎回来！</h2>
          <p>这里是您的健康管理仪表盘</p>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="8">
        <el-card class="quick-actions">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <el-button type="primary" @click="goToMedicalRecords">查看病历</el-button>
          <el-button type="success" @click="goToMedicationRecords">查看用药记录</el-button>
          <el-button type="warning" @click="goToVaccinationRecords">查看疫苗接种记录</el-button>
          <el-button type="info" @click="goToPhysicalExams">查看体检记录</el-button>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card class="recent-activities">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-empty v-if="!activities.length" description="暂无活动记录" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="activity in activities"
              :key="activity.id"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'DashboardPage',
  setup() {
    const router = useRouter()
    const activities = ref([])
    
    const goToMedicalRecords = () => {
      router.push('/medical-records')
    }
    
    const goToMedicationRecords = () => {
      router.push('/medication-records')
    }
    
    const goToVaccinationRecords = () => {
      router.push('/vaccination-records')
    }
    
    const goToPhysicalExams = () => {
      router.push('/physical-exams')
    }
    
    return {
      activities,
      goToMedicalRecords,
      goToMedicationRecords,
      goToVaccinationRecords,
      goToPhysicalExams
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.welcome-card {
  text-align: center;
  padding: 20px;
}

.welcome-card h2 {
  margin-bottom: 10px;
  color: #409EFF;
}

.quick-actions {
  height: 100%;
}

.quick-actions .el-button {
  margin: 5px;
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-activities {
  height: 100%;
}
</style> 