<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8" :md="6">
        <el-card class="profile-card">
          <div class="avatar-container">
            <el-avatar
              :size="120"
              :src="userInfo.avatar || '/default-avatar.png'"
              @click="handleAvatarClick"
            />
            <el-upload
              ref="uploadRef"
              class="avatar-uploader"
              action="/api/user/avatar/"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              v-show="false"
            >
              <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" />
            </el-upload>
          </div>
          <h3 class="username">{{ userInfo.username }}</h3>
          <p class="user-role">{{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}</p>
          <p class="join-date">加入时间：{{ formatDate(userInfo.joinDate) }}</p>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="16" :md="18">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <el-button type="primary" @click="startEdit" v-if="!isEditing">
                编辑资料
              </el-button>
              <div v-else>
                <el-button type="success" @click="saveUserInfo" :loading="saving">
                  保存
                </el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </div>
            </div>
          </template>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="100px"
            :disabled="!isEditing"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" />
            </el-form-item>
            <el-form-item label="真实姓名" prop="realName">
              <el-input v-model="form.realName" />
            </el-form-item>
            <el-form-item label="性别" prop="gender">
              <el-select v-model="form.gender" placeholder="请选择性别">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="出生日期" prop="birthDate">
              <el-date-picker
                v-model="form.birthDate"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="地址" prop="address">
              <el-input v-model="form.address" type="textarea" :rows="2" />
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="health-info-card">
          <template #header>
            <div class="card-header">
              <span>健康信息</span>
            </div>
          </template>

          <el-form
            :model="healthForm"
            label-width="100px"
            :disabled="!isEditing"
          >
            <el-form-item label="身高(cm)">
              <el-input-number v-model="healthForm.height" :min="0" :max="300" />
            </el-form-item>
            <el-form-item label="体重(kg)">
              <el-input-number v-model="healthForm.weight" :min="0" :max="500" />
            </el-form-item>
            <el-form-item label="血型">
              <el-select v-model="healthForm.bloodType">
                <el-option label="A" value="A" />
                <el-option label="B" value="B" />
                <el-option label="O" value="O" />
                <el-option label="AB" value="AB" />
              </el-select>
            </el-form-item>
            <el-form-item label="过敏史">
              <el-input
                v-model="healthForm.allergies"
                type="textarea"
                :rows="2"
                placeholder="请输入过敏史（如有）"
              />
            </el-form-item>
            <el-form-item label="慢性病史">
              <el-input
                v-model="healthForm.chronicDiseases"
                type="textarea"
                :rows="2"
                placeholder="请输入慢性病史（如有）"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, UploadProps } from 'element-plus'

const formRef = ref<FormInstance>()
const uploadRef = ref()
const fileInput = ref()
const isEditing = ref(false)
const saving = ref(false)

// 用户信息
const userInfo = reactive({
  username: '',
  avatar: '',
  role: '',
  joinDate: '',
})

// 表单数据
const form = reactive({
  username: '',
  realName: '',
  gender: '',
  birthDate: '',
  phone: '',
  email: '',
  address: '',
})

// 健康信息
const healthForm = reactive({
  height: 170,
  weight: 60,
  bloodType: '',
  allergies: '',
  chronicDiseases: '',
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

// 获取用户信息
const getUserInfo = async () => {
  try {
    const response = await fetch('/api/user/profile/')
    const data = await response.json()
    Object.assign(userInfo, data)
    Object.assign(form, data)
    Object.assign(healthForm, data.healthInfo || {})
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  getUserInfo() // 重新获取用户信息
}

// 保存用户信息
const saveUserInfo = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      try {
        const response = await fetch('/api/user/profile/', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...form,
            healthInfo: healthForm
          })
        })
        
        if (response.ok) {
          ElMessage.success('保存成功')
          isEditing.value = false
          getUserInfo()
        } else {
          throw new Error('保存失败')
        }
      } catch (error) {
        ElMessage.error('保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

// 头像上传相关方法
const handleAvatarClick = () => {
  fileInput.value.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const file = target.files[0]
    beforeAvatarUpload(file) && uploadRef.value.submit()
  }
}

const beforeAvatarUpload: UploadProps['beforeUpload'] = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('上传头像图片只能是图片格式!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleAvatarSuccess: UploadProps['onSuccess'] = (response) => {
  userInfo.avatar = response.url
  ElMessage.success('头像上传成功')
}

onMounted(() => {
  getUserInfo()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-container {
  margin: 20px 0;
  position: relative;
  cursor: pointer;
}

.avatar-container:hover::after {
  content: '点击更换头像';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.username {
  margin: 10px 0;
  font-size: 18px;
  font-weight: 500;
}

.user-role {
  color: #909399;
  margin: 5px 0;
}

.join-date {
  color: #909399;
  font-size: 12px;
}

.info-card,
.health-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

@media screen and (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .profile-card {
    margin-bottom: 15px;
  }

  :deep(.el-form-item__label) {
    float: none;
    display: block;
    text-align: left;
    margin-bottom: 8px;
  }
}
</style> 