# Vue前端管理界面架构文档

## 概述

Vue前端管理界面是小智ESP32服务器的Web管理控制台，基于Vue.js 2.x和Element UI构建，提供设备管理、用户管理、系统配置等功能的可视化界面。

## 技术栈

- **Vue.js**: 2.6+ (前端框架)
- **Element UI**: 2.15+ (UI组件库)
- **Vue Router**: 3.6+ (路由管理)
- **Vuex**: 3.6+ (状态管理)
- **Axios**: HTTP客户端
- **Sass**: CSS预处理器
- **Webpack**: 构建工具

## 项目结构

```
manager-web/
├── public/                     # 静态资源
│   ├── index.html             # 主HTML文件
│   ├── favicon.ico            # 网站图标
│   └── offline.html           # 离线页面
├── src/                       # 源代码
│   ├── main.js                # 应用入口
│   ├── App.vue                # 根组件
│   ├── apis/                  # API接口
│   │   ├── api.js             # API配置
│   │   ├── httpRequest.js     # HTTP请求封装
│   │   └── module/            # 模块API
│   ├── assets/                # 静态资源
│   │   ├── images/            # 图片资源
│   │   └── styles/            # 样式文件
│   ├── components/            # 公共组件
│   ├── router/                # 路由配置
│   ├── store/                 # 状态管理
│   ├── utils/                 # 工具类
│   └── views/                 # 页面组件
├── package.json               # 依赖配置
├── vue.config.js              # Vue配置
└── babel.config.js            # Babel配置
```

## 核心架构

### 1. 应用入口

```javascript
// main.js
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import './assets/styles/global.scss'

Vue.use(ElementUI)
Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
```

### 2. 根组件

```vue
<!-- App.vue -->
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // 检查用户登录状态
    this.checkAuth()
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('token')
      if (!token && this.$route.meta.requiresAuth) {
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style lang="scss">
#app {
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}
</style>
```

## 路由管理

### 1. 路由配置

```javascript
// router/index.js
import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/components/Layout.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', requiresAuth: true }
      },
      {
        path: 'device',
        name: 'DeviceManagement',
        component: () => import('@/views/DeviceManagement.vue'),
        meta: { title: '设备管理', requiresAuth: true }
      },
      {
        path: 'user',
        name: 'UserManagement',
        component: () => import('@/views/UserManagement.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'config',
        name: 'ConfigManagement',
        component: () => import('@/views/ConfigManagement.vue'),
        meta: { title: '配置管理', requiresAuth: true }
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
```

### 2. 布局组件

```vue
<!-- components/Layout.vue -->
<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <img src="@/assets/images/logo.png" alt="Logo">
        <span>小智管理平台</span>
      </div>
      
      <el-menu
        :default-active="$route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF">
        
        <el-menu-item index="/dashboard">
          <i class="el-icon-s-home"></i>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/device">
          <i class="el-icon-cpu"></i>
          <span>设备管理</span>
        </el-menu-item>
        
        <el-menu-item index="/user">
          <i class="el-icon-user"></i>
          <span>用户管理</span>
        </el-menu-item>
        
        <el-menu-item index="/config">
          <i class="el-icon-setting"></i>
          <span>配置管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              {{ userInfo.username }}
              <i class="el-icon-arrow-down"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Layout',
  computed: {
    ...mapState(['userInfo']),
    breadcrumbs() {
      const matched = this.$route.matched.filter(item => item.meta && item.meta.title)
      return matched.map(item => ({
        title: item.meta.title,
        path: item.path
      }))
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.$store.dispatch('logout')
        this.$router.push('/login')
      } else if (command === 'profile') {
        this.$router.push('/profile')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  
  .sidebar {
    background-color: #304156;
    
    .logo {
      height: 60px;
      display: flex;
      align-items: center;
      padding: 0 20px;
      color: #fff;
      
      img {
        width: 32px;
        height: 32px;
        margin-right: 10px;
      }
    }
  }
  
  .header {
    background-color: #fff;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    
    .user-info {
      cursor: pointer;
      color: #606266;
    }
  }
  
  .main-content {
    background-color: #f0f2f5;
    padding: 20px;
  }
}
</style>
```

## 状态管理

### 1. Vuex配置

```javascript
// store/index.js
import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import device from './modules/device'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    device
  },
  
  state: {
    loading: false,
    sidebarCollapsed: false
  },
  
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    TOGGLE_SIDEBAR(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed
    }
  },
  
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    toggleSidebar({ commit }) {
      commit('TOGGLE_SIDEBAR')
    }
  }
})
```

### 2. 用户模块

```javascript
// store/modules/user.js
import { login, logout, getUserInfo } from '@/apis/module/auth'

const state = {
  token: localStorage.getItem('token') || '',
  userInfo: {},
  permissions: []
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    localStorage.setItem('token', token)
  },
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
  },
  SET_PERMISSIONS(state, permissions) {
    state.permissions = permissions
  },
  CLEAR_USER(state) {
    state.token = ''
    state.userInfo = {}
    state.permissions = []
    localStorage.removeItem('token')
  }
}

const actions = {
  async login({ commit }, loginForm) {
    try {
      const response = await login(loginForm)
      const { token, userInfo } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER_INFO', userInfo)
      
      return response
    } catch (error) {
      throw error
    }
  },
  
  async getUserInfo({ commit }) {
    try {
      const response = await getUserInfo()
      const { userInfo, permissions } = response.data
      
      commit('SET_USER_INFO', userInfo)
      commit('SET_PERMISSIONS', permissions)
      
      return response
    } catch (error) {
      throw error
    }
  },
  
  async logout({ commit }) {
    try {
      await logout()
      commit('CLEAR_USER')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }
}

const getters = {
  isLoggedIn: state => !!state.token,
  hasPermission: state => permission => {
    return state.permissions.includes(permission)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
```

### 3. 设备模块

```javascript
// store/modules/device.js
import { getDeviceList, createDevice, updateDevice, deleteDevice } from '@/apis/module/device'

const state = {
  deviceList: [],
  total: 0,
  loading: false
}

const mutations = {
  SET_DEVICE_LIST(state, { list, total }) {
    state.deviceList = list
    state.total = total
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  ADD_DEVICE(state, device) {
    state.deviceList.unshift(device)
    state.total++
  },
  UPDATE_DEVICE(state, device) {
    const index = state.deviceList.findIndex(item => item.id === device.id)
    if (index !== -1) {
      state.deviceList.splice(index, 1, device)
    }
  },
  DELETE_DEVICE(state, id) {
    const index = state.deviceList.findIndex(item => item.id === id)
    if (index !== -1) {
      state.deviceList.splice(index, 1)
      state.total--
    }
  }
}

const actions = {
  async getDeviceList({ commit }, params) {
    commit('SET_LOADING', true)
    try {
      const response = await getDeviceList(params)
      const { list, total } = response.data
      commit('SET_DEVICE_LIST', { list, total })
      return response
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createDevice({ commit }, deviceData) {
    const response = await createDevice(deviceData)
    commit('ADD_DEVICE', response.data)
    return response
  },
  
  async updateDevice({ commit }, { id, data }) {
    const response = await updateDevice(id, data)
    commit('UPDATE_DEVICE', response.data)
    return response
  },
  
  async deleteDevice({ commit }, id) {
    await deleteDevice(id)
    commit('DELETE_DEVICE', id)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
```

## API接口管理

### 1. HTTP请求封装

```javascript
// apis/httpRequest.js
import axios from 'axios'
import { Message } from 'element-ui'
import router from '@/router'
import store from '@/store'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const { code, message, data } = response.data
    
    if (code === 200) {
      return response.data
    } else {
      Message.error(message || '请求失败')
      return Promise.reject(new Error(message || '请求失败'))
    }
  },
  error => {
    console.error('Response error:', error)
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          Message.error('登录已过期，请重新登录')
          store.dispatch('user/logout')
          router.push('/login')
          break
        case 403:
          Message.error('没有权限访问')
          break
        case 404:
          Message.error('请求的资源不存在')
          break
        case 500:
          Message.error('服务器内部错误')
          break
        default:
          Message.error(data.message || '请求失败')
      }
    } else {
      Message.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default service
```

### 2. 模块API

```javascript
// apis/module/device.js
import request from '@/apis/httpRequest'

// 获取设备列表
export function getDeviceList(params) {
  return request({
    url: '/v1/device',
    method: 'get',
    params
  })
}

// 创建设备
export function createDevice(data) {
  return request({
    url: '/v1/device',
    method: 'post',
    data
  })
}

// 更新设备
export function updateDevice(id, data) {
  return request({
    url: `/v1/device/${id}`,
    method: 'put',
    data
  })
}

// 删除设备
export function deleteDevice(id) {
  return request({
    url: `/v1/device/${id}`,
    method: 'delete'
  })
}

// 获取设备详情
export function getDeviceDetail(id) {
  return request({
    url: `/v1/device/${id}`,
    method: 'get'
  })
}
```

## 页面组件

### 1. 登录页面

```vue
<!-- views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <img src="@/assets/images/logo.png" alt="Logo">
        <h2>小智管理平台</h2>
      </div>
      
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        class="login-form">
        
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
            size="large" />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
            size="large"
            @keyup.enter.native="handleLogin" />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      loading: false,
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    ...mapActions('user', ['login']),
    
    async handleLogin() {
      try {
        await this.$refs.loginForm.validate()
        
        this.loading = true
        await this.login(this.loginForm)
        
        this.$message.success('登录成功')
        this.$router.push('/')
      } catch (error) {
        console.error('Login error:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  
  .login-box {
    width: 400px;
    padding: 40px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    
    .login-header {
      text-align: center;
      margin-bottom: 30px;
      
      img {
        width: 64px;
        height: 64px;
        margin-bottom: 16px;
      }
      
      h2 {
        color: #303133;
        margin: 0;
      }
    }
    
    .login-form {
      .login-button {
        width: 100%;
      }
    }
  }
}
</style>
```

### 2. 设备管理页面

```vue
<!-- views/DeviceManagement.vue -->
<template>
  <div class="device-management">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="设备名称">
          <el-input
            v-model="searchForm.deviceName"
            placeholder="请输入设备名称"
            clearable />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="searchForm.deviceType" placeholder="请选择设备类型" clearable>
            <el-option label="ESP32" value="ESP32" />
            <el-option label="ESP8266" value="ESP8266" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 数据表格 -->
    <el-card class="table-card">
      <div slot="header" class="table-header">
        <span>设备列表</span>
        <el-button type="primary" @click="handleAdd">添加设备</el-button>
      </div>
      
      <el-table
        :data="deviceList"
        v-loading="loading"
        border
        stripe>
        
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="deviceName" label="设备名称" />
        <el-table-column prop="deviceType" label="设备类型" />
        <el-table-column prop="status" label="状态">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'ONLINE' ? 'success' : 'danger'">
              {{ scope.row.status === 'ONLINE' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        :current-page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.size"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="500px"
      @close="handleDialogClose">
      
      <el-form
        ref="deviceForm"
        :model="deviceForm"
        :rules="deviceRules"
        label-width="100px">
        
        <el-form-item label="设备名称" prop="deviceName">
          <el-input v-model="deviceForm.deviceName" placeholder="请输入设备名称" />
        </el-form-item>
        
        <el-form-item label="设备类型" prop="deviceType">
          <el-select v-model="deviceForm.deviceType" placeholder="请选择设备类型">
            <el-option label="ESP32" value="ESP32" />
            <el-option label="ESP8266" value="ESP8266" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="deviceForm.description"
            type="textarea"
            placeholder="请输入设备描述" />
        </el-form-item>
      </el-form>
      
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'DeviceManagement',
  data() {
    return {
      loading: false,
      submitLoading: false,
      dialogVisible: false,
      isEdit: false,
      searchForm: {
        deviceName: '',
        deviceType: ''
      },
      deviceForm: {
        deviceName: '',
        deviceType: '',
        description: ''
      },
      deviceRules: {
        deviceName: [
          { required: true, message: '请输入设备名称', trigger: 'blur' }
        ],
        deviceType: [
          { required: true, message: '请选择设备类型', trigger: 'change' }
        ]
      },
      pagination: {
        page: 1,
        size: 10
      }
    }
  },
  computed: {
    ...mapState('device', ['deviceList', 'total']),
    dialogTitle() {
      return this.isEdit ? '编辑设备' : '添加设备'
    }
  },
  mounted() {
    this.loadDeviceList()
  },
  methods: {
    ...mapActions('device', ['getDeviceList', 'createDevice', 'updateDevice', 'deleteDevice']),
    
    async loadDeviceList() {
      try {
        this.loading = true
        const params = {
          ...this.searchForm,
          ...this.pagination
        }
        await this.getDeviceList(params)
      } catch (error) {
        console.error('Load device list error:', error)
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      this.pagination.page = 1
      this.loadDeviceList()
    },
    
    handleReset() {
      this.searchForm = {
        deviceName: '',
        deviceType: ''
      }
      this.handleSearch()
    },
    
    handleSizeChange(size) {
      this.pagination.size = size
      this.loadDeviceList()
    },
    
    handleCurrentChange(page) {
      this.pagination.page = page
      this.loadDeviceList()
    },
    
    handleAdd() {
      this.isEdit = false
      this.deviceForm = {
        deviceName: '',
        deviceType: '',
        description: ''
      }
      this.dialogVisible = true
    },
    
    handleEdit(row) {
      this.isEdit = true
      this.deviceForm = { ...row }
      this.dialogVisible = true
    },
    
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该设备吗？', '提示', {
          type: 'warning'
        })
        
        await this.deleteDevice(row.id)
        this.$message.success('删除成功')
        this.loadDeviceList()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Delete device error:', error)
        }
      }
    },
    
    async handleSubmit() {
      try {
        await this.$refs.deviceForm.validate()
        
        this.submitLoading = true
        if (this.isEdit) {
          await this.updateDevice({
            id: this.deviceForm.id,
            data: this.deviceForm
          })
          this.$message.success('更新成功')
        } else {
          await this.createDevice(this.deviceForm)
          this.$message.success('创建成功')
        }
        
        this.dialogVisible = false
        this.loadDeviceList()
      } catch (error) {
        console.error('Submit device error:', error)
      } finally {
        this.submitLoading = false
      }
    },
    
    handleDialogClose() {
      this.$refs.deviceForm.resetFields()
    }
  }
}
</script>

<style lang="scss" scoped>
.device-management {
  .search-card {
    margin-bottom: 20px;
  }
  
  .table-card {
    .table-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .el-pagination {
      margin-top: 20px;
      text-align: right;
    }
  }
}
</style>
```

## 公共组件

### 1. 表格组件

```vue
<!-- components/DataTable.vue -->
<template>
  <div class="data-table">
    <el-table
      :data="data"
      v-loading="loading"
      border
      stripe
      @selection-change="handleSelectionChange">
      
      <el-table-column
        v-if="selection"
        type="selection"
        width="55" />
      
      <el-table-column
        v-for="column in columns"
        :key="column.prop"
        :prop="column.prop"
        :label="column.label"
        :width="column.width"
        :formatter="column.formatter">
        
        <template slot-scope="scope" v-if="column.slot">
          <slot :name="column.slot" :row="scope.row" :$index="scope.$index" />
        </template>
      </el-table-column>
      
      <el-table-column
        v-if="actions"
        label="操作"
        :width="actionWidth">
        <template slot-scope="scope">
          <slot name="actions" :row="scope.row" :$index="scope.$index" />
        </template>
      </el-table-column>
    </el-table>
    
    <el-pagination
      v-if="pagination"
      :current-page="pagination.page"
      :page-sizes="pagination.sizes"
      :page-size="pagination.size"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange" />
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    columns: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    selection: {
      type: Boolean,
      default: false
    },
    actions: {
      type: Boolean,
      default: false
    },
    actionWidth: {
      type: [String, Number],
      default: 200
    },
    pagination: {
      type: Object,
      default: null
    }
  },
  methods: {
    handleSelectionChange(selection) {
      this.$emit('selection-change', selection)
    },
    handleSizeChange(size) {
      this.$emit('size-change', size)
    },
    handleCurrentChange(page) {
      this.$emit('current-change', page)
    }
  }
}
</script>

<style lang="scss" scoped>
.data-table {
  .el-pagination {
    margin-top: 20px;
    text-align: right;
  }
}
</style>
```

### 2. 搜索表单组件

```vue
<!-- components/SearchForm.vue -->
<template>
  <el-card class="search-form">
    <el-form :inline="true" :model="form" class="form-content">
      <el-form-item
        v-for="item in fields"
        :key="item.prop"
        :label="item.label">
        
        <!-- 输入框 -->
        <el-input
          v-if="item.type === 'input'"
          v-model="form[item.prop]"
          :placeholder="item.placeholder"
          :clearable="item.clearable !== false" />
        
        <!-- 选择框 -->
        <el-select
          v-else-if="item.type === 'select'"
          v-model="form[item.prop]"
          :placeholder="item.placeholder"
          :clearable="item.clearable !== false">
          <el-option
            v-for="option in item.options"
            :key="option.value"
            :label="option.label"
            :value="option.value" />
        </el-select>
        
        <!-- 日期选择器 -->
        <el-date-picker
          v-else-if="item.type === 'date'"
          v-model="form[item.prop]"
          :type="item.dateType || 'date'"
          :placeholder="item.placeholder"
          :format="item.format"
          :value-format="item.valueFormat" />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script>
export default {
  name: 'SearchForm',
  props: {
    fields: {
      type: Array,
      required: true
    },
    value: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      form: { ...this.value }
    }
  },
  watch: {
    value: {
      handler(val) {
        this.form = { ...val }
      },
      deep: true
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', this.form)
    },
    handleReset() {
      this.form = {}
      this.$emit('reset')
    }
  }
}
</script>

<style lang="scss" scoped>
.search-form {
  margin-bottom: 20px;
  
  .form-content {
    .el-form-item {
      margin-bottom: 0;
    }
  }
}
</style>
```

## 工具类

### 1. 日期工具

```javascript
// utils/date.js
import dayjs from 'dayjs'

// 格式化日期
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  return dayjs(date).format(format)
}

// 获取相对时间
export function getRelativeTime(date) {
  if (!date) return ''
  return dayjs(date).fromNow()
}

// 获取日期范围
export function getDateRange(type) {
  const now = dayjs()
  
  switch (type) {
    case 'today':
      return [now.startOf('day'), now.endOf('day')]
    case 'yesterday':
      return [now.subtract(1, 'day').startOf('day'), now.subtract(1, 'day').endOf('day')]
    case 'week':
      return [now.startOf('week'), now.endOf('week')]
    case 'month':
      return [now.startOf('month'), now.endOf('month')]
    default:
      return [now.subtract(7, 'day'), now]
  }
}
```

### 2. 验证工具

```javascript
// utils/validator.js
// 手机号验证
export function validatePhone(phone) {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

// 邮箱验证
export function validateEmail(email) {
  const reg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return reg.test(email)
}

// 密码强度验证
export function validatePassword(password) {
  const reg = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/
  return reg.test(password)
}
```

## 构建配置

### 1. Vue配置

```javascript
// vue.config.js
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/xiaozhi/api'
        }
      }
    }
  },
  
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src')
      }
    }
  },
  
  css: {
    loaderOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  }
})
```

### 2. 环境配置

```javascript
// .env.development
NODE_ENV=development
VUE_APP_API_BASE_URL=http://localhost:8002/xiaozhi/api

// .env.production
NODE_ENV=production
VUE_APP_API_BASE_URL=/api
```

## 部署配置

### 1. 构建脚本

```json
// package.json
{
  "scripts": {
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build",
    "build:prod": "vue-cli-service build --mode production",
    "lint": "vue-cli-service lint"
  }
}
```

### 2. Nginx配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 扩展开发指南

### 1. 添加新页面

1. 在 `views` 目录创建页面组件
2. 在路由配置中添加路由
3. 在菜单中添加菜单项
4. 创建对应的API接口

### 2. 添加新组件

1. 在 `components` 目录创建组件
2. 定义组件的props和events
3. 在页面中使用组件

### 3. 添加新功能

1. 在Vuex中添加状态管理
2. 创建API接口
3. 在页面中实现功能逻辑

## 最佳实践

### 1. 组件设计

- 组件职责单一
- 合理使用props和events
- 避免组件间直接通信

### 2. 状态管理

- 合理划分模块
- 避免状态冗余
- 使用getters计算派生状态

### 3. 性能优化

- 使用懒加载
- 合理使用v-if和v-show
- 避免不必要的计算

### 4. 代码规范

- 使用ESLint
- 遵循Vue风格指南
- 编写单元测试

## 总结

Vue前端管理界面采用组件化、模块化的架构设计，提供了完整的设备管理、用户管理等功能。通过合理的状态管理、路由配置和组件设计，确保系统的可维护性和扩展性。 