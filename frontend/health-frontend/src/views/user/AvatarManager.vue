<!-- 头像管理界面 -->
<template>
  <div class="avatar-manager">
    <h2>头像管理</h2>
    
    <div class="avatar-options">
      <div class="current-avatar">
        <h3>当前头像</h3>
        <img :src="currentAvatar || defaultAvatarUrl" alt="当前头像" class="avatar-preview" />
      </div>
      
      <div class="upload-avatar">
        <h3>上传新头像</h3>
        <el-upload
          class="avatar-uploader"
          :action="uploadUrl"
          :headers="headers"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload">
          <img v-if="imageUrl" :src="imageUrl" class="avatar-preview" />
          <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
        </el-upload>
      </div>
      
      <div class="default-avatars">
        <h3>选择默认头像</h3>
        <div class="default-avatar-grid" v-loading="loadingDefaultAvatars">
          <div 
            v-for="avatar in defaultAvatars" 
            :key="avatar.id" 
            class="default-avatar-item"
            @click="selectDefaultAvatar(avatar)">
            <img :src="avatar.avatar" alt="默认头像" class="avatar-preview" />
            <div class="avatar-info">
              <span>{{ getGenderText(avatar.gender) }}</span>
              <span>{{ getAgeGroupText(avatar.age_group) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="avatar-actions">
      <el-button type="primary" @click="saveAvatar">保存更改</el-button>
      <el-button @click="cancelChanges">取消</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus/es/components/upload/src/upload'
import { useAuthStore } from '@/stores/auth'
import { userApi } from '@/api/user'
import type { User } from '@/types/auth'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const userInfo = computed(() => authStore.user as User)
const currentAvatar = ref<string | null>(null)
const activeTab = ref('child')
const uploading = ref(false)
const avatarFile = ref<File | null>(null)

// 默认头像URL
const maleChildAvatar = ref('')
const femaleChildAvatar = ref('')
const maleAdultAvatar = ref('')
const femaleAdultAvatar = ref('')
const maleElderAvatar = ref('')
const femaleElderAvatar = ref('')

// 计算年龄
const userAge = computed(() => {
  const birthDate = userInfo.value?.birth_date
  if (!birthDate) return '未知'
  
  try {
    const birthDateObj = new Date(birthDate)
    const today = new Date()
    let age = today.getFullYear() - birthDateObj.getFullYear()
    const m = today.getMonth() - birthDateObj.getMonth()
    
    if (m < 0 || (m === 0 && today.getDate() < birthDateObj.getDate())) {
      age--
    }
    
    return age
  } catch (e) {
    return '未知'
  }
})

// 获取当前用户头像
const loadCurrentAvatar = async () => {
  try {
    const response = await userApi.getAvatar()
    if (response.avatar_url) {
      currentAvatar.value = response.avatar_url
    }
  } catch (error) {
    console.error('获取头像失败:', error)
  }
}

// 获取所有默认头像
const loadDefaultAvatars = async () => {
  try {
    const loadAvatar = async (category: string) => {
      try {
        const response = await userApi.getDefaultAvatar(category)
        return response.image_url
      } catch (error) {
        console.error(`获取${category}头像失败:`, error)
        return ''
      }
    }
    
    maleChildAvatar.value = await loadAvatar('male_child')
    femaleChildAvatar.value = await loadAvatar('female_child')
    maleAdultAvatar.value = await loadAvatar('male_adult')
    femaleAdultAvatar.value = await loadAvatar('female_adult')
    maleElderAvatar.value = await loadAvatar('male_elder')
    femaleElderAvatar.value = await loadAvatar('female_elder')
  } catch (error) {
    console.error('获取默认头像失败:', error)
  }
}

// 处理头像更改
const handleAvatarChange = (file: UploadFile) => {
  avatarFile.value = file.raw as File
  
  // 预览选中的图片
  const reader = new FileReader()
  reader.onload = (e) => {
    currentAvatar.value = e.target?.result as string
  }
  reader.readAsDataURL(avatarFile.value)
}

// 选择默认头像
const selectDefaultAvatar = async (category: string) => {
  try {
    const response = await userApi.getDefaultAvatar(category)
    if (response.image_url) {
      currentAvatar.value = response.image_url
      avatarFile.value = null // 清除上传的文件
    }
  } catch (error) {
    console.error('选择默认头像失败:', error)
  }
}

// 保存头像
const saveAvatar = async () => {
  if (!avatarFile.value) {
    ElMessage.info('请先选择或上传头像')
    return
  }
  
  uploading.value = true
  try {
    console.log('开始上传头像文件:', avatarFile.value)
    const response = await userApi.updateAvatar(avatarFile.value)
    console.log('头像上传响应:', response)
    
    if (response.avatar_url) {
      currentAvatar.value = response.avatar_url
      ElMessage.success('头像更新成功')
      
      // 更新store中的用户信息，避免刷新页面
      if (authStore.user) {
        // 强制刷新用户数据
        await authStore.loadUser()
        console.log('已刷新用户信息')
      }
    } else {
      ElMessage.warning('头像已上传，但未获取到URL')
    }
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('头像更新失败: ' + (error instanceof Error ? error.message : String(error)))
  } finally {
    uploading.value = false
  }
}

// 取消更改
const cancelChanges = async () => {
  await loadCurrentAvatar()
  avatarFile.value = null
  ElMessage.info('已取消更改')
}

// 页面加载时获取头像数据
onMounted(async () => {
  await loadCurrentAvatar()
  await loadDefaultAvatars()
})

const imageUrl = ref('')
const selectedDefaultAvatar = ref(null)
const defaultAvatars = ref([])
const loadingDefaultAvatars = ref(false)
const defaultAvatarUrl = ref('')

const uploadUrl = `${import.meta.env.VITE_API_BASE_URL}/api/users/avatar/`
const headers = {
  Authorization: `Bearer ${getToken()}`
}

const fetchUserProfile = async () => {
  try {
    const profile = await getUserProfile()
    currentAvatar.value = profile.avatar
  } catch (error) {
    ElMessage.error('获取用户资料失败')
    console.error(error)
  }
}

const fetchDefaultAvatars = async () => {
  loadingDefaultAvatars.value = true
  try {
    const avatars = await getDefaultAvatars()
    defaultAvatars.value = avatars
    
    // 获取当前用户的年龄和性别来获取默认头像
    const profile = await getUserProfile()
    if (profile.birth_date && profile.gender) {
      const birthDate = new Date(profile.birth_date)
      const today = new Date()
      const age = today.getFullYear() - birthDate.getFullYear()
      
      // 查找合适的默认头像
      const suitableAvatar = avatars.find(avatar => {
        if (avatar.gender === profile.gender) {
          if ((avatar.age_group === 'child' && age < 18) ||
              (avatar.age_group === 'adult' && age >= 18 && age < 65) ||
              (avatar.age_group === 'elderly' && age >= 65)) {
            return true
          }
        }
        return false
      })
      
      if (suitableAvatar) {
        defaultAvatarUrl.value = suitableAvatar.avatar
      }
    }
  } catch (error) {
    ElMessage.error('获取默认头像失败')
    console.error(error)
  } finally {
    loadingDefaultAvatars.value = false
  }
}

const handleAvatarSuccess = (response) => {
  imageUrl.value = response.avatar
  selectedDefaultAvatar.value = null
}

const beforeAvatarUpload = (file) => {
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

const getGenderText = (gender) => {
  switch (gender) {
    case 'M':
      return '男性'
    case 'F':
      return '女性'
    default:
      return '其他'
  }
}

const getAgeGroupText = (ageGroup) => {
  switch (ageGroup) {
    case 'child':
      return '儿童'
    case 'adult':
      return '成人'
    case 'elderly':
      return '老年'
    default:
      return '未知'
  }
}
</script>

<style scoped>
.avatar-manager {
  padding: 20px;
}

.avatar-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
}

.current-avatar,
.upload-avatar,
.default-avatars {
  flex: 1;
  min-width: 250px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
  margin: 0 auto;
}

.avatar-uploader {
  text-align: center;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
}

.default-avatar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.default-avatar-item {
  cursor: pointer;
  padding: 10px;
  border-radius: 4px;
  transition: all 0.3s;
  text-align: center;
}

.default-avatar-item:hover {
  background-color: #e6f7ff;
}

.avatar-info {
  margin-top: 5px;
  font-size: 12px;
  color: #606266;
  display: flex;
  flex-direction: column;
}

.avatar-actions {
  text-align: center;
}
</style> 