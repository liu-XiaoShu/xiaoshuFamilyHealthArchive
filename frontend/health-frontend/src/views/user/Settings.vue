<template>
  <div class="settings-page">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <h1>账号设置</h1>
        </div>
      </template>

      <div class="settings-content">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="安全设置" name="security">
            <div class="tab-content">
              <h2>修改密码</h2>
              <el-form 
                :model="passwordForm" 
                :rules="passwordRules" 
                ref="passwordFormRef" 
                label-width="120px"
                class="settings-form"
              >
                <el-form-item label="当前密码" prop="currentPassword">
                  <el-input 
                    v-model="passwordForm.currentPassword" 
                    type="password" 
                    show-password
                    placeholder="输入当前密码"
                  />
                </el-form-item>
                
                <el-form-item label="新密码" prop="newPassword">
                  <el-input 
                    v-model="passwordForm.newPassword" 
                    type="password" 
                    show-password
                    placeholder="输入新密码"
                  />
                </el-form-item>
                
                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input 
                    v-model="passwordForm.confirmPassword" 
                    type="password" 
                    show-password
                    placeholder="再次输入新密码"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updatePassword">更新密码</el-button>
                  <el-button @click="resetPasswordForm">重置</el-button>
                </el-form-item>
              </el-form>
              
              <el-divider />
              
              <h2>绑定手机号</h2>
              <el-form 
                :model="phoneForm" 
                :rules="phoneRules" 
                ref="phoneFormRef" 
                label-width="120px"
                class="settings-form"
              >
                <el-form-item label="手机号码" prop="phone">
                  <el-input 
                    v-model="phoneForm.phone" 
                    placeholder="输入手机号码"
                  />
                </el-form-item>
                
                <el-form-item label="验证码" prop="code">
                  <div class="code-input-wrapper">
                    <el-input 
                      v-model="phoneForm.code" 
                      placeholder="输入验证码"
                    />
                    <el-button 
                      type="primary" 
                      :disabled="isCountingDown" 
                      @click="sendVerificationCode"
                    >
                      {{ isCountingDown ? `${countDown}秒后重试` : '获取验证码' }}
                    </el-button>
                  </div>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updatePhone">绑定手机</el-button>
                  <el-button @click="resetPhoneForm">重置</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="通知设置" name="notifications">
            <div class="tab-content">
              <h2>消息通知</h2>
              <el-form 
                :model="notificationSettings" 
                label-width="120px"
                class="settings-form"
              >
                <el-form-item label="系统通知">
                  <el-switch v-model="notificationSettings.systemNotifications" />
                </el-form-item>
                
                <el-form-item label="健康提醒">
                  <el-switch v-model="notificationSettings.healthReminders" />
                </el-form-item>
                
                <el-form-item label="用药提醒">
                  <el-switch v-model="notificationSettings.medicationReminders" />
                </el-form-item>
                
                <el-form-item label="体检提醒">
                  <el-switch v-model="notificationSettings.examReminders" />
                </el-form-item>
                
                <el-form-item label="提醒方式">
                  <el-checkbox-group v-model="notificationSettings.notificationMethods">
                    <el-checkbox label="app">应用内通知</el-checkbox>
                    <el-checkbox label="email">邮件</el-checkbox>
                    <el-checkbox label="sms">短信</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updateNotificationSettings">保存设置</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="隐私设置" name="privacy">
            <div class="tab-content">
              <h2>数据共享</h2>
              <el-form 
                :model="privacySettings" 
                label-width="200px"
                class="settings-form"
              >
                <el-form-item label="允许与医生共享健康数据">
                  <el-switch v-model="privacySettings.shareWithDoctors" />
                </el-form-item>
                
                <el-form-item label="允许用于匿名健康研究">
                  <el-switch v-model="privacySettings.anonymousResearch" />
                </el-form-item>
                
                <el-form-item label="允许健康数据分析">
                  <el-switch v-model="privacySettings.dataAnalysis" />
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="updatePrivacySettings">保存设置</el-button>
                </el-form-item>
              </el-form>
              
              <el-divider />
              
              <h2>危险操作</h2>
              <div class="danger-zone">
                <div class="danger-item">
                  <div class="danger-info">
                    <h3>注销账号</h3>
                    <p>永久删除您的账号和所有相关数据，此操作不可逆</p>
                  </div>
                  <el-button type="danger" @click="showDeleteAccountDialog">注销账号</el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
    
    <!-- 删除账号确认对话框 -->
    <el-dialog v-model="deleteAccountDialogVisible" title="注销账号" width="30%">
      <p>您确定要永久删除您的账号吗？此操作不可逆，所有数据将被永久删除。</p>
      <div class="confirm-delete">
        <el-input 
          v-model="deleteConfirmation" 
          placeholder="请输入您的密码确认"
          type="password"
          show-password
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteAccountDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="deleteAccount" :disabled="!deleteConfirmation">
            确认注销
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { FormInstance } from 'element-plus'

const authStore = useAuthStore()
const activeTab = ref('security')

// 修改密码表单
const passwordFormRef = ref<FormInstance>()
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 绑定手机表单
const phoneFormRef = ref<FormInstance>()
const phoneForm = reactive({
  phone: '',
  code: ''
})

const phoneRules = {
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

// 验证码倒计时
const isCountingDown = ref(false)
const countDown = ref(60)
let timer: number | null = null

// 通知设置
const notificationSettings = reactive({
  systemNotifications: true,
  healthReminders: true,
  medicationReminders: true,
  examReminders: true,
  notificationMethods: ['app', 'email']
})

// 隐私设置
const privacySettings = reactive({
  shareWithDoctors: true,
  anonymousResearch: false,
  dataAnalysis: true
})

// 删除账号相关
const deleteAccountDialogVisible = ref(false)
const deleteConfirmation = ref('')

// 更新密码
const updatePassword = () => {
  passwordFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        // 调用API更新密码
        // await authApi.updatePassword(passwordForm)
        
        ElMessage.success('密码更新成功')
        resetPasswordForm()
      } catch (error) {
        console.error('更新密码失败:', error)
        ElMessage.error('更新密码失败，请重试')
      }
    }
  })
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordFormRef.value?.resetFields()
}

// 发送验证码
const sendVerificationCode = async () => {
  try {
    await phoneFormRef.value?.validateField('phone')
    
    // 调用API发送验证码
    // await authApi.sendVerificationCode(phoneForm.phone)
    
    ElMessage.success(`验证码已发送至手机号: ${phoneForm.phone}`)
    startCountDown()
  } catch (error) {
    console.error('发送验证码失败:', error)
    ElMessage.error('发送验证码失败，请重试')
  }
}

// 开始倒计时
const startCountDown = () => {
  isCountingDown.value = true
  countDown.value = 60
  
  timer = window.setInterval(() => {
    countDown.value--
    if (countDown.value <= 0) {
      clearInterval(timer as number)
      isCountingDown.value = false
    }
  }, 1000)
}

// 更新手机号
const updatePhone = () => {
  phoneFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        // 调用API绑定手机号
        // await authApi.updatePhone(phoneForm)
        
        ElMessage.success('手机号绑定成功')
        resetPhoneForm()
      } catch (error) {
        console.error('绑定手机号失败:', error)
        ElMessage.error('绑定手机号失败，请重试')
      }
    }
  })
}

// 重置手机表单
const resetPhoneForm = () => {
  phoneFormRef.value?.resetFields()
}

// 更新通知设置
const updateNotificationSettings = async () => {
  try {
    // 调用API更新通知设置
    // await userApi.updateNotificationSettings(notificationSettings)
    
    ElMessage.success('通知设置已更新')
  } catch (error) {
    console.error('更新通知设置失败:', error)
    ElMessage.error('更新通知设置失败，请重试')
  }
}

// 更新隐私设置
const updatePrivacySettings = async () => {
  try {
    // 调用API更新隐私设置
    // await userApi.updatePrivacySettings(privacySettings)
    
    ElMessage.success('隐私设置已更新')
  } catch (error) {
    console.error('更新隐私设置失败:', error)
    ElMessage.error('更新隐私设置失败，请重试')
  }
}

// 显示删除账号对话框
const showDeleteAccountDialog = () => {
  deleteAccountDialogVisible.value = true
  deleteConfirmation.value = ''
}

// 删除账号
const deleteAccount = async () => {
  try {
    // 二次确认
    await ElMessageBox.confirm(
      '此操作将永久删除您的账号和所有数据，不可恢复。确认继续吗？',
      '警告',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用API删除账号
    // await authApi.deleteAccount(deleteConfirmation.value)
    
    ElMessage.success('账号已注销')
    deleteAccountDialogVisible.value = false
    
    // 登出
    await authStore.logout()
    
    // 跳转到登录页面
    window.location.href = '/login'
  } catch (error) {
    if (error !== 'cancel') {
      console.error('注销账号失败:', error)
      ElMessage.error('注销账号失败，请重试')
    }
  }
}

// 加载初始设置
const loadSettings = async () => {
  try {
    // 加载用户设置
    // const settings = await userApi.getSettings()
    // notificationSettings.value = settings.notifications
    // privacySettings.value = settings.privacy
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 24px;
}

.settings-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h1 {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.settings-content {
  padding: 16px 0;
}

.tab-content {
  padding: 20px 0;
}

.tab-content h2 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 18px;
  color: var(--el-text-color-primary);
}

.settings-form {
  max-width: 600px;
}

.code-input-wrapper {
  display: flex;
  gap: 12px;
}

.danger-zone {
  border: 1px solid var(--el-color-danger);
  border-radius: 4px;
  padding: 16px;
  margin-top: 16px;
}

.danger-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.danger-info h3 {
  margin: 0 0 8px;
  color: var(--el-color-danger);
}

.danger-info p {
  margin: 0;
  color: var(--el-text-color-secondary);
}

.confirm-delete {
  margin: 16px 0;
}

@media (max-width: 768px) {
  .settings-page {
    padding: 16px;
  }
  
  .danger-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .danger-item .el-button {
    margin-left: 0;
  }
  
  .code-input-wrapper {
    flex-direction: column;
  }
}
</style> 