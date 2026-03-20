<template>
  <el-container class="main-layout">
    <!-- Sidebar -->
    <el-aside width="220px" class="sidebar">
      <div class="sidebar-logo">
        <el-icon :size="24" color="#60A5FA"><Connection /></el-icon>
        <span class="logo-text">护肤知识图谱</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#1E293B"
        text-color="#94A3B8"
        active-text-color="#FFFFFF"
        router
      >
        <el-menu-item index="/knowledge">
          <el-icon><Share /></el-icon>
          <span>知识管理</span>
        </el-menu-item>
        <el-menu-item index="/dashboard" disabled>
          <el-icon><DataAnalysis /></el-icon>
          <span>概览 Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/annotation" disabled>
          <el-icon><EditPen /></el-icon>
          <span>标注 & 训练</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <span class="version">v1.0 · MVP</span>
      </div>
    </el-aside>

    <!-- Main content -->
    <el-container class="main-container">
      <!-- Top bar -->
      <el-header class="topbar" height="48px">
        <div class="topbar-left">
          <h3 class="page-title">{{ pageTitle }}</h3>
        </div>
        <div class="topbar-right">
          <el-badge :value="3" :max="99" class="notification-badge">
            <el-button :icon="Bell" circle size="small" />
          </el-badge>
          <el-dropdown trigger="click">
            <div class="user-info">
              <el-avatar :size="28" style="background: #3B82F6">管</el-avatar>
              <span class="username">管理员</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>系统设置</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Router view -->
      <el-main class="page-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/knowledge': '知识管理',
    '/dashboard': '概览 Dashboard',
    '/annotation': '标注 & 训练',
  }
  return titles[route.path] || '护肤知识图谱管理平台'
})
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.sidebar {
  background: #1E293B;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-logo {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid #334155;
}

.logo-text {
  color: #F1F5F9;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  border-right: none;

  .el-menu-item {
    height: 48px;
    line-height: 48px;
    &.is-active {
      background: #334155 !important;
      border-left: 3px solid #3B82F6;
    }
    &.is-disabled {
      opacity: 0.4;
    }
  }
}

.sidebar-footer {
  padding: 12px 20px;
  border-top: 1px solid #334155;
}

.version {
  color: #64748B;
  font-size: 12px;
}

.main-container {
  flex-direction: column;
}

.topbar {
  background: #FFFFFF;
  border-bottom: 1px solid #E2E8F0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.topbar-left {
  .page-title {
    font-size: 16px;
    font-weight: 600;
    color: #1E293B;
  }
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  :deep(.el-badge__content) {
    font-size: 10px;
  }
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #475569;
}

.page-content {
  padding: 0;
  overflow: hidden;
}
</style>
