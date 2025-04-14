<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h1>个人资料</h1>
        </div>
      </template>

      <div class="profile-content">
        <div class="avatar-section">
          <el-avatar :src="userInfo?.avatar || ''" :size="120" :icon="User" />
          <el-upload
            class="avatar-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleAvatarChange"
          >
            <el-button type="primary" size="small">更换头像</el-button>
          </el-upload>
        </div>
        
        <el-divider />

        <el-form 
          :model="form" 
          :rules="rules" 
          ref="formRef" 
          label-width="100px" 
          label-position="left"
          class="profile-form"
        >
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" />
          </el-form-item>
          
          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="form.nickname" />
          </el-form-item>
          
          <el-form-item label="电子邮箱" prop="email">
            <el-input v-model="form.email" />
          </el-form-item>
          
          <el-form-item label="手机号码" prop="phone">
            <el-input v-model="form.phone" />
          </el-form-item>
          
          <el-divider content-position="left">个人信息</el-divider>
          
          <el-form-item label="出生日期" prop="birthdate">
            <el-date-picker 
              v-model="form.birthdate" 
              type="date" 
              placeholder="选择出生日期"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="form.gender">
              <el-radio label="male">男</el-radio>
              <el-radio label="female">女</el-radio>
              <el-radio label="other">其他</el-radio>
              <el-radio label="prefer_not_to_say">不愿透露</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="身高(cm)" prop="height">
            <el-input-number v-model="form.height" :min="0" :max="300" :precision="1" style="width: 180px" />
          </el-form-item>
          
          <el-form-item label="体重(kg)" prop="weight">
            <el-input-number v-model="form.weight" :min="0" :max="300" :precision="1" style="width: 180px" />
          </el-form-item>
          
          <el-form-item label="血型" prop="bloodType">
            <el-select v-model="form.bloodType" placeholder="选择血型" style="width: 180px">
              <el-option label="A型" value="A" />
              <el-option label="B型" value="B" />
              <el-option label="AB型" value="AB" />
              <el-option label="O型" value="O" />
              <el-option label="不确定" value="unknown" />
            </el-select>
          </el-form-item>
          
          <el-divider content-position="left">紧急联系人</el-divider>
          
          <el-form-item label="姓名" prop="emergencyContact.name">
            <el-input v-model="form.emergencyContact.name" />
          </el-form-item>
          
          <el-form-item label="关系" prop="emergencyContact.relationship">
            <el-input v-model="form.emergencyContact.relationship" />
          </el-form-item>
          
          <el-form-item label="电话" prop="emergencyContact.phone">
            <el-input v-model="form.emergencyContact.phone" />
          </el-form-item>
          
          <el-divider content-position="left">过敏信息</el-divider>
          
          <el-form-item label="过敏情况">
            <div v-for="(allergy, index) in form.allergies" :key="index" class="allergy-item">
              <el-input 
                v-model="form.allergies[index]" 
                placeholder="输入过敏物质或药物"
                class="allergy-input"
              />
              <el-button 
                type="danger" 
                circle 
                size="small" 
                @click="removeAllergy(index)"
                :disabled="form.allergies.length <= 1"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addAllergy" class="add-btn">
              添加过敏信息
            </el-button>
          </el-form-item>
          
          <el-form-item label="备注" prop="notes">
            <el-input 
              v-model="form.notes" 
              type="textarea" 
              :rows="4" 
              placeholder="添加其他健康相关备注信息"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="saveProfile">保存资料</el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Delete } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import type { FormInstance, UploadFile } from 'element-plus'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const userInfo = ref<any>(authStore.user || {})

// 表单数据
const form = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  birthdate: null as Date | null,
  gender: 'prefer_not_to_say',
  height: 0,
  weight: 0,
  bloodType: '',
  emergencyContact: {
    name: '',
    relationship: '',
    phone: ''
  },
  allergies: [''],
  notes: '',
  avatar: null as File | null
})

// 验证规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的电子邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  'emergencyContact.phone': [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 处理头像上传
const handleAvatarChange = (file: UploadFile) => {
  form.avatar = file.raw as File
  ElMessage.success('头像已选择，点击保存按钮完成更新')
}

// 添加过敏信息
const addAllergy = () => {
  form.allergies.push('')
}

// 移除过敏信息
const removeAllergy = (index: number) => {
  if (form.allergies.length > 1) {
    form.allergies.splice(index, 1)
  }
}

// 保存个人资料
const saveProfile = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请完成必填项')
      return
    }
    
    try {
      // 提交前确认必要字段存在
      if (!form.username) {
        ElMessage.warning('用户名不能为空')
        return
      }
      
      console.log('提交表单数据:', form)
      
      // 准备用户资料数据
      const profileData = {
        nickname: form.nickname,
        phone: form.phone,
        birth_date: form.birthdate ? new Date(form.birthdate).toISOString().split('T')[0] : undefined,
        gender: form.gender
        // API需要字符串格式，不能使用对象格式的emergency_contact
      }
      
      // 还可以传递紧急联系人信息字符串
      if (form.emergencyContact.name && form.emergencyContact.relationship && form.emergencyContact.phone) {
        // @ts-ignore - 忽略类型检查，因为API接受字符串
        profileData.emergency_contact = `${form.emergencyContact.name}-${form.emergencyContact.relationship}-${form.emergencyContact.phone}`
      }
      
      // 调用API保存用户资料
      await userApi.updateProfile(profileData)
      
      // 更新健康信息
      await userApi.updateHealthInfo({
        height: form.height,
        weight: form.weight,
        blood_type: form.bloodType,
        allergies: form.allergies.filter(a => a.trim() !== '')
      })
      
      // 如果有头像更新，上传头像
      if (form.avatar instanceof File) {
        console.log('准备上传头像文件:', form.avatar)
        try {
          await userApi.updateAvatar(form.avatar)
          console.log('头像上传成功')
        } catch (avatarError) {
          console.error('头像上传失败:', avatarError)
          ElMessage.warning('个人资料已保存，但头像上传失败')
          return // 提前返回，避免显示完全成功信息
        }
      }
      
      ElMessage.success('个人资料更新成功')
      
      // 刷新用户信息
      authStore.loadUser()
    } catch (error) {
      console.error('保存个人资料失败:', error)
      ElMessage.error('保存个人资料失败，请重试')
    }
  })
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
}

// 初始化表单数据
const initFormData = async () => {
  try {
    // 加载用户基本信息
    const profile = await userApi.getProfile()
    if (profile) {
      form.username = profile.username || ''
      form.nickname = profile.nickname || ''
      form.email = profile.email || ''
      form.phone = profile.phone || ''
      form.birthdate = profile.birth_date ? new Date(profile.birth_date) : null
      form.gender = profile.gender || 'prefer_not_to_say'
      
      // 解析紧急联系人信息 (格式: 姓名-关系-电话)
      if (profile.emergency_contact) {
        const parts = profile.emergency_contact.split('-')
        if (parts.length === 3) {
          form.emergencyContact.name = parts[0]
          form.emergencyContact.relationship = parts[1]
          form.emergencyContact.phone = parts[2]
        }
      }
    }
    
    // 加载健康信息
    const healthInfo = await userApi.getHealthInfo()
    if (healthInfo) {
      form.height = healthInfo.height || 0
      form.weight = healthInfo.weight || 0
      form.bloodType = healthInfo.blood_type || ''
      form.allergies = healthInfo.allergies?.length ? healthInfo.allergies : ['']
      form.notes = healthInfo.notes || ''
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
    ElMessage.error('加载用户信息失败')
  }
}

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.profile-page {
  padding: 24px;
}

.profile-card {
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

.profile-content {
  padding: 16px 0;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.profile-form {
  margin-top: 24px;
}

.allergy-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.allergy-input {
  flex: 1;
}

.add-btn {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 16px;
  }
  
  .profile-form :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    margin-bottom: 8px;
  }
  
  .profile-form :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}
</style> 