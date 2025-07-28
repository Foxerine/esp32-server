# 部署和运维指南

## 概述

本指南详细说明小智ESP32服务器的部署和运维流程，包括环境准备、部署方式、监控配置、故障处理等。

## 环境要求

### 1. 系统要求

```bash
# 操作系统
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Windows 10+ (开发环境)

# 硬件要求
- CPU: 4核心以上
- 内存: 8GB以上
- 存储: 50GB以上可用空间
- 网络: 稳定的互联网连接

# 软件要求
- Python 3.8+
- Java 8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+
- Nginx 1.18+
```

### 2. 依赖安装

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y openjdk-8-jdk
sudo apt install -y nodejs npm
sudo apt install -y mysql-server redis-server nginx
sudo apt install -y ffmpeg

# CentOS/RHEL
sudo yum update -y
sudo yum install -y python3 python3-pip
sudo yum install -y java-1.8.0-openjdk
sudo yum install -y nodejs npm
sudo yum install -y mysql-server redis nginx
sudo yum install -y ffmpeg

# 安装Docker (可选)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 部署方式

### 1. 源码部署

#### 1.1 环境准备

```bash
# 创建项目目录
mkdir -p /opt/xiaozhi-server
cd /opt/xiaozhi-server

# 克隆代码
git clone https://github.com/your-repo/xiaozhi-esp32-server.git .

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

#### 1.2 数据库配置

```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 创建数据库和用户
mysql -u root -p
```

```sql
-- 创建数据库
CREATE DATABASE xiaozhi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'xiaozhi'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON xiaozhi.* TO 'xiaozhi'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

#### 1.3 Redis配置

```bash
# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis

# 配置Redis
sudo nano /etc/redis/redis.conf
```

```conf
# Redis配置
bind 127.0.0.1
port 6379
requirepass your_redis_password
maxmemory 256mb
maxmemory-policy allkeys-lru
```

#### 1.4 配置文件

```yaml
# config.yaml
server:
  host: "0.0.0.0"
  port: 8000
  websocket_port: 8003

manager-api:
  url: "http://localhost:8002/xiaozhi"
  secret: "your_secret_key"

database:
  host: "localhost"
  port: 3306
  name: "xiaozhi"
  username: "xiaozhi"
  password: "your_password"

redis:
  host: "localhost"
  port: 6379
  password: "your_redis_password"
  database: 0

# AI服务配置
LLM:
  openai:
    api_key: "your_openai_key"
    model: "gpt-3.5-turbo"

TTS:
  aliyun:
    access_key_id: "your_aliyun_key"
    access_key_secret: "your_aliyun_secret"
    app_key: "your_app_key"

ASR:
  aliyun:
    access_key_id: "your_aliyun_key"
    access_key_secret: "your_aliyun_secret"
```

#### 1.5 启动服务

```bash
# 启动Java管理API
cd main/manager-api
mvn clean package
java -jar target/manager-api.jar --spring.profiles.active=prod

# 启动Vue前端 (开发模式)
cd main/manager-web
npm install
npm run serve

# 启动Python后端服务
cd main/xiaozhi-server
python app.py
```

### 2. Docker部署

#### 2.1 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # MySQL数据库
  mysql:
    image: mysql:8.0
    container_name: xiaozhi-mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: xiaozhi
      MYSQL_USER: xiaozhi
      MYSQL_PASSWORD: xiaozhi_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    networks:
      - xiaozhi-network

  # Redis缓存
  redis:
    image: redis:6.2-alpine
    container_name: xiaozhi-redis
    command: redis-server --requirepass redis_password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - xiaozhi-network

  # Java管理API
  manager-api:
    build:
      context: ./main/manager-api
      dockerfile: Dockerfile
    container_name: xiaozhi-api
    environment:
      SPRING_PROFILES_ACTIVE: prod
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/xiaozhi
      SPRING_DATASOURCE_USERNAME: xiaozhi
      SPRING_DATASOURCE_PASSWORD: xiaozhi_password
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PASSWORD: redis_password
    ports:
      - "8002:8002"
    depends_on:
      - mysql
      - redis
    networks:
      - xiaozhi-network

  # Python后端服务
  xiaozhi-server:
    build:
      context: ./main/xiaozhi-server
      dockerfile: Dockerfile
    container_name: xiaozhi-server
    environment:
      - MANAGER_API_URL=http://manager-api:8002/xiaozhi
      - MANAGER_API_SECRET=your_secret_key
      - REDIS_HOST=redis
      - REDIS_PASSWORD=redis_password
    ports:
      - "8000:8000"
      - "8003:8003"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - manager-api
      - redis
    networks:
      - xiaozhi-network

  # Vue前端
  manager-web:
    build:
      context: ./main/manager-web
      dockerfile: Dockerfile
    container_name: xiaozhi-web
    ports:
      - "8080:80"
    depends_on:
      - manager-api
    networks:
      - xiaozhi-network

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: xiaozhi-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - manager-api
      - xiaozhi-server
      - manager-web
    networks:
      - xiaozhi-network

volumes:
  mysql_data:
  redis_data:

networks:
  xiaozhi-network:
    driver: bridge
```

#### 2.2 Nginx配置

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server manager-api:8002;
    }
    
    upstream server_backend {
        server xiaozhi-server:8000;
    }
    
    upstream web_backend {
        server manager-web:80;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # 管理API
        location /xiaozhi/api/ {
            proxy_pass http://api_backend/xiaozhi/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Python后端服务
        location /api/ {
            proxy_pass http://server_backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket
        location /ws/ {
            proxy_pass http://server_backend/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
        
        # 前端页面
        location / {
            proxy_pass http://web_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 2.3 启动Docker服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 系统服务部署

#### 3.1 创建系统服务

```bash
# Python后端服务
sudo nano /etc/systemd/system/xiaozhi-server.service
```

```ini
[Unit]
Description=Xiaozhi Python Server
After=network.target mysql.service redis.service

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/opt/xiaozhi-server/main/xiaozhi-server
Environment=PATH=/opt/xiaozhi-server/venv/bin
ExecStart=/opt/xiaozhi-server/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Java管理API服务
sudo nano /etc/systemd/system/xiaozhi-api.service
```

```ini
[Unit]
Description=Xiaozhi Java API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/opt/xiaozhi-server/main/manager-api
ExecStart=/usr/bin/java -jar target/manager-api.jar --spring.profiles.active=prod
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3.2 启动系统服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable xiaozhi-server
sudo systemctl enable xiaozhi-api

# 启动服务
sudo systemctl start xiaozhi-server
sudo systemctl start xiaozhi-api

# 查看服务状态
sudo systemctl status xiaozhi-server
sudo systemctl status xiaozhi-api

# 查看日志
sudo journalctl -u xiaozhi-server -f
sudo journalctl -u xiaozhi-api -f
```

## 监控配置

### 1. 日志管理

#### 1.1 日志配置

```python
# main/xiaozhi-server/config/logger.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """配置日志"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/xiaozhi-server.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 错误日志处理器
    error_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/xiaozhi-server-error.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger
```

#### 1.2 日志轮转

```bash
# /etc/logrotate.d/xiaozhi-server
/opt/xiaozhi-server/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 xiaozhi xiaozhi
    postrotate
        systemctl reload xiaozhi-server
    endscript
}
```

### 2. 性能监控

#### 2.1 系统监控

```python
# main/xiaozhi-server/core/utils/monitor.py
import psutil
import time
from typing import Dict, Any

class SystemMonitor:
    """系统监控"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_total": memory.total,
                "memory_used": memory.used,
                "memory_percent": memory.percent,
                "disk_total": disk.total,
                "disk_used": disk.used,
                "disk_percent": (disk.used / disk.total) * 100
            }
        except Exception as e:
            self.logger.error(f"获取系统信息失败: {e}")
            return {}
    
    def get_process_info(self) -> Dict[str, Any]:
        """获取进程信息"""
        try:
            process = psutil.Process()
            return {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
        except Exception as e:
            self.logger.error(f"获取进程信息失败: {e}")
            return {}
    
    def monitor_performance(self):
        """性能监控"""
        while True:
            try:
                system_info = self.get_system_info()
                process_info = self.get_process_info()
                
                # 记录性能指标
                self.logger.info(f"系统性能: {system_info}")
                self.logger.info(f"进程性能: {process_info}")
                
                # 检查告警条件
                if system_info.get("cpu_percent", 0) > 80:
                    self.logger.warning("CPU使用率过高")
                
                if system_info.get("memory_percent", 0) > 80:
                    self.logger.warning("内存使用率过高")
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                self.logger.error(f"性能监控失败: {e}")
                time.sleep(60)
```

#### 2.2 应用监控

```python
# main/xiaozhi-server/core/utils/metrics.py
import time
from functools import wraps
from typing import Dict, Any

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "request_time": [],
            "error_count": 0,
            "active_connections": 0
        }
    
    def record_request(self, duration: float):
        """记录请求"""
        self.metrics["request_count"] += 1
        self.metrics["request_time"].append(duration)
        
        # 保持最近1000个请求的时间
        if len(self.metrics["request_time"]) > 1000:
            self.metrics["request_time"] = self.metrics["request_time"][-1000:]
    
    def record_error(self):
        """记录错误"""
        self.metrics["error_count"] += 1
    
    def set_active_connections(self, count: int):
        """设置活跃连接数"""
        self.metrics["active_connections"] = count
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        request_times = self.metrics["request_time"]
        avg_time = sum(request_times) / len(request_times) if request_times else 0
        
        return {
            "request_count": self.metrics["request_count"],
            "error_count": self.metrics["error_count"],
            "active_connections": self.metrics["active_connections"],
            "avg_request_time": avg_time,
            "error_rate": self.metrics["error_count"] / max(self.metrics["request_count"], 1)
        }

# 全局指标收集器
metrics_collector = MetricsCollector()

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            metrics_collector.record_request(duration)
            return result
        except Exception as e:
            metrics_collector.record_error()
            raise
    return wrapper
```

### 3. 健康检查

#### 3.1 健康检查端点

```python
# main/xiaozhi-server/core/api/health_handler.py
from core.api.base_handler import BaseHandler
from core.utils.response import success_response, error_response
from core.utils.monitor import SystemMonitor
from core.utils.metrics import metrics_collector
import psutil

class HealthHandler(BaseHandler):
    """健康检查处理器"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.system_monitor = SystemMonitor()
    
    async def handle_get(self, request) -> Dict[str, Any]:
        """处理健康检查请求"""
        try:
            # 基本健康状态
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0"
            }
            
            # 系统信息
            system_info = self.system_monitor.get_system_info()
            if system_info:
                health_status["system"] = system_info
            
            # 应用指标
            app_metrics = metrics_collector.get_metrics()
            health_status["metrics"] = app_metrics
            
            # 数据库连接检查
            db_status = await self._check_database()
            health_status["database"] = db_status
            
            # Redis连接检查
            redis_status = await self._check_redis()
            health_status["redis"] = redis_status
            
            # 检查是否健康
            if not all([db_status["healthy"], redis_status["healthy"]]):
                health_status["status"] = "unhealthy"
            
            return success_response(health_status)
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return error_response("健康检查失败")
    
    async def _check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            # 这里应该实现实际的数据库连接检查
            return {
                "healthy": True,
                "message": "数据库连接正常"
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": f"数据库连接失败: {e}"
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            # 这里应该实现实际的Redis连接检查
            return {
                "healthy": True,
                "message": "Redis连接正常"
            }
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Redis连接失败: {e}"
            }
```

## 故障处理

### 1. 常见问题排查

#### 1.1 服务无法启动

```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8002
sudo netstat -tlnp | grep :8003

# 检查日志
tail -f logs/xiaozhi-server.log
tail -f logs/xiaozhi-server-error.log

# 检查配置文件
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# 检查依赖
pip list | grep -E "(fastapi|websockets|redis|mysql)"
```

#### 1.2 数据库连接问题

```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查MySQL连接
mysql -u xiaozhi -p -h localhost

# 检查数据库表
mysql -u xiaozhi -p -e "USE xiaozhi; SHOW TABLES;"

# 检查MySQL日志
sudo tail -f /var/log/mysql/error.log
```

#### 1.3 Redis连接问题

```bash
# 检查Redis服务状态
sudo systemctl status redis

# 测试Redis连接
redis-cli -a your_redis_password ping

# 检查Redis日志
sudo tail -f /var/log/redis/redis-server.log
```

### 2. 性能优化

#### 2.1 数据库优化

```sql
-- 检查慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 优化查询
EXPLAIN SELECT * FROM device WHERE device_name LIKE '%test%';

-- 添加索引
CREATE INDEX idx_device_name ON device(device_name);
CREATE INDEX idx_create_time ON device(create_time);

-- 分析表
ANALYZE TABLE device;
```

#### 2.2 应用优化

```python
# 连接池配置
# config.yaml
database:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600

redis:
  pool_size: 10
  max_connections: 20
```

#### 2.3 系统优化

```bash
# 调整系统参数
# /etc/sysctl.conf
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200

# 应用配置
sudo sysctl -p
```

### 3. 备份和恢复

#### 3.1 数据库备份

```bash
#!/bin/bash
# backup.sh

# 设置变量
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="xiaozhi"
DB_USER="xiaozhi"
DB_PASS="your_password"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/xiaozhi_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/xiaozhi_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "xiaozhi_*.sql.gz" -mtime +7 -delete

echo "备份完成: xiaozhi_$DATE.sql.gz"
```

#### 3.2 配置文件备份

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/opt/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
cp /opt/xiaozhi-server/config.yaml $BACKUP_DIR/config_$DATE.yaml
cp /opt/xiaozhi-server/data/.config.yaml $BACKUP_DIR/custom_config_$DATE.yaml

# 压缩备份
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C $BACKUP_DIR config_$DATE.yaml custom_config_$DATE.yaml

# 清理临时文件
rm $BACKUP_DIR/config_$DATE.yaml $BACKUP_DIR/custom_config_$DATE.yaml

echo "配置文件备份完成: config_$DATE.tar.gz"
```

#### 3.3 数据恢复

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_NAME="xiaozhi"
DB_USER="xiaozhi"
DB_PASS="your_password"

if [ -z "$BACKUP_FILE" ]; then
    echo "请指定备份文件"
    exit 1
fi

# 解压备份文件
gunzip $BACKUP_FILE

# 恢复数据库
mysql -u $DB_USER -p$DB_PASS $DB_NAME < ${BACKUP_FILE%.gz}

echo "数据恢复完成"
```

## 安全配置

### 1. 防火墙配置

```bash
# 配置UFW防火墙
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许SSH
sudo ufw allow ssh

# 允许Web服务端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8002/tcp
sudo ufw allow 8003/tcp

# 查看防火墙状态
sudo ufw status
```

### 2. SSL证书配置

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 安全加固

```bash
# 禁用不必要的服务
sudo systemctl disable telnet
sudo systemctl disable rsh
sudo systemctl disable rlogin

# 配置SSH安全
sudo nano /etc/ssh/sshd_config
```

```conf
# SSH安全配置
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers xiaozhi
Port 2222
```

## 总结

通过合理的部署配置、完善的监控体系和有效的故障处理机制，可以确保小智ESP32服务器的稳定运行。定期进行性能优化、安全加固和备份恢复，是保证系统可靠性的重要措施。 