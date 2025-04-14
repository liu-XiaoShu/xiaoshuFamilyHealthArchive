<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h1>{{ greeting }}，{{ userData.username || '用户' }}</h1>
      <p>今天是 {{ currentDate }}，祝您健康愉快！</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="content-area">
      <!-- 左侧: 健康统计和快捷操作 -->
      <div class="left-panel">
        <el-card class="health-stats-card">
          <template #header>
            <div class="card-header">
              <h3>健康统计</h3>
              <el-button type="text" @click="refreshStats">刷新</el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <div v-else class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon health-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ healthStats.height || '--' }} cm</div>
                <div class="stat-label">身高</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon weight-icon">
                <el-icon><ScaleToOriginal /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ healthStats.weight || '--' }} kg</div>
                <div class="stat-label">体重</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon blood-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ healthStats.bloodPressure || '--' }}</div>
                <div class="stat-label">血压</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon heart-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ healthStats.heartRate || '--' }} bpm</div>
                <div class="stat-label">心率</div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <h3>快捷操作</h3>
            </div>
          </template>
          <div class="actions-grid">
            <el-button class="action-btn" @click="navigateTo('/records/create')">
              <el-icon><DocumentAdd /></el-icon>
              记录就诊
            </el-button>
            <el-button class="action-btn" @click="navigateTo('/records/medication')">
              <el-icon><Calendar /></el-icon>
              用药提醒
            </el-button>
            <el-button class="action-btn" @click="navigateTo('/records/physical')">
              <el-icon><DataAnalysis /></el-icon>
              体检报告
            </el-button>
            <el-button class="action-btn" @click="navigateTo('/family')">
              <el-icon><UserFilled /></el-icon>
              家庭成员
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 中间: 健康统计信息展示（替换原来的3D人体模型） -->
      <div class="center-panel">
        <el-card class="health-stats-card">
          <template #header>
            <div class="card-header">
              <h3>健康统计</h3>
              <el-button type="text" @click="refreshStats">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-icon class="loading-icon"><Loading /></el-icon>
            <span>正在加载健康数据...</span>
          </div>
          <div v-else class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon health-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ healthStats.height || '--' }} cm</span>
                <span class="stat-label">身高</span>
              </div>
            </div>
            
            <div class="stat-item">
              <div class="stat-icon weight-icon">
                <el-icon><ScaleToOriginal /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ healthStats.weight || '--' }} kg</span>
                <span class="stat-label">体重</span>
              </div>
            </div>
            
            <div class="stat-item">
              <div class="stat-icon blood-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ healthStats.bloodPressure || '--' }}</span>
                <span class="stat-label">血压</span>
              </div>
            </div>
            
            <div class="stat-item">
              <div class="stat-icon heart-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ healthStats.heartRate || '--' }} bpm</span>
                <span class="stat-label">心率</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧: 即将到来的事件和健康趋势 -->
      <div class="right-panel">
        <el-card class="upcoming-events-card">
          <template #header>
            <div class="card-header">
              <h3>即将到来的事件</h3>
              <el-button type="text" @click="navigateTo('/events')">查看全部</el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <div v-else-if="upcomingEvents.length > 0" class="events-list">
            <div v-for="event in upcomingEvents" :key="event.id" class="event-item">
              <div class="event-date">
                <div class="event-day">{{ formatDay(event.date) }}</div>
                <div class="event-month">{{ formatMonth(event.date) }}</div>
              </div>
              <div class="event-details">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-description">{{ event.description }}</div>
              </div>
              <el-icon class="event-icon"><ArrowRight /></el-icon>
            </div>
          </div>
          <el-empty v-else description="暂无即将到来的事件" />
        </el-card>

        <el-card class="health-trend-card">
          <template #header>
            <div class="card-header">
              <h3>健康趋势</h3>
              <el-button type="text" @click="navigateTo('/stats')">详细分析</el-button>
            </div>
          </template>
          <div ref="healthTrendChart" class="health-trend-chart"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useUserStore } from '@/stores/user'
import { 
  User, 
  ScaleToOriginal, 
  CircleCheck, 
  Monitor, 
  DocumentAdd, 
  Calendar, 
  DataAnalysis, 
  UserFilled, 
  Refresh, 
  Loading,
  ArrowRight
} from '@element-plus/icons-vue'

// 注册必要的echarts组件
echarts.use([
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  CanvasRenderer
])

const router = useRouter()
const userStore = useUserStore()
const healthTrendChart = ref(null)
const loading = ref(true)

// 用户数据
const userData = reactive({
  username: '',
  email: '',
  phone: ''
})

// 健康统计数据
const healthStats = reactive({
  height: null,
  weight: null,
  bloodPressure: null,
  heartRate: null
})

// 即将到来的事件
const upcomingEvents = ref([])

// 获取用户欢迎语
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  return '晚上好'
})

// 当前日期
const currentDate = computed(() => {
  return format(new Date(), 'yyyy年MM月dd日 EEEE', { locale: zhCN })
})

// 导航方法
const navigateTo = (path) => {
  router.push(path)
}

// 刷新健康统计数据
const refreshStats = () => {
  loading.value = true
  fetchHealthStats()
}

// 格式化日期显示
const formatDay = (dateStr) => {
  return format(new Date(dateStr), 'dd')
}

const formatMonth = (dateStr) => {
  return format(new Date(dateStr), 'MM月')
}

// 初始化健康趋势图表
const initHealthTrendChart = () => {
  if (!healthTrendChart.value) return

  const chart = echarts.init(healthTrendChart.value)
  
  // 模拟数据
  const dates = [];
  const weights = [];
  const bloodPressures = [];
  
  // 生成最近7天的数据
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(format(date, 'MM-dd'));
    
    // 模拟体重数据，基准57kg加上随机波动
    weights.push((57 + Math.random() * 0.6 - 0.3).toFixed(1));
    
    // 模拟血压数据，收缩压/舒张压
    const systolic = Math.floor(120 + Math.random() * 10 - 5);
    const diastolic = Math.floor(80 + Math.random() * 8 - 4);
    bloodPressures.push(`${systolic}/${diastolic}`);
  }
  
  const option = {
    title: {
      text: '近期健康指标变化',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const date = params[0].axisValue;
        let result = `${date}<br/>`;
        params.forEach(param => {
          if (param.seriesName === '体重') {
            result += `${param.seriesName}: ${param.value} kg<br/>`;
          } else if (param.seriesName === '血压') {
            result += `${param.seriesName}: ${bloodPressures[param.dataIndex]}<br/>`;
          }
        });
        return result;
      }
    },
    legend: {
      data: ['体重', '血压'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value} kg'
      }
    },
    series: [
      {
        name: '体重',
        type: 'line',
        data: weights,
        symbolSize: 6,
        itemStyle: {
          color: '#409EFF'
        },
        lineStyle: {
          width: 2
        }
      },
      {
        name: '血压',
        type: 'line',
        data: weights.map(() => null), // 只是为了在图例中显示
        symbolSize: 0,
        lineStyle: {
          width: 0
        }
      }
    ]
  };
  
  chart.setOption(option);
  
  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    chart.resize();
  });
}

// 获取用户信息
const fetchUserData = async () => {
  try {
    // 先尝试从用户store获取
    if (userStore.user) {
      userData.username = userStore.user.username || '用户'
      userData.email = userStore.user.email || ''
      userData.phone = userStore.user.phone || ''
      return
    }
    
    // 如果store中没有，从API获取
    const response = await fetch('/api/users/me/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      userData.username = data.username
      userData.email = data.email
      userData.phone = data.phone
      
      // 更新store
      userStore.setUser(data)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    
    // 使用模拟数据
    userData.username = '测试用户'
    userData.email = 'test@example.com'
    userData.phone = '13800138000'
  }
}

// 获取健康统计数据
const fetchHealthStats = async () => {
  try {
    const response = await fetch('/api/records/overview/summary/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      healthStats.height = data.height
      healthStats.weight = data.weight
      healthStats.bloodPressure = data.blood_pressure
      healthStats.heartRate = data.heart_rate
    }
  } catch (error) {
    console.error('获取健康统计数据失败:', error)
    
    // 使用模拟数据
    healthStats.height = 173
    healthStats.weight = 67.5
    healthStats.bloodPressure = '120/80'
    healthStats.heartRate = 72
  } finally {
    loading.value = false
  }
}

// 获取即将到来的事件
const fetchUpcomingEvents = async () => {
  try {
    const response = await fetch('/api/events/upcoming/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      upcomingEvents.value = data
    }
  } catch (error) {
    console.error('获取即将到来的事件失败:', error)
    
    // 使用模拟数据
    upcomingEvents.value = [
      {
        id: 1,
        title: '体检预约',
        description: '年度体检 - 城市中心医院',
        date: '2025-04-15'
      },
      {
        id: 2,
        title: '医生复诊',
        description: '心内科随访 - 李医生',
        date: '2025-04-18'
      },
      {
        id: 3,
        title: '疫苗接种',
        description: '季节性流感疫苗',
        date: '2025-04-25'
      }
    ]
  } finally {
    loading.value = false
  }
}

// 生命周期钩子
onMounted(async () => {
  // 获取必要数据
  loading.value = true
  await fetchUserData()
  await fetchHealthStats()
  await fetchUpcomingEvents()
  
  // 初始化图表
  nextTick(() => {
    initHealthTrendChart()
  })
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  height: 100%;
}

.welcome-section {
  margin-bottom: 20px;
}

.welcome-section h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.welcome-section p {
  margin: 5px 0 0;
  color: #606266;
}

.content-area {
  display: flex;
  gap: 20px;
  height: calc(100% - 70px);
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 25%;
  max-width: 350px;
}

.center-panel {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #909399;
}

/* 健康统计卡片 */
.health-stats-card {
  flex: 0 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  background-color: #f5f7fa;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  margin-right: 10px;
}

.health-icon {
  background-color: #ecf5ff;
  color: #409eff;
}

.weight-icon {
  background-color: #f0f9eb;
  color: #67c23a;
}

.blood-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.heart-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

/* 快捷操作卡片 */
.quick-actions-card {
  flex: 0 0 auto;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 80px;
  background-color: #f5f7fa;
}

.action-btn :deep(.el-icon) {
  font-size: 24px;
  margin-bottom: 8px;
}

/* 即将到来的事件卡片 */
.upcoming-events-card {
  flex: 0 0 auto;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: background-color 0.3s;
}

.event-item:hover {
  background-color: #ecf5ff;
}

.event-date {
  width: 50px;
  height: 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #409eff;
  color: white;
  border-radius: 6px;
  margin-right: 15px;
}

.event-day {
  font-size: 18px;
  font-weight: 600;
}

.event-month {
  font-size: 12px;
}

.event-details {
  flex: 1;
  min-width: 0;
}

.event-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-description {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-icon {
  color: #909399;
  margin-left: 10px;
}

/* 健康趋势卡片 */
.health-trend-card {
  flex: 1;
  min-height: 0;
}

.health-trend-card :deep(.el-card__body) {
  height: calc(100% - 60px);
}

.health-trend-chart {
  height: 100%;
  width: 100%;
}

/* 响应式布局 */
@media screen and (max-width: 1200px) {
  .content-area {
    flex-direction: column;
  }
  
  .left-panel, .center-panel, .right-panel {
    width: 100%;
    max-width: none;
  }
  
  .center-panel {
    order: -1;
  }
  
  .body-model-card, .health-trend-card {
    height: 400px;
  }
}

@media screen and (max-width: 768px) {
  .stats-grid, .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style> 