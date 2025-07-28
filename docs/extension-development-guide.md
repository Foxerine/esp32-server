# 扩展功能开发指南

## 概述

本指南详细说明如何为小智ESP32服务器开发扩展功能，包括AI服务提供商、工具调用、API接口等。开发扩展功能时，应尽量避免修改原有代码，而是使用独立的模块或插件方式。

## 扩展开发原则

### 1. 开闭原则
- 对扩展开放，对修改封闭
- 新增功能通过继承或组合实现
- 避免直接修改核心代码

### 2. 模块化设计
- 每个扩展功能独立成模块
- 清晰的接口定义
- 松耦合的架构设计

### 3. 配置驱动
- 通过配置文件启用/禁用功能
- 支持热插拔
- 便于维护和部署

## AI服务提供商扩展

### 1. 添加新的LLM提供商

```python
# core/providers/llm/custom_llm.py
from core.providers.llm.base import BaseLLM
from typing import Dict, List, Optional
import aiohttp
import json

class CustomLLM(BaseLLM):
    """自定义LLM提供商"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", "default-model")
        self.max_tokens = config.get("max_tokens", 2048)
    
    async def initialize(self):
        """初始化提供商"""
        # 验证配置
        if not self.api_key:
            raise ValueError("API密钥未配置")
        
        # 测试连接
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                if response.status != 200:
                    raise ConnectionError("无法连接到LLM服务")
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """聊天对话"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API请求失败: {response.status}")
                    
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            self.logger.error(f"LLM聊天失败: {e}")
            raise
    
    async def stream_chat(self, messages: List[Dict], **kwargs):
        """流式聊天"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", 0.7),
                "stream": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as response:
                    if response.status != 200:
                        raise Exception(f"API请求失败: {response.status}")
                    
                    async for line in response.content:
                        if line:
                            data = json.loads(line.decode('utf-8'))
                            if data.get("choices"):
                                content = data["choices"][0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                                    
        except Exception as e:
            self.logger.error(f"LLM流式聊天失败: {e}")
            raise
```

### 2. 注册新提供商

```python
# 在配置文件中添加新提供商
# config.yaml
LLM:
  custom_llm:
    api_key: "your_api_key"
    base_url: "https://api.custom-llm.com"
    model: "custom-model"
    max_tokens: 2048
    temperature: 0.7

# 选择使用新提供商
selected_module:
  LLM: "custom_llm"
```

### 3. 提供商工厂模式

```python
# core/providers/llm/factory.py
from typing import Dict, Type
from core.providers.llm.base import BaseLLM
from core.providers.llm.openai import OpenAILLM
from core.providers.llm.custom_llm import CustomLLM

class LLMFactory:
    """LLM提供商工厂"""
    
    _providers: Dict[str, Type[BaseLLM]] = {
        "openai": OpenAILLM,
        "custom_llm": CustomLLM
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLM]):
        """注册新的提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str, config: Dict) -> BaseLLM:
        """创建提供商实例"""
        if name not in cls._providers:
            raise ValueError(f"不支持的LLM提供商: {name}")
        
        provider_class = cls._providers[name]
        return provider_class(config)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """列出所有可用提供商"""
        return list(cls._providers.keys())

# 注册自定义提供商
LLMFactory.register_provider("custom_llm", CustomLLM)
```

## 工具调用扩展

### 1. 添加新的工具类型

```python
# core/providers/tools/custom_tool/custom_executor.py
from core.providers.tools.base.tool_executor import BaseToolExecutor
from typing import Dict, Any
import asyncio

class CustomToolExecutor(BaseToolExecutor):
    """自定义工具执行器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_endpoint = config.get("api_endpoint")
        self.api_key = config.get("api_key")
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        try:
            action = params.get("action")
            
            if action == "custom_action":
                return await self._custom_action(params)
            elif action == "data_process":
                return await self._data_process(params)
            else:
                raise ValueError(f"不支持的操作: {action}")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "工具执行失败"
            }
    
    async def _custom_action(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """自定义操作"""
        # 实现具体的业务逻辑
        data = params.get("data")
        result = await self._process_data(data)
        
        return {
            "success": True,
            "data": result,
            "message": "自定义操作执行成功"
        }
    
    async def _data_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """数据处理"""
        input_data = params.get("input_data")
        process_type = params.get("process_type", "default")
        
        # 根据处理类型执行不同的处理逻辑
        if process_type == "transform":
            result = await self._transform_data(input_data)
        elif process_type == "filter":
            result = await self._filter_data(input_data)
        else:
            result = await self._default_process(input_data)
        
        return {
            "success": True,
            "data": result,
            "message": "数据处理完成"
        }
    
    async def _process_data(self, data: Any) -> Any:
        """处理数据的具体实现"""
        # 模拟异步处理
        await asyncio.sleep(0.1)
        return {"processed": data, "timestamp": asyncio.get_event_loop().time()}
    
    async def _transform_data(self, data: Any) -> Any:
        """数据转换"""
        # 实现数据转换逻辑
        return {"transformed": data}
    
    async def _filter_data(self, data: Any) -> Any:
        """数据过滤"""
        # 实现数据过滤逻辑
        return {"filtered": data}
    
    async def _default_process(self, data: Any) -> Any:
        """默认处理"""
        return {"default_processed": data}
```

### 2. 工具描述器

```python
# core/providers/tools/custom_tool/custom_descriptor.py
from core.providers.tools.base.tool_types import ToolDescriptor
from typing import Dict, Any

class CustomToolDescriptor(ToolDescriptor):
    """自定义工具描述器"""
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具模式定义"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["custom_action", "data_process"],
                    "description": "要执行的操作"
                },
                "data": {
                    "type": "string",
                    "description": "要处理的数据"
                },
                "process_type": {
                    "type": "string",
                    "enum": ["transform", "filter", "default"],
                    "description": "数据处理类型"
                }
            },
            "required": ["action"]
        }
    
    def get_tool_description(self) -> str:
        """获取工具描述"""
        return "自定义工具，支持数据处理和自定义操作"
    
    def get_examples(self) -> List[Dict[str, Any]]:
        """获取使用示例"""
        return [
            {
                "action": "custom_action",
                "data": "示例数据",
                "description": "执行自定义操作"
            },
            {
                "action": "data_process",
                "input_data": "输入数据",
                "process_type": "transform",
                "description": "转换数据"
            }
        ]
```

### 3. 注册新工具

```python
# core/providers/tools/unified_tool_manager.py
from core.providers.tools.custom_tool.custom_executor import CustomToolExecutor
from core.providers.tools.custom_tool.custom_descriptor import CustomToolDescriptor

class UnifiedToolManager:
    """统一工具管理器"""
    
    def __init__(self):
        self.tools = {}
        self.descriptors = {}
    
    def register_custom_tool(self, tool_name: str, config: Dict):
        """注册自定义工具"""
        # 创建工具执行器
        executor = CustomToolExecutor(config)
        
        # 创建工具描述器
        descriptor = CustomToolDescriptor()
        
        # 注册工具
        self.tools[tool_name] = executor
        self.descriptors[tool_name] = descriptor
        
        self.logger.info(f"注册自定义工具: {tool_name}")
    
    def get_tool_schemas(self) -> Dict[str, Any]:
        """获取所有工具的模式定义"""
        schemas = {}
        for name, descriptor in self.descriptors.items():
            schemas[name] = {
                "description": descriptor.get_tool_description(),
                "schema": descriptor.get_tool_schema(),
                "examples": descriptor.get_examples()
            }
        return schemas
```

## API接口扩展

### 1. 添加新的API处理器

```python
# core/api/custom_handler.py
from core.api.base_handler import BaseHandler
from core.utils.response import success_response, error_response
from typing import Dict, Any
import json

class CustomAPIHandler(BaseHandler):
    """自定义API处理器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.custom_service = CustomService(config)
    
    async def handle_get(self, request) -> Dict[str, Any]:
        """处理GET请求"""
        try:
            # 获取查询参数
            params = dict(request.query)
            
            # 根据路径处理不同的请求
            path = request.path
            
            if path.endswith("/custom/data"):
                result = await self.custom_service.get_data(params)
            elif path.endswith("/custom/status"):
                result = await self.custom_service.get_status()
            else:
                return error_response("未知的API路径")
            
            return success_response(result)
            
        except Exception as e:
            self.logger.error(f"GET请求处理失败: {e}")
            return error_response(str(e))
    
    async def handle_post(self, request) -> Dict[str, Any]:
        """处理POST请求"""
        try:
            # 获取请求体
            body = await request.json()
            
            # 根据路径处理不同的请求
            path = request.path
            
            if path.endswith("/custom/process"):
                result = await self.custom_service.process_data(body)
            elif path.endswith("/custom/action"):
                result = await self.custom_service.execute_action(body)
            else:
                return error_response("未知的API路径")
            
            return success_response(result)
            
        except Exception as e:
            self.logger.error(f"POST请求处理失败: {e}")
            return error_response(str(e))
    
    async def handle_put(self, request) -> Dict[str, Any]:
        """处理PUT请求"""
        try:
            body = await request.json()
            path = request.path
            
            if path.endswith("/custom/update"):
                result = await self.custom_service.update_data(body)
            else:
                return error_response("未知的API路径")
            
            return success_response(result)
            
        except Exception as e:
            self.logger.error(f"PUT请求处理失败: {e}")
            return error_response(str(e))
    
    async def handle_delete(self, request) -> Dict[str, Any]:
        """处理DELETE请求"""
        try:
            path = request.path
            
            if path.endswith("/custom/delete"):
                # 从路径中提取ID
                item_id = path.split("/")[-1]
                result = await self.custom_service.delete_data(item_id)
            else:
                return error_response("未知的API路径")
            
            return success_response(result)
            
        except Exception as e:
            self.logger.error(f"DELETE请求处理失败: {e}")
            return error_response(str(e))

class CustomService:
    """自定义服务类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = setup_logging()
    
    async def get_data(self, params: Dict) -> Dict[str, Any]:
        """获取数据"""
        # 实现数据获取逻辑
        return {
            "data": "示例数据",
            "params": params,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "status": "running",
            "uptime": 3600,
            "version": "1.0.0"
        }
    
    async def process_data(self, data: Dict) -> Dict[str, Any]:
        """处理数据"""
        # 实现数据处理逻辑
        processed_data = self._process(data)
        return {
            "original": data,
            "processed": processed_data,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def execute_action(self, action_data: Dict) -> Dict[str, Any]:
        """执行动作"""
        action = action_data.get("action")
        params = action_data.get("params", {})
        
        # 根据动作类型执行不同的逻辑
        if action == "custom_action":
            result = await self._custom_action(params)
        else:
            result = {"message": f"未知动作: {action}"}
        
        return {
            "action": action,
            "result": result,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def update_data(self, data: Dict) -> Dict[str, Any]:
        """更新数据"""
        # 实现数据更新逻辑
        return {
            "updated": True,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    async def delete_data(self, item_id: str) -> Dict[str, Any]:
        """删除数据"""
        # 实现数据删除逻辑
        return {
            "deleted": True,
            "id": item_id,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _process(self, data: Dict) -> Dict:
        """内部数据处理方法"""
        # 实现具体的数据处理逻辑
        return {"processed": data}
    
    async def _custom_action(self, params: Dict) -> Dict:
        """自定义动作"""
        # 实现自定义动作逻辑
        return {"action_result": params}
```

### 2. 注册API路由

```python
# core/http_server.py
from core.api.custom_handler import CustomAPIHandler

class SimpleHttpServer:
    """HTTP服务器"""
    
    def __init__(self, config):
        self.config = config
        self.handlers = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """注册处理器"""
        # 注册自定义API处理器
        custom_config = self.config.get("custom_api", {})
        if custom_config:
            self.handlers["/custom"] = CustomAPIHandler(custom_config)
    
    async def handle_request(self, request, response):
        """处理HTTP请求"""
        path = request.path
        
        # 查找对应的处理器
        handler = None
        for prefix, h in self.handlers.items():
            if path.startswith(prefix):
                handler = h
                break
        
        if handler:
            # 根据请求方法调用相应的处理函数
            method = request.method.lower()
            if method == "get":
                result = await handler.handle_get(request)
            elif method == "post":
                result = await handler.handle_post(request)
            elif method == "put":
                result = await handler.handle_put(request)
            elif method == "delete":
                result = await handler.handle_delete(request)
            else:
                result = error_response("不支持的HTTP方法")
        else:
            result = error_response("未找到对应的处理器")
        
        # 返回响应
        response.headers["Content-Type"] = "application/json"
        response.body = json.dumps(result).encode()
```

## 前端扩展

### 1. 添加新的Vue组件

```vue
<!-- src/components/CustomComponent.vue -->
<template>
  <div class="custom-component">
    <el-card>
      <div slot="header">
        <span>{{ title }}</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleRefresh">
          刷新
        </el-button>
      </div>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="请输入关键词" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="status" label="状态">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
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
      
      <el-pagination
        :current-page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.size"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </el-card>
    
    <!-- 编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      :visible.sync="dialogVisible"
      width="500px"
      @close="handleDialogClose">
      
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        label-width="100px">
        
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="请输入描述" />
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
import { getCustomList, createCustom, updateCustom, deleteCustom } from '@/apis/module/custom'

export default {
  name: 'CustomComponent',
  props: {
    title: {
      type: String,
      default: '自定义组件'
    }
  },
  data() {
    return {
      loading: false,
      submitLoading: false,
      dialogVisible: false,
      isEdit: false,
      searchForm: {
        keyword: ''
      },
      form: {
        name: '',
        status: 'active',
        description: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入名称', trigger: 'blur' }
        ],
        status: [
          { required: true, message: '请选择状态', trigger: 'change' }
        ]
      },
      tableData: [],
      total: 0,
      pagination: {
        page: 1,
        size: 10
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.isEdit ? '编辑' : '新增'
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.loading = true
        const params = {
          ...this.searchForm,
          ...this.pagination
        }
        const response = await getCustomList(params)
        this.tableData = response.data.list
        this.total = response.data.total
      } catch (error) {
        this.$message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      this.pagination.page = 1
      this.loadData()
    },
    
    handleReset() {
      this.searchForm = { keyword: '' }
      this.handleSearch()
    },
    
    handleSizeChange(size) {
      this.pagination.size = size
      this.loadData()
    },
    
    handleCurrentChange(page) {
      this.pagination.page = page
      this.loadData()
    },
    
    handleRefresh() {
      this.loadData()
    },
    
    handleAdd() {
      this.isEdit = false
      this.form = {
        name: '',
        status: 'active',
        description: ''
      }
      this.dialogVisible = true
    },
    
    handleEdit(row) {
      this.isEdit = true
      this.form = { ...row }
      this.dialogVisible = true
    },
    
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除该记录吗？', '提示', {
          type: 'warning'
        })
        
        await deleteCustom(row.id)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },
    
    async handleSubmit() {
      try {
        await this.$refs.form.validate()
        
        this.submitLoading = true
        if (this.isEdit) {
          await updateCustom(this.form.id, this.form)
          this.$message.success('更新成功')
        } else {
          await createCustom(this.form)
          this.$message.success('创建成功')
        }
        
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        this.$message.error('操作失败')
      } finally {
        this.submitLoading = false
      }
    },
    
    handleDialogClose() {
      this.$refs.form.resetFields()
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-component {
  .search-form {
    margin-bottom: 20px;
  }
  
  .el-pagination {
    margin-top: 20px;
    text-align: right;
  }
}
</style>
```

### 2. 添加新的API接口

```javascript
// src/apis/module/custom.js
import request from '@/apis/httpRequest'

// 获取自定义数据列表
export function getCustomList(params) {
  return request({
    url: '/custom/data',
    method: 'get',
    params
  })
}

// 创建自定义数据
export function createCustom(data) {
  return request({
    url: '/custom/data',
    method: 'post',
    data
  })
}

// 更新自定义数据
export function updateCustom(id, data) {
  return request({
    url: `/custom/data/${id}`,
    method: 'put',
    data
  })
}

// 删除自定义数据
export function deleteCustom(id) {
  return request({
    url: `/custom/data/${id}`,
    method: 'delete'
  })
}

// 获取自定义状态
export function getCustomStatus() {
  return request({
    url: '/custom/status',
    method: 'get'
  })
}

// 执行自定义动作
export function executeCustomAction(actionData) {
  return request({
    url: '/custom/action',
    method: 'post',
    data: actionData
  })
}
```

### 3. 添加新的路由

```javascript
// src/router/index.js
import CustomComponent from '@/components/CustomComponent.vue'

const routes = [
  // ... 其他路由
  {
    path: '/custom',
    name: 'CustomManagement',
    component: CustomComponent,
    meta: {
      title: '自定义管理',
      requiresAuth: true
    }
  }
]
```

## 配置管理扩展

### 1. 扩展配置文件

```yaml
# config.yaml
# 添加自定义配置
custom_api:
  enabled: true
  base_url: "https://api.custom.com"
  api_key: "your_api_key"
  timeout: 30

custom_tool:
  enabled: true
  api_endpoint: "https://tool.custom.com"
  api_key: "your_tool_api_key"

# 自定义LLM配置
LLM:
  custom_llm:
    api_key: "your_llm_api_key"
    base_url: "https://llm.custom.com"
    model: "custom-model"
    max_tokens: 2048

# 选择使用自定义模块
selected_module:
  LLM: "custom_llm"
```

### 2. 配置验证

```python
# core/utils/config_validator.py
from typing import Dict, Any, List
import yaml

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.required_fields = {
            "custom_api": ["base_url", "api_key"],
            "custom_tool": ["api_endpoint", "api_key"],
            "LLM": {
                "custom_llm": ["api_key", "base_url", "model"]
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """验证配置"""
        errors = []
        
        # 验证自定义API配置
        if config.get("custom_api", {}).get("enabled"):
            errors.extend(self._validate_section(config, "custom_api"))
        
        # 验证自定义工具配置
        if config.get("custom_tool", {}).get("enabled"):
            errors.extend(self._validate_section(config, "custom_tool"))
        
        # 验证LLM配置
        selected_llm = config.get("selected_module", {}).get("LLM")
        if selected_llm and selected_llm in self.required_fields["LLM"]:
            errors.extend(self._validate_llm_config(config, selected_llm))
        
        return errors
    
    def _validate_section(self, config: Dict, section: str) -> List[str]:
        """验证配置节"""
        errors = []
        section_config = config.get(section, {})
        required_fields = self.required_fields.get(section, [])
        
        for field in required_fields:
            if not section_config.get(field):
                errors.append(f"{section}.{field} 是必需的")
        
        return errors
    
    def _validate_llm_config(self, config: Dict, llm_name: str) -> List[str]:
        """验证LLM配置"""
        errors = []
        llm_config = config.get("LLM", {}).get(llm_name, {})
        required_fields = self.required_fields["LLM"].get(llm_name, [])
        
        for field in required_fields:
            if not llm_config.get(field):
                errors.append(f"LLM.{llm_name}.{field} 是必需的")
        
        return errors
```

## 测试扩展

### 1. 单元测试

```python
# test/test_custom_llm.py
import pytest
from unittest.mock import Mock, patch
from core.providers.llm.custom_llm import CustomLLM

class TestCustomLLM:
    """自定义LLM测试"""
    
    def setup_method(self):
        self.config = {
            "api_key": "test_key",
            "base_url": "https://test-api.com",
            "model": "test-model"
        }
        self.llm = CustomLLM(self.config)
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """测试初始化成功"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            await self.llm.initialize()
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self):
        """测试初始化失败"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 500
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ConnectionError):
                await self.llm.initialize()
    
    @pytest.mark.asyncio
    async def test_chat_success(self):
        """测试聊天成功"""
        messages = [{"role": "user", "content": "Hello"}]
        expected_response = "Hello, how can I help you?"
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = Mock(return_value={
                "choices": [{"message": {"content": expected_response}}]
            })
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await self.llm.chat(messages)
            assert result == expected_response
```

### 2. 集成测试

```python
# test/test_custom_integration.py
import pytest
from core.providers.tools.custom_tool.custom_executor import CustomToolExecutor
from core.api.custom_handler import CustomAPIHandler

class TestCustomIntegration:
    """自定义功能集成测试"""
    
    @pytest.fixture
    def tool_executor(self):
        config = {
            "api_endpoint": "https://test-tool.com",
            "api_key": "test_key"
        }
        return CustomToolExecutor(config)
    
    @pytest.fixture
    def api_handler(self):
        config = {
            "custom_api": {
                "base_url": "https://test-api.com",
                "api_key": "test_key"
            }
        }
        return CustomAPIHandler(config)
    
    @pytest.mark.asyncio
    async def test_custom_tool_execution(self, tool_executor):
        """测试自定义工具执行"""
        params = {
            "action": "custom_action",
            "data": "test_data"
        }
        
        result = await tool_executor.execute(params)
        
        assert result["success"] is True
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_custom_api_handler(self, api_handler):
        """测试自定义API处理器"""
        # 模拟请求对象
        mock_request = Mock()
        mock_request.path = "/custom/data"
        mock_request.method = "GET"
        mock_request.query = {"keyword": "test"}
        
        result = await api_handler.handle_get(mock_request)
        
        assert result["success"] is True
        assert "data" in result
```

## 部署扩展

### 1. Docker配置

```dockerfile
# Dockerfile.custom
FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制自定义代码
COPY core/providers/llm/custom_llm.py /app/core/providers/llm/
COPY core/providers/tools/custom_tool/ /app/core/providers/tools/custom_tool/
COPY core/api/custom_handler.py /app/core/api/
COPY plugins_func/functions/custom_plugin.py /app/plugins_func/functions/

# 复制配置文件
COPY config.yaml /app/

EXPOSE 8000 8003

CMD ["python", "app.py"]
```

### 2. 环境变量配置

```bash
# .env.custom
CUSTOM_API_KEY=your_custom_api_key
CUSTOM_TOOL_API_KEY=your_tool_api_key
CUSTOM_LLM_API_KEY=your_llm_api_key
CUSTOM_API_BASE_URL=https://api.custom.com
CUSTOM_TOOL_ENDPOINT=https://tool.custom.com
```

## 总结

扩展功能开发应遵循以下原则：

1. **模块化设计**: 每个扩展功能独立成模块，避免修改核心代码
2. **接口标准化**: 遵循统一的接口规范，便于集成和维护
3. **配置驱动**: 通过配置文件控制功能的启用和参数设置
4. **完整测试**: 编写单元测试和集成测试，确保功能稳定性
5. **文档完善**: 提供详细的开发文档和使用说明

通过这种方式，可以安全地为小智ESP32服务器添加新功能，同时保持系统的稳定性和可维护性。 