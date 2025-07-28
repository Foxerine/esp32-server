# Python后端服务架构文档

## 概述

Python后端服务是小智ESP32服务器的核心组件，负责处理AI相关的所有功能，包括语音识别、大模型对话、语音合成、视觉分析等。服务采用异步架构，支持高并发处理。

## 核心架构

### 1. 服务启动流程

```python
# app.py - 主入口
async def main():
    # 1. 加载配置
    config = load_config()
    
    # 2. 启动WebSocket服务器
    ws_server = WebSocketServer(config)
    ws_task = asyncio.create_task(ws_server.start())
    
    # 3. 启动HTTP服务器
    ota_server = SimpleHttpServer(config)
    ota_task = asyncio.create_task(ota_server.start())
    
    # 4. 等待服务运行
    await asyncio.gather(ws_task, ota_task)
```

### 2. 核心模块结构

```
xiaozhi-server/
├── app.py                    # 主入口文件
├── config/                   # 配置管理
│   ├── config_loader.py      # 配置加载器
│   ├── logger.py             # 日志配置
│   └── manage_api_client.py  # 管理API客户端
├── core/                     # 核心模块
│   ├── websocket_server.py   # WebSocket服务器
│   ├── http_server.py        # HTTP服务器
│   ├── connection.py         # 连接管理
│   ├── auth.py               # 认证模块
│   ├── providers/            # AI服务提供商
│   │   ├── asr/              # 语音识别
│   │   ├── llm/              # 大语言模型
│   │   ├── tts/              # 语音合成
│   │   ├── vllm/             # 视觉大模型
│   │   ├── vad/              # 语音活动检测
│   │   ├── intent/           # 意图识别
│   │   ├── memory/           # 记忆系统
│   │   └── tools/            # 工具调用
│   ├── handle/               # 消息处理
│   ├── api/                  # API接口
│   └── utils/                # 工具类
└── plugins_func/             # 插件系统
```

## 配置管理

### 1. 配置文件结构

```yaml
# config.yaml - 默认配置
server:
  ip: "0.0.0.0"
  port: 8000
  http_port: 8003
  auth_key: ""

# AI服务配置
ASR:
  funasr:
    model_dir: "models/FunASR"
    output_dir: "tmp/asr_output"

LLM:
  openai:
    api_key: "your_api_key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-3.5-turbo"

TTS:
  aliyun:
    access_key_id: "your_access_key"
    access_key_secret: "your_secret"
    output_dir: "tmp/tts_output"

# 模块选择
selected_module:
  ASR: "funasr"
  LLM: "openai"
  TTS: "aliyun"
```

### 2. 配置加载机制

```python
# config/config_loader.py
def load_config():
    """加载配置文件"""
    # 1. 检查缓存
    cached_config = cache_manager.get(CacheType.CONFIG, "main_config")
    if cached_config is not None:
        return cached_config
    
    # 2. 加载默认配置
    default_config = read_config("config.yaml")
    
    # 3. 加载自定义配置
    custom_config = read_config("data/.config.yaml")
    
    # 4. 合并配置
    config = merge_configs(default_config, custom_config)
    
    # 5. 缓存配置
    cache_manager.set(CacheType.CONFIG, "main_config", config)
    return config
```

## WebSocket服务器

### 1. 连接管理

```python
# core/websocket_server.py
class WebSocketServer:
    def __init__(self, config):
        self.config = config
        self.connections = {}  # 连接池
        self.connection_manager = ConnectionManager()
    
    async def start(self):
        """启动WebSocket服务器"""
        server = await websockets.serve(
            self.handle_connection,
            self.config["server"]["ip"],
            self.config["server"]["port"]
        )
        await server.wait_closed()
    
    async def handle_connection(self, websocket, path):
        """处理WebSocket连接"""
        connection = Connection(websocket, self.config)
        await self.connection_manager.add_connection(connection)
        
        try:
            async for message in websocket:
                await self.handle_message(connection, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.connection_manager.remove_connection(connection)
```

### 2. 消息处理流程

```python
# core/connection.py
class Connection:
    async def handle_message(self, message):
        """处理接收到的消息"""
        try:
            # 1. 解析消息
            data = json.loads(message)
            msg_type = data.get("type")
            
            # 2. 根据消息类型分发处理
            if msg_type == "audio":
                await self.handle_audio_message(data)
            elif msg_type == "text":
                await self.handle_text_message(data)
            elif msg_type == "image":
                await self.handle_image_message(data)
            else:
                await self.send_error("Unknown message type")
                
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await self.send_error(str(e))
    
    async def handle_audio_message(self, data):
        """处理音频消息"""
        # 1. 语音识别
        text = await self.asr.recognize(data["audio"])
        
        # 2. 意图识别
        intent = await self.intent.recognize(text)
        
        # 3. 大模型对话
        response = await self.llm.chat(text, intent)
        
        # 4. 语音合成
        audio = await self.tts.synthesize(response)
        
        # 5. 返回结果
        await self.send_audio_response(audio)
```

## AI服务提供商

### 1. 提供商基类

```python
# core/providers/base.py
class BaseProvider:
    """AI服务提供商基类"""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logging()
    
    async def initialize(self):
        """初始化提供商"""
        pass
    
    async def cleanup(self):
        """清理资源"""
        pass
    
    def get_config(self, key, default=None):
        """获取配置"""
        return self.config.get(key, default)
```

### 2. 语音识别(ASR)提供商

```python
# core/providers/asr/base.py
class BaseASR(BaseProvider):
    """语音识别基类"""
    
    async def recognize(self, audio_data: bytes) -> str:
        """识别音频为文本"""
        raise NotImplementedError
    
    async def recognize_stream(self, audio_stream):
        """流式语音识别"""
        raise NotImplementedError

# core/providers/asr/funasr.py
class FunASR(BaseASR):
    """FunASR语音识别"""
    
    def __init__(self, config):
        super().__init__(config)
        self.model_dir = config.get("model_dir")
        self.model = None
    
    async def initialize(self):
        """初始化FunASR模型"""
        from funasr import AutoModel
        self.model = AutoModel(model=self.model_dir)
    
    async def recognize(self, audio_data: bytes) -> str:
        """识别音频"""
        result = self.model.generate(audio_data)
        return result[0]["text"]
```

### 3. 大语言模型(LLM)提供商

```python
# core/providers/llm/base.py
class BaseLLM(BaseProvider):
    """大语言模型基类"""
    
    async def chat(self, messages: list, **kwargs) -> str:
        """聊天对话"""
        raise NotImplementedError
    
    async def stream_chat(self, messages: list, **kwargs):
        """流式聊天"""
        raise NotImplementedError

# core/providers/llm/openai.py
class OpenAILLM(BaseLLM):
    """OpenAI大语言模型"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url")
        self.model = config.get("model", "gpt-3.5-turbo")
    
    async def chat(self, messages: list, **kwargs) -> str:
        """OpenAI聊天"""
        import openai
        
        openai.api_key = self.api_key
        openai.base_url = self.base_url
        
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            **kwargs
        )
        
        return response.choices[0].message.content
```

### 4. 语音合成(TTS)提供商

```python
# core/providers/tts/base.py
class BaseTTS(BaseProvider):
    """语音合成基类"""
    
    async def synthesize(self, text: str, **kwargs) -> bytes:
        """合成语音"""
        raise NotImplementedError
    
    async def synthesize_stream(self, text: str, **kwargs):
        """流式语音合成"""
        raise NotImplementedError

# core/providers/tts/aliyun.py
class AliyunTTS(BaseTTS):
    """阿里云语音合成"""
    
    def __init__(self, config):
        super().__init__(config)
        self.access_key_id = config.get("access_key_id")
        self.access_key_secret = config.get("access_key_secret")
        self.output_dir = config.get("output_dir")
    
    async def synthesize(self, text: str, **kwargs) -> bytes:
        """阿里云TTS合成"""
        from aliyunsdkcore.client import AcsClient
        from aliyunsdkcore.request import CommonRequest
        
        client = AcsClient(self.access_key_id, self.access_key_secret)
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateTtsTask')
        
        # 设置参数
        request.add_query_param('Text', text)
        request.add_query_param('Voice', kwargs.get('voice', 'xiaoyun'))
        
        response = client.do_action_with_exception(request)
        return response
```

## 插件系统

### 1. 插件架构

```python
# plugins_func/loadplugins.py
class PluginLoader:
    """插件加载器"""
    
    def __init__(self):
        self.plugins = {}
        self.functions = {}
    
    def load_plugins(self):
        """加载所有插件"""
        plugin_dir = "plugins_func/functions"
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py'):
                module_name = filename[:-3]
                module = importlib.import_module(f"plugins_func.functions.{module_name}")
                
                # 注册插件函数
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, '__doc__'):
                        self.functions[attr_name] = {
                            'function': attr,
                            'description': attr.__doc__,
                            'module': module_name
                        }
    
    def get_function(self, name):
        """获取插件函数"""
        return self.functions.get(name)
    
    def list_functions(self):
        """列出所有插件函数"""
        return list(self.functions.keys())
```

### 2. 插件开发示例

```python
# plugins_func/functions/weather_plugin.py
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
        url = f"https://api.weatherapi.com/v1/current.json"
        params = {
            'key': 'your_api_key',
            'q': city,
            'lang': 'zh'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            "success": True,
            "data": {
                "city": city,
                "temperature": data['current']['temp_c'],
                "weather": data['current']['condition']['text'],
                "humidity": data['current']['humidity']
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """
    获取天气预报
    
    Args:
        city: 城市名称
        days: 预报天数
        
    Returns:
        天气预报信息
    """
    # 实现天气预报逻辑
    pass
```

## 工具调用系统

### 1. 工具管理器

```python
# core/providers/tools/unified_tool_manager.py
class UnifiedToolManager:
    """统一工具管理器"""
    
    def __init__(self):
        self.tools = {}
        self.plugin_loader = PluginLoader()
    
    async def initialize(self):
        """初始化工具管理器"""
        # 加载插件
        self.plugin_loader.load_plugins()
        
        # 注册内置工具
        self.register_builtin_tools()
        
        # 注册插件工具
        self.register_plugin_tools()
    
    def register_builtin_tools(self):
        """注册内置工具"""
        # IoT工具
        self.tools['iot_control'] = IOTExecutor()
        
        # MCP工具
        self.tools['mcp_client'] = MCPClientExecutor()
        self.tools['mcp_server'] = MCPServerExecutor()
    
    def register_plugin_tools(self):
        """注册插件工具"""
        for func_name, func_info in self.plugin_loader.functions.items():
            self.tools[func_name] = PluginExecutor(func_info)
    
    async def execute_tool(self, tool_name: str, params: dict):
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tools[tool_name]
        return await tool.execute(params)
```

### 2. IoT工具执行器

```python
# core/providers/tools/device_iot/iot_executor.py
class IOTExecutor:
    """IoT工具执行器"""
    
    def __init__(self):
        self.devices = {}
    
    async def execute(self, params: dict):
        """执行IoT指令"""
        action = params.get('action')
        device_id = params.get('device_id')
        
        if action == 'turn_on':
            return await self.turn_on_device(device_id)
        elif action == 'turn_off':
            return await self.turn_off_device(device_id)
        elif action == 'get_status':
            return await self.get_device_status(device_id)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def turn_on_device(self, device_id: str):
        """打开设备"""
        # 实现设备控制逻辑
        return {"success": True, "message": f"Device {device_id} turned on"}
    
    async def turn_off_device(self, device_id: str):
        """关闭设备"""
        # 实现设备控制逻辑
        return {"success": True, "message": f"Device {device_id} turned off"}
    
    async def get_device_status(self, device_id: str):
        """获取设备状态"""
        # 实现状态查询逻辑
        return {"success": True, "status": "online"}
```

## 缓存系统

### 1. 缓存管理器

```python
# core/utils/cache/manager.py
class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.caches = {}
        self.strategies = {}
    
    def register_strategy(self, cache_type: CacheType, strategy: CacheStrategy):
        """注册缓存策略"""
        self.strategies[cache_type] = strategy
    
    def get(self, cache_type: CacheType, key: str):
        """获取缓存"""
        strategy = self.strategies.get(cache_type)
        if strategy:
            return strategy.get(key)
        return None
    
    def set(self, cache_type: CacheType, key: str, value, ttl: int = None):
        """设置缓存"""
        strategy = self.strategies.get(cache_type)
        if strategy:
            strategy.set(key, value, ttl)
    
    def delete(self, cache_type: CacheType, key: str):
        """删除缓存"""
        strategy = self.strategies.get(cache_type)
        if strategy:
            strategy.delete(key)
    
    def clear(self, cache_type: CacheType = None):
        """清空缓存"""
        if cache_type:
            strategy = self.strategies.get(cache_type)
            if strategy:
                strategy.clear()
        else:
            for strategy in self.strategies.values():
                strategy.clear()
```

### 2. 内存缓存策略

```python
# core/utils/cache/strategies.py
class MemoryCacheStrategy(CacheStrategy):
    """内存缓存策略"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str):
        """获取缓存"""
        if key in self.cache:
            # 检查是否过期
            if self._is_expired(key):
                self.delete(key)
                return None
            return self.cache[key]
        return None
    
    def set(self, key: str, value, ttl: int = None):
        """设置缓存"""
        self.cache[key] = value
        if ttl:
            self.timestamps[key] = time.time() + ttl
        else:
            self.timestamps[key] = None
    
    def delete(self, key: str):
        """删除缓存"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """检查是否过期"""
        timestamp = self.timestamps.get(key)
        if timestamp is None:
            return False
        return time.time() > timestamp
```

## 错误处理

### 1. 异常定义

```python
# core/utils/exceptions.py
class XiaozhiException(Exception):
    """小智基础异常"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

class ConfigException(XiaozhiException):
    """配置异常"""
    pass

class ProviderException(XiaozhiException):
    """提供商异常"""
    pass

class ConnectionException(XiaozhiException):
    """连接异常"""
    pass

class PluginException(XiaozhiException):
    """插件异常"""
    pass
```

### 2. 错误处理中间件

```python
# core/utils/error_handler.py
class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    async def handle_exception(func):
        """异常处理装饰器"""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except XiaozhiException as e:
                logger.error(f"Xiaozhi error: {e.message}")
                return {
                    "success": False,
                    "error": e.message,
                    "error_code": e.error_code
                }
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {
                    "success": False,
                    "error": "Internal server error",
                    "error_code": "INTERNAL_ERROR"
                }
        return wrapper
```

## 性能监控

### 1. 性能指标收集

```python
# core/utils/performance.py
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, name: str):
        """开始计时"""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str):
        """结束计时"""
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            if name not in self.metrics:
                self.metrics[name] = []
            self.metrics[name].append(duration)
            del self.start_times[name]
    
    def get_average_time(self, name: str) -> float:
        """获取平均时间"""
        if name in self.metrics and self.metrics[name]:
            return sum(self.metrics[name]) / len(self.metrics[name])
        return 0.0
    
    def get_metrics(self) -> dict:
        """获取所有指标"""
        return {
            name: {
                "count": len(times),
                "average": sum(times) / len(times),
                "min": min(times),
                "max": max(times)
            }
            for name, times in self.metrics.items()
        }
```

### 2. 性能装饰器

```python
# core/utils/performance.py
def monitor_performance(name: str):
    """性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            monitor.start_timer(name)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                monitor.end_timer(name)
        return wrapper
    return decorator
```

## 扩展开发指南

### 1. 添加新的AI提供商

1. 在对应目录创建新的提供商类
2. 继承基类并实现必要方法
3. 在配置文件中添加配置项
4. 更新模块选择配置

### 2. 添加新的插件功能

1. 在 `plugins_func/functions/` 目录创建插件文件
2. 实现插件函数并添加文档字符串
3. 插件会自动被加载和注册

### 3. 添加新的工具类型

1. 创建工具执行器类
2. 在工具管理器中注册
3. 实现具体的执行逻辑

### 4. 添加新的API接口

1. 创建API处理器类
2. 在HTTP服务器中注册路由
3. 实现具体的处理逻辑

## 最佳实践

### 1. 异步编程

- 使用 `async/await` 进行异步操作
- 避免阻塞操作
- 合理使用 `asyncio.gather` 进行并发处理

### 2. 错误处理

- 使用自定义异常类
- 统一错误处理机制
- 记录详细的错误日志

### 3. 性能优化

- 使用连接池
- 实现缓存机制
- 监控性能指标

### 4. 配置管理

- 使用环境变量
- 支持配置文件热重载
- 实现配置验证

### 5. 日志记录

- 使用结构化日志
- 设置合适的日志级别
- 实现日志轮转

## 测试策略

### 1. 单元测试

```python
# test/test_asr.py
import pytest
from unittest.mock import Mock, patch
from core.providers.asr.funasr import FunASR

class TestFunASR:
    def setup_method(self):
        self.config = {
            "model_dir": "test_models/funasr"
        }
        self.asr = FunASR(self.config)
    
    @pytest.mark.asyncio
    async def test_recognize(self):
        # 测试语音识别
        audio_data = b"test_audio_data"
        with patch('funasr.AutoModel') as mock_model:
            mock_model.return_value.generate.return_value = [{"text": "测试文本"}]
            result = await self.asr.recognize(audio_data)
            assert result == "测试文本"
```

### 2. 集成测试

```python
# test/integration/test_workflow.py
import pytest
from core.connection import Connection

class TestWorkflow:
    @pytest.mark.asyncio
    async def test_audio_workflow(self):
        # 测试完整的音频处理流程
        connection = Connection(Mock(), {})
        
        # 模拟音频消息
        audio_message = {
            "type": "audio",
            "audio": b"test_audio_data"
        }
        
        # 处理消息
        await connection.handle_message(json.dumps(audio_message))
        
        # 验证结果
        # ...
```

## 部署配置

### 1. 生产环境配置

```yaml
# production.yaml
server:
  ip: "0.0.0.0"
  port: 8000
  http_port: 8003
  auth_key: "${AUTH_KEY}"

log:
  level: "INFO"
  log_dir: "/var/log/xiaozhi"

# 使用生产环境的AI服务
selected_module:
  ASR: "funasr"
  LLM: "openai"
  TTS: "aliyun"
```

### 2. Docker配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8003

CMD ["python", "app.py"]
```

### 3. 系统服务配置

```ini
# /etc/systemd/system/xiaozhi-server.service
[Unit]
Description=Xiaozhi Python Server
After=network.target

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/opt/xiaozhi-server
ExecStart=/opt/xiaozhi-server/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 故障排查

### 1. 常见问题

**Q: 服务启动失败**
A: 检查配置文件、依赖安装、端口占用

**Q: 语音识别不工作**
A: 检查ASR模型文件、API密钥、网络连接

**Q: 大模型响应慢**
A: 检查网络连接、模型配置、并发设置

**Q: 内存使用过高**
A: 检查缓存配置、连接池设置、资源释放

### 2. 日志分析

```bash
# 查看错误日志
tail -f logs/error.log

# 查看性能日志
tail -f logs/performance.log

# 查看访问日志
tail -f logs/access.log
```

### 3. 性能调优

```python
# 调整并发设置
import asyncio

# 设置事件循环策略
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 调整连接池大小
MAX_CONNECTIONS = 1000
```

## 总结

Python后端服务是小智ESP32服务器的核心，采用模块化、插件化的架构设计，支持多种AI服务提供商，具备良好的扩展性和可维护性。通过合理的配置管理、错误处理、性能监控和测试策略，确保服务的稳定性和可靠性。 