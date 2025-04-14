<!-- 头像管理界面 -->
<template>
  <div class="avatar-manager">
    <h1>头像管理</h1>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="current-avatar">
          <h2>当前头像</h2>
          <div class="avatar-display">
            <el-avatar :size="120" :src="currentAvatar" />
          </div>
          <p>用户名: {{ userInfo?.username }}</p>
          <p>性别: {{ userInfo?.gender || '未知' }}</p>
          <p>年龄: {{ userAge }} 岁</p>
        </div>
        
        <el-upload
          class="avatar-upload"
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleAvatarChange"
          accept="image/*"
        >
          <el-button type="primary">上传新头像</el-button>
        </el-upload>
      </el-col>
      
      <el-col :span="12">
        <div class="default-avatars">
          <h2>默认头像</h2>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="儿童" name="child">
              <div class="avatar-list">
                <div class="avatar-item">
                  <el-avatar :size="100" :src="maleChildAvatar" @click="selectDefaultAvatar('male_child')" />
                  <p>男孩</p>
                </div>
                <div class="avatar-item">
                  <el-avatar :size="100" :src="femaleChildAvatar" @click="selectDefaultAvatar('female_child')" />
                  <p>女孩</p>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="成年" name="adult">
              <div class="avatar-list">
                <div class="avatar-item">
                  <el-avatar :size="100" :src="maleAdultAvatar" @click="selectDefaultAvatar('male_adult')" />
                  <p>成年男性</p>
                </div>
                <div class="avatar-item">
                  <el-avatar :size="100" :src="femaleAdultAvatar" @click="selectDefaultAvatar('female_adult')" />
                  <p>成年女性</p>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="老年" name="elder">
              <div class="avatar-list">
                <div class="avatar-item">
                  <el-avatar :size="100" :src="maleElderAvatar" @click="selectDefaultAvatar('male_elder')" />
                  <p>老年男性</p>
                </div>
                <div class="avatar-item">
                  <el-avatar :size="100" :src="femaleElderAvatar" @click="selectDefaultAvatar('female_elder')" />
                  <p>老年女性</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>
    
    <div class="action-buttons">
      <el-button type="primary" @click="saveAvatar" :loading="uploading">保存头像</el-button>
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
</script>

<style scoped>
.avatar-manager {
  padding: 20px;
}

.current-avatar, .default-avatars {
  background-color: #f7f8fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  min-height: 300px;
}

.avatar-display {
  margin: 20px 0;
  display: flex;
  justify-content: center;
}

.avatar-upload {
  margin-top: 20px;
  text-align: center;
}

.avatar-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.avatar-item {
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.avatar-item:hover {
  transform: scale(1.05);
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}
</style> 