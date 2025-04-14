<template>
  <div class="settings-container">
    <h2>系统设置</h2>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>主题设置</span>
        </div>
      </template>

      <el-form :model="themeSettings" label-width="120px">
        <el-form-item label="主题色">
          <el-color-picker v-model="themeSettings.primaryColor" @change="updateTheme" />
        </el-form-item>
        <el-form-item label="深色模式">
          <el-switch v-model="themeSettings.darkMode" @change="toggleDarkMode" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>通知设置</span>
        </div>
      </template>

      <el-form :model="notificationSettings" label-width="120px">
        <el-form-item label="体检提醒">
          <el-switch v-model="notificationSettings.physicalExam" />
        </el-form-item>
        <el-form-item label="用药提醒">
          <el-switch v-model="notificationSettings.medication" />
        </el-form-item>
        <el-form-item label="疫苗接种提醒">
          <el-switch v-model="notificationSettings.vaccination" />
        </el-form-item>
        <el-form-item label="提前提醒天数">
          <el-input-number
            v-model="notificationSettings.reminderDays"
            :min="1"
            :max="30"
            controls-position="right"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>隐私设置</span>
        </div>
      </template>

      <el-form :model="privacySettings" label-width="120px">
        <el-form-item label="数据加密">
          <el-switch v-model="privacySettings.encryption" />
        </el-form-item>
        <el-form-item label="自动备份">
          <el-switch v-model="privacySettings.autoBackup" />
        </el-form-item>
        <el-form-item label="备份频率" v-if="privacySettings.autoBackup">
          <el-select v-model="privacySettings.backupFrequency">
            <el-option label="每天" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="settings-actions">
      <el-button type="primary" @click="saveSettings" :loading="saving">
        保存设置
      </el-button>
      <el-button @click="resetSettings">
        重置设置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const saving = ref(false)

const themeSettings = reactive({
  primaryColor: '#409EFF',
  darkMode: false
})

const notificationSettings = reactive({
  physicalExam: true,
  medication: true,
  vaccination: true,
  reminderDays: 7
})

const privacySettings = reactive({
  encryption: true,
  autoBackup: false,
  backupFrequency: 'weekly'
})

// 更新主题色
const updateTheme = (color: string) => {
  const style = document.documentElement.style
  style.setProperty('--el-color-primary', color)
  
  // 生成不同深度的主题色
  const mix = (color1: string, color2: string, weight: number) => {
    const d2h = (d: number) => d.toString(16).padStart(2, '0')
    const h2d = (h: string) => parseInt(h, 16)
    
    let color = '#'
    for (let i = 0; i < 3; i++) {
      const c1 = h2d(color1.substr(i * 2 + 1, 2))
      const c2 = h2d(color2.substr(i * 2 + 1, 2))
      const c = d2h(Math.round(c1 * (1 - weight) + c2 * weight))
      color += c
    }
    return color
  }

  for (let i = 1; i <= 9; i++) {
    const lightColor = mix(color, '#ffffff', i * 0.1)
    style.setProperty(`--el-color-primary-light-${i}`, lightColor)
  }
}

// 切换深色模式
const toggleDarkMode = (value: boolean) => {
  document.documentElement.classList.toggle('dark', value)
}

// 保存设置
const saveSettings = async () => {
  saving.value = true
  try {
    await fetch('/api/settings/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        theme: themeSettings,
        notification: notificationSettings,
        privacy: privacySettings
      })
    })
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('设置保存失败')
  } finally {
    saving.value = false
  }
}

// 重置设置
const resetSettings = () => {
  themeSettings.primaryColor = '#409EFF'
  themeSettings.darkMode = false
  notificationSettings.physicalExam = true
  notificationSettings.medication = true
  notificationSettings.vaccination = true
  notificationSettings.reminderDays = 7
  privacySettings.encryption = true
  privacySettings.autoBackup = false
  privacySettings.backupFrequency = 'weekly'
  
  updateTheme(themeSettings.primaryColor)
  toggleDarkMode(themeSettings.darkMode)
  ElMessage.success('设置已重置')
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.settings-container h2 {
  margin: 0 0 20px;
  font-size: 24px;
  font-weight: 500;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-actions {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-top: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input-number) {
  width: 120px;
}

@media screen and (max-width: 768px) {
  .settings-container {
    padding: 10px;
  }

  :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    margin-bottom: 8px;
  }

  :deep(.el-form) {
    max-width: 100%;
  }
}
</style> 