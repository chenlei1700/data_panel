// src/router/index.js
// 此文件由 auto-config-generator.py 自动生成，请勿手动编辑

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import StackedAreaDemo from '../views/StackedAreaDemo.vue'
import StockDashboard from '../views/StockDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/demo_1',
    name: 'demo_1',
    component: StockDashboard,
    meta: {
      title: '股票仪表盘演示',
      apiService: 'demo_1'  // 对应API配置中的键名，使用端口5004
    }
  },
  {
    path: '/stacked-area-demo',
    name: 'stacked_area_demo',
    component: StackedAreaDemo,
    meta: {
      title: '堆叠面积图组件演示',
      apiService: 'stacked_area_demo'  // 对应API配置中的键名，使用端口5007
    }
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
