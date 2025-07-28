# 插件系统开发指南

## 概述

小智ESP32服务器的插件系统提供了灵活的扩展机制，允许开发者在不修改核心代码的情况下添加新功能。插件系统支持热加载，可以动态注册和执行插件功能。

## 插件系统架构

### 1. 插件目录结构

```
plugins_func/
├── functions/              # 插件函数目录
│   ├── weather_plugin.py   # 天气插件
│   ├── news_plugin.py      # 新闻插件
│   ├── music_plugin.py     # 音乐插件
│   └── iot_plugin.py       # IoT控制插件
├── loadplugins.py          # 插件加载器
└── register.py             # 插件注册器
```

### 2. 插件加载流程

```python
# 插件加载流程
1. 扫描functions目录
2. 动态导入插件模块
3. 解析插件函数和元数据
4. 注册到插件管理器
5. 提供API接口调用
```

## 插件开发规范

### 1. 插件函数规范

```python
# plugins_func/functions/example_plugin.py
import requests
from typing import Dict, Any, Optional

def get_weather(city: str, country: str = "CN") -> Dict[str, Any]:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称
        country: 国家代码，默认为CN
        
    Returns:
        包含天气信息的字典
        
    Example:
        >>> get_weather("北京")
        {
            "success": True,
            "data": {
                "city": "北京",
                "temperature": 25,
                "weather": "晴天",
                "humidity": 60
            }
        }
    """
    try:
        # 实现天气查询逻辑
        response = requests.get(f"https://api.weather.com/{city}")
        data = response.json()
        
        return {
            "success": True,
            "data": {
                "city": city,
                "temperature": data.get("temp"),
                "weather": data.get("weather"),
                "humidity": data.get("humidity")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取天气信息失败"
        }

def get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """
    获取天气预报
    
    Args:
        city: 城市名称
        days: 预报天数，默认3天
        
    Returns:
        天气预报信息
    """
    # 实现天气预报逻辑
    pass
```

### 2. 插件元数据规范

```python
# 插件函数必须包含以下元数据：
# 1. 函数文档字符串（docstring）
# 2. 类型注解
# 3. 返回值格式统一

# 返回值格式规范：
{
    "success": bool,           # 执行是否成功
    "data": Any,              # 成功时的数据
    "error": str,             # 失败时的错误信息
    "message": str            # 用户友好的消息
}
```

## 插件开发示例

### 1. 天气插件

```python
# plugins_func/functions/weather_plugin.py
import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

class WeatherAPI:
    """天气API封装类"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1"
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """获取当前天气"""
        url = f"{self.base_url}/current.json"
        params = {
            'key': self.api_key,
            'q': city,
            'lang': 'zh'
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    def get_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """获取天气预报"""
        url = f"{self.base_url}/forecast.json"
        params = {
            'key': self.api_key,
            'q': city,
            'days': days,
            'lang': 'zh'
        }
        
        response = requests.get(url, params=params)
        return response.json()

# 全局API实例
weather_api = WeatherAPI("your_api_key")

def get_weather(city: str) -> Dict[str, Any]:
    """
    获取指定城市的当前天气信息
    
    Args:
        city: 城市名称，如"北京"、"上海"
        
    Returns:
        天气信息字典
    """
    try:
        data = weather_api.get_current_weather(city)
        
        if data.get('error'):
            return {
                "success": False,
                "error": data['error']['message'],
                "message": "获取天气信息失败"
            }
        
        current = data['current']
        location = data['location']
        
        return {
            "success": True,
            "data": {
                "city": location['name'],
                "region": location['region'],
                "country": location['country'],
                "temperature": current['temp_c'],
                "feels_like": current['feelslike_c'],
                "weather": current['condition']['text'],
                "humidity": current['humidity'],
                "wind_speed": current['wind_kph'],
                "wind_direction": current['wind_dir'],
                "pressure": current['pressure_mb'],
                "visibility": current['vis_km'],
                "uv": current['uv'],
                "last_updated": current['last_updated']
            },
            "message": f"获取{city}天气信息成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取天气信息时发生错误"
        }

def get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """
    获取指定城市的天气预报
    
    Args:
        city: 城市名称
        days: 预报天数，1-7天
        
    Returns:
        天气预报信息
    """
    try:
        if days < 1 or days > 7:
            return {
                "success": False,
                "error": "预报天数必须在1-7天之间",
                "message": "参数错误"
            }
        
        data = weather_api.get_forecast(city, days)
        
        if data.get('error'):
            return {
                "success": False,
                "error": data['error']['message'],
                "message": "获取天气预报失败"
            }
        
        forecast_days = []
        for day in data['forecast']['forecastday']:
            forecast_days.append({
                "date": day['date'],
                "max_temp": day['day']['maxtemp_c'],
                "min_temp": day['day']['mintemp_c'],
                "avg_temp": day['day']['avgtemp_c'],
                "weather": day['day']['condition']['text'],
                "humidity": day['day']['avghumidity'],
                "chance_of_rain": day['day']['daily_chance_of_rain'],
                "sunrise": day['astro']['sunrise'],
                "sunset": day['astro']['sunset']
            })
        
        return {
            "success": True,
            "data": {
                "city": data['location']['name'],
                "forecast_days": forecast_days
            },
            "message": f"获取{city}未来{days}天天气预报成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取天气预报时发生错误"
        }
```

### 2. 新闻插件

```python
# plugins_func/functions/news_plugin.py
import requests
from typing import Dict, Any, List
from datetime import datetime

def get_news(category: str = "general", count: int = 5) -> Dict[str, Any]:
    """
    获取新闻信息
    
    Args:
        category: 新闻类别，如"general"、"technology"、"sports"
        count: 获取新闻数量，默认5条
        
    Returns:
        新闻信息列表
    """
    try:
        # 使用新闻API
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'country': 'cn',
            'category': category,
            'pageSize': count,
            'apiKey': 'your_news_api_key'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') != 'ok':
            return {
                "success": False,
                "error": data.get('message', '获取新闻失败'),
                "message": "获取新闻信息失败"
            }
        
        news_list = []
        for article in data['articles']:
            news_list.append({
                "title": article['title'],
                "description": article['description'],
                "url": article['url'],
                "published_at": article['publishedAt'],
                "source": article['source']['name']
            })
        
        return {
            "success": True,
            "data": {
                "category": category,
                "count": len(news_list),
                "news": news_list
            },
            "message": f"获取{category}类别新闻成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取新闻信息时发生错误"
        }

def search_news(keyword: str, count: int = 5) -> Dict[str, Any]:
    """
    搜索新闻
    
    Args:
        keyword: 搜索关键词
        count: 返回结果数量
        
    Returns:
        搜索结果
    """
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': keyword,
            'language': 'zh',
            'sortBy': 'publishedAt',
            'pageSize': count,
            'apiKey': 'your_news_api_key'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('status') != 'ok':
            return {
                "success": False,
                "error": data.get('message', '搜索新闻失败'),
                "message": "搜索新闻失败"
            }
        
        news_list = []
        for article in data['articles']:
            news_list.append({
                "title": article['title'],
                "description": article['description'],
                "url": article['url'],
                "published_at": article['publishedAt'],
                "source": article['source']['name']
            })
        
        return {
            "success": True,
            "data": {
                "keyword": keyword,
                "count": len(news_list),
                "news": news_list
            },
            "message": f"搜索关键词'{keyword}'的新闻成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "搜索新闻时发生错误"
        }
```

### 3. IoT控制插件

```python
# plugins_func/functions/iot_plugin.py
import requests
import json
from typing import Dict, Any, List

class IoTController:
    """IoT设备控制器"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """获取设备列表"""
        response = requests.get(f"{self.base_url}/devices", headers=self.headers)
        return response.json()
    
    def control_device(self, device_id: str, action: str, params: Dict = None) -> Dict[str, Any]:
        """控制设备"""
        data = {
            "action": action,
            "params": params or {}
        }
        response = requests.post(
            f"{self.base_url}/devices/{device_id}/control",
            headers=self.headers,
            json=data
        )
        return response.json()

# 全局IoT控制器实例
iot_controller = IoTController("https://your-iot-api.com", "your_api_key")

def get_device_list() -> Dict[str, Any]:
    """
    获取IoT设备列表
    
    Returns:
        设备列表信息
    """
    try:
        devices = iot_controller.get_devices()
        
        return {
            "success": True,
            "data": {
                "devices": devices,
                "count": len(devices)
            },
            "message": "获取设备列表成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "获取设备列表失败"
        }

def control_device(device_id: str, action: str, **kwargs) -> Dict[str, Any]:
    """
    控制IoT设备
    
    Args:
        device_id: 设备ID
        action: 控制动作，如"turn_on"、"turn_off"、"set_brightness"
        **kwargs: 其他参数
        
    Returns:
        控制结果
    """
    try:
        result = iot_controller.control_device(device_id, action, kwargs)
        
        return {
            "success": True,
            "data": result,
            "message": f"设备{device_id}执行{action}操作成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"控制设备{device_id}失败"
        }

def turn_on_light(device_id: str) -> Dict[str, Any]:
    """
    打开灯光
    
    Args:
        device_id: 灯光设备ID
        
    Returns:
        操作结果
    """
    return control_device(device_id, "turn_on")

def turn_off_light(device_id: str) -> Dict[str, Any]:
    """
    关闭灯光
    
    Args:
        device_id: 灯光设备ID
        
    Returns:
        操作结果
    """
    return control_device(device_id, "turn_off")

def set_light_brightness(device_id: str, brightness: int) -> Dict[str, Any]:
    """
    设置灯光亮度
    
    Args:
        device_id: 灯光设备ID
        brightness: 亮度值(0-100)
        
    Returns:
        操作结果
    """
    if brightness < 0 or brightness > 100:
        return {
            "success": False,
            "error": "亮度值必须在0-100之间",
            "message": "参数错误"
        }
    
    return control_device(device_id, "set_brightness", brightness=brightness)
```

## 插件注册和管理

### 1. 插件注册器

```python
# plugins_func/register.py
from typing import Dict, Any, Callable
import inspect

class PluginRegistry:
    """插件注册器"""
    
    def __init__(self):
        self.plugins = {}
        self.functions = {}
    
    def register_function(self, func: Callable, module_name: str = None):
        """注册插件函数"""
        func_name = func.__name__
        
        # 解析函数文档
        doc = func.__doc__ or ""
        signature = inspect.signature(func)
        
        # 构建函数元数据
        metadata = {
            "function": func,
            "module": module_name or func.__module__,
            "doc": doc,
            "signature": str(signature),
            "parameters": list(signature.parameters.keys())
        }
        
        self.functions[func_name] = metadata
        print(f"注册插件函数: {func_name}")
    
    def get_function(self, name: str) -> Callable:
        """获取插件函数"""
        if name in self.functions:
            return self.functions[name]["function"]
        return None
    
    def list_functions(self) -> List[str]:
        """列出所有插件函数"""
        return list(self.functions.keys())
    
    def get_function_info(self, name: str) -> Dict[str, Any]:
        """获取函数信息"""
        return self.functions.get(name, {})

# 全局插件注册器
plugin_registry = PluginRegistry()

def register_plugin_functions():
    """注册所有插件函数"""
    import os
    import importlib
    
    functions_dir = os.path.dirname(__file__) + "/functions"
    
    for filename in os.listdir(functions_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"plugins_func.functions.{module_name}")
                
                # 注册模块中的所有函数
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, '__doc__') and not attr_name.startswith('_'):
                        plugin_registry.register_function(attr, module_name)
                        
            except Exception as e:
                print(f"加载插件模块 {module_name} 失败: {e}")

# 自动注册插件函数
register_plugin_functions()
```

### 2. 插件管理器

```python
# core/providers/tools/plugin_executor.py
from typing import Dict, Any
import asyncio
from plugins_func.register import plugin_registry

class PluginExecutor:
    """插件执行器"""
    
    def __init__(self):
        self.registry = plugin_registry
    
    async def execute_plugin(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """执行插件函数"""
        try:
            func = self.registry.get_function(plugin_name)
            if not func:
                return {
                    "success": False,
                    "error": f"插件函数 {plugin_name} 不存在",
                    "message": "插件未找到"
                }
            
            # 执行插件函数
            if asyncio.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"执行插件 {plugin_name} 时发生错误"
            }
    
    def list_plugins(self) -> Dict[str, Any]:
        """列出所有可用插件"""
        plugins = {}
        for func_name in self.registry.list_functions():
            info = self.registry.get_function_info(func_name)
            plugins[func_name] = {
                "module": info.get("module"),
                "doc": info.get("doc"),
                "parameters": info.get("parameters", [])
            }
        
        return {
            "success": True,
            "data": {
                "plugins": plugins,
                "count": len(plugins)
            },
            "message": "获取插件列表成功"
        }
    
    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件信息"""
        info = self.registry.get_function_info(plugin_name)
        if not info:
            return {
                "success": False,
                "error": f"插件 {plugin_name} 不存在",
                "message": "插件未找到"
            }
        
        return {
            "success": True,
            "data": info,
            "message": "获取插件信息成功"
        }
```

## 插件调用示例

### 1. 通过API调用插件

```python
# 在对话系统中调用插件
async def handle_user_request(user_input: str):
    """处理用户请求"""
    
    # 1. 意图识别
    intent = await intent_recognizer.recognize(user_input)
    
    # 2. 根据意图调用相应插件
    if intent == "get_weather":
        # 提取城市信息
        city = extract_city_from_input(user_input)
        result = await plugin_executor.execute_plugin("get_weather", city=city)
        
    elif intent == "control_device":
        # 提取设备控制信息
        device_id, action = extract_device_info(user_input)
        result = await plugin_executor.execute_plugin("control_device", 
                                                    device_id=device_id, 
                                                    action=action)
    
    # 3. 处理插件结果
    if result["success"]:
        response = format_plugin_response(result["data"])
    else:
        response = f"抱歉，{result['message']}"
    
    return response
```

### 2. 插件热加载

```python
# 支持插件热加载
import importlib
import os

def reload_plugins():
    """重新加载插件"""
    # 清除已注册的插件
    plugin_registry.functions.clear()
    
    # 重新注册插件
    register_plugin_functions()
    
    return {
        "success": True,
        "message": "插件重新加载成功"
    }

def add_new_plugin(plugin_file: str):
    """添加新插件"""
    try:
        # 复制插件文件到functions目录
        import shutil
        functions_dir = "plugins_func/functions"
        shutil.copy(plugin_file, functions_dir)
        
        # 重新加载插件
        reload_plugins()
        
        return {
            "success": True,
            "message": "新插件添加成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "添加插件失败"
        }
```

## 插件开发最佳实践

### 1. 错误处理

```python
def robust_plugin_function(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    健壮的插件函数示例
    
    Args:
        param1: 必需参数
        param2: 可选参数，默认值10
        
    Returns:
        执行结果
    """
    try:
        # 参数验证
        if not param1:
            return {
                "success": False,
                "error": "param1不能为空",
                "message": "参数错误"
            }
        
        if param2 < 0 or param2 > 100:
            return {
                "success": False,
                "error": "param2必须在0-100之间",
                "message": "参数范围错误"
            }
        
        # 业务逻辑
        result = process_business_logic(param1, param2)
        
        return {
            "success": True,
            "data": result,
            "message": "操作成功"
        }
        
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"网络请求失败: {str(e)}",
            "message": "网络连接错误"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": f"数据格式错误: {str(e)}",
            "message": "数据格式不正确"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未知错误: {str(e)}",
            "message": "操作失败"
        }
```

### 2. 配置管理

```python
# plugins_func/config.py
import os
import json
from typing import Dict, Any

class PluginConfig:
    """插件配置管理"""
    
    def __init__(self):
        self.config_file = "plugins_func/config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        self.save_config()

# 全局配置实例
plugin_config = PluginConfig()

# 在插件中使用配置
def get_weather_with_config(city: str) -> Dict[str, Any]:
    """使用配置的天气插件"""
    api_key = plugin_config.get("weather_api_key")
    if not api_key:
        return {
            "success": False,
            "error": "未配置天气API密钥",
            "message": "请先配置API密钥"
        }
    
    # 使用配置的API密钥
    return get_weather(city, api_key)
```

### 3. 日志记录

```python
import logging
from typing import Dict, Any

# 配置插件日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/plugins.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('plugins')

def logged_plugin_function(param: str) -> Dict[str, Any]:
    """
    带日志记录的插件函数
    
    Args:
        param: 输入参数
        
    Returns:
        执行结果
    """
    logger.info(f"开始执行插件函数，参数: {param}")
    
    try:
        # 业务逻辑
        result = process_data(param)
        
        logger.info(f"插件函数执行成功，结果: {result}")
        return {
            "success": True,
            "data": result,
            "message": "操作成功"
        }
        
    except Exception as e:
        logger.error(f"插件函数执行失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "message": "操作失败"
        }
```

## 插件测试

### 1. 单元测试

```python
# test/test_plugins.py
import pytest
from unittest.mock import Mock, patch
from plugins_func.functions.weather_plugin import get_weather

class TestWeatherPlugin:
    """天气插件测试"""
    
    def test_get_weather_success(self):
        """测试成功获取天气"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                'current': {
                    'temp_c': 25,
                    'condition': {'text': '晴天'},
                    'humidity': 60
                },
                'location': {
                    'name': '北京',
                    'region': '北京',
                    'country': '中国'
                }
            }
            mock_get.return_value = mock_response
            
            result = get_weather("北京")
            
            assert result["success"] is True
            assert result["data"]["city"] == "北京"
            assert result["data"]["temperature"] == 25
    
    def test_get_weather_failure(self):
        """测试获取天气失败"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("网络错误")
            
            result = get_weather("北京")
            
            assert result["success"] is False
            assert "网络错误" in result["error"]
```

### 2. 集成测试

```python
# test/test_plugin_integration.py
import pytest
from core.providers.tools.plugin_executor import PluginExecutor

class TestPluginIntegration:
    """插件集成测试"""
    
    @pytest.fixture
    def executor(self):
        return PluginExecutor()
    
    @pytest.mark.asyncio
    async def test_weather_plugin_integration(self, executor):
        """测试天气插件集成"""
        result = await executor.execute_plugin("get_weather", city="北京")
        
        assert "success" in result
        if result["success"]:
            assert "data" in result
            assert "city" in result["data"]
    
    @pytest.mark.asyncio
    async def test_plugin_list(self, executor):
        """测试插件列表"""
        result = executor.list_plugins()
        
        assert result["success"] is True
        assert "plugins" in result["data"]
        assert isinstance(result["data"]["plugins"], dict)
```

## 总结

插件系统为小智ESP32服务器提供了强大的扩展能力，开发者可以通过简单的函数定义来添加新功能。通过规范的开发流程、完善的错误处理和测试覆盖，确保插件的稳定性和可靠性。 