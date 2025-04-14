<!-- src/App.vue -->
<template>
  <div id="app">
    <el-config-provider>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-config-provider>
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    console.log('App 组件已创建')
  },
  mounted() {
    console.log('App 组件已挂载')
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
}

.app-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  overflow: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 全局样式 */
* {
  box-sizing: border-box;
}

.el-main {
  padding: 20px;
  height: 100%;
}

.el-aside {
  transition: width 0.3s;
}

@media screen and (max-width: 768px) {
  .el-aside {
    width: 64px !important;
  }
}
</style>

