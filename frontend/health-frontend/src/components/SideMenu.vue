<template>
  <el-menu
    :default-active="route.path"
    class="side-menu"
    :collapse="isCollapse"
    @select="handleSelect"
  >
    <el-menu-item index="/dashboard">
      <el-icon><House /></el-icon>
      <span>首页</span>
    </el-menu-item>

    <el-sub-menu index="records">
      <template #title>
        <el-icon><Document /></el-icon>
        <span>健康记录</span>
      </template>
      <el-menu-item index="/medical-records">
        <el-icon><FirstAidKit /></el-icon>
        <span>就医记录</span>
      </el-menu-item>
      <el-menu-item index="/medication-records">
        <el-icon><Medicine /></el-icon>
        <span>用药记录</span>
      </el-menu-item>
      <el-menu-item index="/vaccination-records">
        <el-icon><Syringe /></el-icon>
        <span>疫苗接种</span>
      </el-menu-item>
      <el-menu-item index="/physical-exams">
        <el-icon><Stethoscope /></el-icon>
        <span>体检报告</span>
      </el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/profile">
      <el-icon><User /></el-icon>
      <span>个人资料</span>
    </el-menu-item>

    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <span>系统设置</span>
    </el-menu-item>
  </el-menu>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  Document,
  Briefcase as FirstAidKit,
  Notebook as Medicine,
  Stamp as Syringe,
  Odometer as Stethoscope,
  User,
  Setting
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'SideMenu',
  components: {
    House,
    Document,
    FirstAidKit,
    Medicine,
    Syringe,
    Stethoscope,
    User,
    Setting
  },
  props: {
    isCollapse: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const route = useRoute()
    const router = useRouter()

    const handleSelect = (index: string) => {
      router.push(index)
    }

    return {
      route,
      handleSelect
    }
  }
})
</script>

<style scoped>
.side-menu {
  height: 100%;
  border-right: none;
}

.side-menu:not(.el-menu--collapse) {
  width: 200px;
}
</style> 