# 小智ESP32服务器开发指南

## 项目概述

小智ESP32服务器是一个基于人机共生智能理论的智能终端软硬件体系，为开源智能硬件项目提供后端服务。项目采用微服务架构，包含以下主要组件：

- **Python后端服务** (`xiaozhi-server`): 核心AI服务，处理语音识别、大模型对话、语音合成等
- **Java管理API** (`manager-api`): 提供设备管理、用户管理、配置管理等RESTful API
- **Vue管理界面** (`manager-web`): 基于Vue.js的Web管理控制台

## 技术栈

### 后端技术栈
- **Python**: 3.8+ (核心AI服务)
- **Java**: 8+ (管理API)
- **Spring Boot**: 2.x (Java框架)
- **WebSocket**: 实时通信
- **Redis**: 缓存和会话管理
- **MySQL**: 数据持久化

### 前端技术栈
- **Vue.js**: 2.6+ (前端框架)
- **Element UI**: UI组件库
- **Vue Router**: 路由管理
- **Vuex**: 状态管理
- **Axios**: HTTP客户端

## 项目架构

```
esp32-server/
├── main/
│   ├── xiaozhi-server/          # Python核心服务
│   │   ├── app.py               # 主入口
│   │   ├── config/              # 配置管理
│   │   ├── core/                # 核心模块
│   │   │   ├── providers/       # AI服务提供商
│   │   │   ├── handle/          # 消息处理
│   │   │   ├── api/             # API接口
│   │   │   └── utils/           # 工具类
│   │   └── plugins_func/        # 插件系统
│   ├── manager-api/             # Java管理API
│   │   └── src/main/java/xiaozhi/
│   │       ├── modules/         # 业务模块
│   │       ├── common/          # 公共组件
│   │       └── AdminApplication.java
│   └── manager-web/             # Vue管理界面
│       ├── src/
│       │   ├── components/      # Vue组件
│       │   ├── views/           # 页面视图
│       │   ├── apis/            # API调用
│       │   └── store/           # 状态管理
│       └── public/
└── docs/                        # 文档目录
```

## 开发环境搭建

### 1. Python环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
cd main/xiaozhi-server
pip install -r requirements.txt
```

### 2. Java环境配置

```bash
# 确保Java 8+已安装
java -version

# 编译项目
cd main/manager-api
mvn clean install
```

### 3. Node.js环境配置

```bash
# 安装Node.js 14+
node --version

# 安装依赖
cd main/manager-web
npm install
```

## 开发规范

### 1. 代码风格

#### Python代码规范
- 遵循PEP 8规范
- 使用类型注解
- 函数和类必须有文档字符串
- 使用异步编程模式

```python
from typing import Dict, Optional, List
import asyncio

class ExampleService:
    """示例服务类"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    async def process_data(self, data: str) -> Optional[str]:
        """
        处理数据
        
        Args:
            data: 输入数据
            
        Returns:
            处理结果
        """
        # 实现逻辑
        pass
```

#### Java代码规范
- 遵循阿里巴巴Java开发手册
- 使用Lombok简化代码
- 统一异常处理
- 使用Swagger注解

```java
@RestController
@RequestMapping("/api/v1/example")
@Slf4j
public class ExampleController {
    
    @Autowired
    private ExampleService exampleService;
    
    @GetMapping("/{id}")
    @ApiOperation("获取示例数据")
    public ResponseEntity<Result<ExampleDTO>> getExample(@PathVariable Long id) {
        try {
            ExampleDTO result = exampleService.getById(id);
            return ResponseEntity.ok(Result.success(result));
        } catch (Exception e) {
            log.error("获取示例数据失败", e);
            return ResponseEntity.ok(Result.error("获取失败"));
        }
    }
}
```

#### Vue代码规范
- 使用ESLint和Prettier
- 组件命名使用PascalCase
- 方法命名使用camelCase
- 使用Vuex管理状态

```vue
<template>
  <div class="example-component">
    <el-button @click="handleClick">点击</el-button>
  </div>
</template>

<script>
export default {
  name: 'ExampleComponent',
  data() {
    return {
      loading: false
    }
  },
  methods: {
    async handleClick() {
      this.loading = true
      try {
        await this.$api.example.getData()
      } catch (error) {
        this.$message.error('操作失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
```

### 2. 提交规范

使用Conventional Commits规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 3. 分支管理

- `main`: 主分支，用于生产环境
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 热修复分支
- `release/*`: 发布分支

## 扩展开发指南

### 1. 添加新的AI服务提供商

#### 步骤1: 创建提供商类

在 `main/xiaozhi-server/core/providers/` 对应目录下创建新的提供商：

```python
# core/providers/llm/example_llm.py
from core.providers.llm.base import BaseLLM
from typing import Dict, Optional

class ExampleLLM(BaseLLM):
    """示例LLM提供商"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
    
    async def chat(self, messages: list, **kwargs) -> str:
        """实现聊天功能"""
        # 实现具体的API调用逻辑
        pass
    
    async def stream_chat(self, messages: list, **kwargs):
        """实现流式聊天功能"""
        # 实现流式API调用逻辑
        pass
```

#### 步骤2: 注册提供商

在配置文件中添加新提供商：

```yaml
# config.yaml
LLM:
  example_llm:
    api_key: "your_api_key"
    base_url: "https://api.example.com"
    model: "example-model"
    max_tokens: 2048
```

#### 步骤3: 更新选择配置

```yaml
selected_module:
  LLM: "example_llm"
```

### 2. 添加新的插件功能

#### 步骤1: 创建插件文件

在 `main/xiaozhi-server/plugins_func/functions/` 目录下创建插件：

```python
# plugins_func/functions/example_plugin.py
import requests
from typing import Dict, Any

def get_weather(city: str) -> Dict[str, Any]:
    """
    获取天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息字典
    """
    try:
        # 调用天气API
        response = requests.get(f"https://api.weather.com/{city}")
        data = response.json()
        
        return {
            "success": True,
            "data": {
                "city": city,
                "temperature": data.get("temp"),
                "weather": data.get("weather")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

#### 步骤2: 注册插件

在 `plugins_func/register.py` 中注册插件：

```python
# plugins_func/register.py
from .functions.example_plugin import get_weather

PLUGIN_FUNCTIONS = {
    "get_weather": {
        "function": get_weather,
        "description": "获取指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    }
}
```

### 3. 添加新的API接口

#### Java API接口

```java
// modules/example/controller/ExampleController.java
@RestController
@RequestMapping("/api/v1/example")
@Api(tags = "示例管理")
public class ExampleController {
    
    @Autowired
    private ExampleService exampleService;
    
    @PostMapping
    @ApiOperation("创建示例")
    public ResponseEntity<Result<ExampleDTO>> create(@RequestBody @Valid ExampleCreateRequest request) {
        ExampleDTO result = exampleService.create(request);
        return ResponseEntity.ok(Result.success(result));
    }
    
    @GetMapping("/{id}")
    @ApiOperation("获取示例详情")
    public ResponseEntity<Result<ExampleDTO>> getById(@PathVariable Long id) {
        ExampleDTO result = exampleService.getById(id);
        return ResponseEntity.ok(Result.success(result));
    }
}
```

#### Python API接口

```python
# core/api/example_handler.py
from core.api.base_handler import BaseHandler
from core.utils.response import success_response, error_response

class ExampleHandler(BaseHandler):
    """示例API处理器"""
    
    async def handle_get(self, request):
        """处理GET请求"""
        try:
            # 实现业务逻辑
            data = {"message": "Hello World"}
            return success_response(data)
        except Exception as e:
            return error_response(str(e))
    
    async def handle_post(self, request):
        """处理POST请求"""
        try:
            body = await request.json()
            # 处理请求数据
            result = {"processed": body}
            return success_response(result)
        except Exception as e:
            return error_response(str(e))
```

### 4. 添加新的前端页面

#### 步骤1: 创建Vue组件

```vue
<!-- src/views/ExampleManagement.vue -->
<template>
  <div class="example-management">
    <el-card>
      <div slot="header">
        <span>示例管理</span>
        <el-button style="float: right; padding: 3px 0" type="text" @click="handleAdd">
          添加
        </el-button>
      </div>
      
      <el-table :data="tableData" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="名称"></el-table-column>
        <el-table-column prop="createTime" label="创建时间"></el-table-column>
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { getExampleList, deleteExample } from '@/apis/module/example'

export default {
  name: 'ExampleManagement',
  data() {
    return {
      loading: false,
      tableData: []
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const response = await getExampleList()
        this.tableData = response.data
      } catch (error) {
        this.$message.error('加载数据失败')
      } finally {
        this.loading = false
      }
    },
    
    handleAdd() {
      // 实现添加逻辑
    },
    
    handleEdit(row) {
      // 实现编辑逻辑
    },
    
    async handleDelete(row) {
      try {
        await this.$confirm('确认删除?', '提示', {
          type: 'warning'
        })
        await deleteExample(row.id)
        this.$message.success('删除成功')
        this.loadData()
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    }
  }
}
</script>
```

#### 步骤2: 添加路由

```javascript
// src/router/index.js
import ExampleManagement from '@/views/ExampleManagement.vue'

const routes = [
  {
    path: '/example',
    name: 'ExampleManagement',
    component: ExampleManagement,
    meta: {
      title: '示例管理',
      requiresAuth: true
    }
  }
]
```

#### 步骤3: 添加API调用

```javascript
// src/apis/module/example.js
import request from '@/apis/httpRequest'

export function getExampleList(params) {
  return request({
    url: '/api/v1/example',
    method: 'get',
    params
  })
}

export function createExample(data) {
  return request({
    url: '/api/v1/example',
    method: 'post',
    data
  })
}

export function updateExample(id, data) {
  return request({
    url: `/api/v1/example/${id}`,
    method: 'put',
    data
  })
}

export function deleteExample(id) {
  return request({
    url: `/api/v1/example/${id}`,
    method: 'delete'
  })
}
```

## 测试指南

### 1. 单元测试

#### Python测试

```python
# test/test_example.py
import pytest
from unittest.mock import Mock, patch
from core.providers.llm.example_llm import ExampleLLM

class TestExampleLLM:
    def setup_method(self):
        self.config = {
            "api_key": "test_key",
            "base_url": "https://api.test.com"
        }
        self.llm = ExampleLLM(self.config)
    
    @pytest.mark.asyncio
    async def test_chat(self):
        # 测试聊天功能
        messages = [{"role": "user", "content": "Hello"}]
        result = await self.llm.chat(messages)
        assert result is not None
```

#### Java测试

```java
// src/test/java/xiaozhi/modules/example/ExampleServiceTest.java
@SpringBootTest
class ExampleServiceTest {
    
    @Autowired
    private ExampleService exampleService;
    
    @Test
    void testCreate() {
        ExampleCreateRequest request = new ExampleCreateRequest();
        request.setName("测试");
        
        ExampleDTO result = exampleService.create(request);
        
        assertNotNull(result);
        assertEquals("测试", result.getName());
    }
}
```

### 2. 集成测试

```python
# test/integration/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_example_api():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/example")
        assert response.status_code == 200
```

## 部署指南

### 1. 开发环境部署

```bash
# 启动Python服务
cd main/xiaozhi-server
python app.py

# 启动Java服务
cd main/manager-api
mvn spring-boot:run

# 启动Vue服务
cd main/manager-web
npm run serve
```

### 2. 生产环境部署

使用Docker Compose进行容器化部署：

```yaml
# docker-compose.yml
version: '3.8'
services:
  xiaozhi-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    volumes:
      - ./data:/app/data
    depends_on:
      - redis
      - mysql
  
  manager-api:
    build: ./main/manager-api
    ports:
      - "8002:8002"
    environment:
      - SPRING_PROFILES_ACTIVE=production
    depends_on:
      - mysql
  
  manager-web:
    build: ./main/manager-web
    ports:
      - "80:80"
    depends_on:
      - manager-api
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: xiaozhi
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## 性能优化

### 1. Python服务优化

- 使用异步编程模式
- 实现连接池
- 使用缓存机制
- 优化数据库查询

### 2. Java服务优化

- 使用连接池
- 实现缓存策略
- 优化SQL查询
- 使用异步处理

### 3. 前端优化

- 代码分割
- 懒加载
- 图片压缩
- CDN加速

## 监控和日志

### 1. 日志配置

```python
# config/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    return logger
```

### 2. 监控指标

- 请求响应时间
- 错误率
- 系统资源使用率
- 业务指标

## 安全考虑

### 1. 认证和授权

- 使用JWT进行身份认证
- 实现基于角色的访问控制
- 定期更新密钥

### 2. 数据安全

- 敏感数据加密存储
- 使用HTTPS传输
- 实现数据备份

### 3. 输入验证

- 参数验证
- SQL注入防护
- XSS防护

## 常见问题

### 1. 开发环境问题

**Q: Python服务启动失败**
A: 检查依赖是否安装完整，配置文件是否正确

**Q: Java服务无法连接数据库**
A: 检查数据库配置，确保数据库服务正常运行

**Q: Vue页面无法访问API**
A: 检查API地址配置，确保跨域设置正确

### 2. 生产环境问题

**Q: 服务性能问题**
A: 检查系统资源使用情况，优化配置参数

**Q: 内存泄漏**
A: 使用监控工具分析内存使用情况，及时释放资源

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request
5. 等待代码审查

## 联系方式

- 项目地址: https://github.com/xinnan-tech/xiaozhi-esp32-server
- 问题反馈: https://github.com/xinnan-tech/xiaozhi-esp32-server/issues
- 文档地址: https://github.com/xinnan-tech/xiaozhi-esp32-server/docs 