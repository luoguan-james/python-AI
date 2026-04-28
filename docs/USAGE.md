# 使用文档

**版本**: 2.0.0
**更新日期**: 2024-06-15
**项目**: python-AI 爬虫系统

---

## 目录

1. [快速开始](#1-快速开始)
2. [环境配置](#2-环境配置)
3. [启动服务](#3-启动服务)
4. [API 使用指南](#4-api-使用指南)
5. [消息队列使用指南](#5-消息队列使用指南)
6. [爬虫数据模型使用指南](#6-爬虫数据模型使用指南)
7. [配置管理](#7-配置管理)
8. [系统架构说明](#8-系统架构说明)
9. [测试指南](#9-测试指南)
10. [常见问题](#10-常见问题)
11. [附录](#11-附录)

---

## 1. 快速开始

### 1.1 环境要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.9+ |
| pip | 21.0+ |
| Redis（可选） | 6.0+（使用 RedisQueue 时） |

### 1.2 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd python-AI

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python -c "from src.main import app; print('安装成功')"
```

### 1.3 一分钟快速体验

```python
# 快速体验消息队列
from message_queue import InMemoryQueue, Producer, Consumer

# 创建队列
queue = InMemoryQueue()

# 创建生产者和消费者
producer = Producer(queue)
consumer = Consumer(queue)

# 发送消息
msg_id = producer.send({"task": "hello"})
print(f"消息已发送: {msg_id}")

# 接收消息
msg = consumer.receive()
print(f"收到消息: {msg.body}")

# 确认处理完成
consumer.ack(msg)
print("消息已确认")
```

### 1.4 快速体验 API 服务

```bash
# 1. 启动服务
uvicorn src.main:app --reload &

# 2. 健康检查
curl http://localhost:8000/health
# {"status": "healthy"}

# 3. 登录获取 Token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' | python3 -m json.tool
# {
#     "token": "valid-token",
#     "expires_in": 3600
# }

# 4. 创建用户
curl -s -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "pass123"}' | python3 -m json.tool
# {
#     "id": 1,
#     "username": "alice",
#     "email": "alice@example.com",
#     "created_at": "2024-06-15T10:30:00"
# }

# 5. 发送消息到队列
curl -s -X POST http://localhost:8000/api/v1/queue/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer valid-token" \
  -d '{"body": {"url": "https://example.com"}, "priority": 5}' | python3 -m json.tool
# {
#     "message_id": "a1b2c3d4-...",
#     "status": "sent",
#     "queue_size": 1
# }
```

---

## 2. 环境配置

### 2.1 配置文件

项目配置通过 `settings.py` 管理，主要配置项如下：

| 配置项 | 说明 | 默认值 | 推荐值 |
|--------|------|--------|--------|
| `BOT_NAME` | Scrapy 爬虫名称 | `TS` | 保持不变 |
| `ROBOTSTXT_OBEY` | 是否遵守 robots.txt | `True` | `True` |
| `LOG_LEVEL` | 日志级别 | `INFO` | `INFO`（开发）/ `WARNING`（生产） |
| `CONCURRENT_REQUESTS` | 最大并发请求数 | 16（注释） | 16~32 |
| `DOWNLOAD_DELAY` | 下载延迟（秒） | 3（注释） | 1~5 |
| `ITEM_PIPELINES` | 数据管道配置 | `TsPipeline: 300` | 保持不变 |

### 2.2 环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| `DATABASE_URL` | 数据库连接字符串 | 否 | 内存存储 |
| `REDIS_URL` | Redis 连接字符串 | 否 | `redis://localhost:6379/0` |
| `JWT_SECRET` | JWT 签名密钥 | 否 | 开发环境默认值 |
| `JWT_EXPIRATION` | JWT 过期时间（秒） | 否 | `3600` |

### 2.3 日志配置

```python
# settings.py 中配置日志级别
LOG_LEVEL = 'INFO'  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL

# 代码中使用日志
import logging
logger = logging.getLogger(__name__)
logger.info("服务启动成功")
logger.debug("调试信息")
logger.error("错误信息")
```

### 2.4 依赖安装

```bash
# 安装核心依赖
pip install fastapi uvicorn pydantic

# 安装消息队列依赖
pip install redis          # Redis 队列支持（可选）

# 安装测试依赖
pip install pytest pytest-cov

# 安装所有依赖
pip install -r requirements.txt
```

### 2.5 PYTHONPATH 配置

为确保模块导入正确，需要将项目根目录添加到 PYTHONPATH：

```bash
# Linux/Mac
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Windows PowerShell
$env:PYTHONPATH = "$env:PYTHONPATH;$PWD"

# 永久配置（Linux/Mac，写入 ~/.bashrc）
echo 'export PYTHONPATH=$PYTHONPATH:/path/to/python-AI' >> ~/.bashrc
```

---

## 3. 启动服务

### 3.1 启动 API 服务

```bash
# 方式一：使用 uvicorn（推荐）
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 方式二：指定更多参数
uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --workers 4

# 方式三：直接运行
python -m src.main
```

### 3.2 验证服务是否启动

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应
{"status": "healthy"}
```

### 3.3 访问 API 文档

服务启动后，可通过以下地址访问自动生成的 API 文档：

| 文档类型 | 地址 |
|----------|------|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

---

## 4. API 使用指南

### 4.1 认证流程

认证模块位于 `src/services/auth_service.py`，使用 JWT Bearer Token 机制。
当前实现使用占位 Token（`valid-token`），生产环境需替换为真实 JWT 签发逻辑。

#### 4.1.1 用户登录

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 响应示例
{
  "token": "valid-token",
  "expires_in": 3600
}
```

**登录请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

**认证逻辑说明：**

1. `AuthService.authenticate()` 调用 `UserRepository.find_by_username()` 查找用户
2. 用户不存在 → 抛出 `AuthenticationError`（401）
3. 密码不匹配 → 抛出 `AuthenticationError`（401）
4. 认证成功 → 返回 `{"token": "valid-token", "expires_in": 3600}`

> **注意**：当前实现使用明文密码比对（`password != "password"`），生产环境应替换为 bcrypt/scrypt 等密码哈希算法，并集成真实的 JWT 签发库（如 `python-jose`）。

#### 4.1.2 使用 Token 访问受保护接口

```bash
# 将 Token 保存为变量
TOKEN="valid-token"

# 访问受保护接口
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

**认证中间件说明：**

认证中间件位于 `src/api/middleware/auth_middleware.py`：

- 使用 `HTTPBearer` 从请求头提取 Token
- 调用 `get_current_user()` 验证 Token 有效性
- 当前实现仅检查 Token 是否为 `"valid-token"`
- 验证通过后返回用户信息 `{"user_id": 1, "username": "testuser"}`
- 验证失败返回 401 错误

**Python 客户端示例：**

```python
import requests

BASE_URL = "http://localhost:8000"

# 登录
resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
    "username": "admin",
    "password": "password",
})
token = resp.json()["token"]

# 使用 Token 访问受保护接口
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/api/v1/users/1", headers=headers)
print(resp.json())
```

### 4.2 用户管理

用户管理模块位于 `src/services/user_service.py`，使用内存存储（`UserRepository`）。
生产环境应替换为数据库实现。

#### 4.2.1 用户数据模型

```python
from src.models.user import User
from datetime import datetime

# User 数据类包含以下字段
user = User(
    id=1,                    # 用户 ID（自动生成）
    username="alice",        # 用户名（唯一）
    email="alice@test.com",  # 邮箱
    password_hash="***",     # 密码哈希
    created_at=datetime.utcnow(),  # 创建时间（自动填充）
)
```

#### 4.2.2 创建用户

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123"
  }'

# 响应示例 (201 Created)
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "created_at": "2024-06-15T10:30:00"
}
```

**创建用户请求参数：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | string | 是 | 用户名（唯一） |
| `email` | string | 是 | 邮箱地址 |
| `password` | string | 是 | 密码 |

**创建用户业务逻辑：**

1. `UserService.create_user()` 检查用户名是否已存在
2. 用户名已存在 → 抛出 `DomainException`（409 CONFLICT）
3. 用户名唯一 → 创建 `User` 对象并调用 `UserRepository.save()` 持久化
4. 返回创建的 User 对象（不含密码）

#### 4.2.3 查询用户信息

```bash
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"

# 响应示例 (200 OK)
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**查询用户响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 用户 ID |
| `username` | string | 用户名 |
| `email` | string | 邮箱 |
| `created_at` | string | 创建时间（ISO 8601 格式） |

#### 4.2.4 用户仓储层说明

`UserRepository` 位于 `src/repositories/user_repository.py`，提供以下方法：

| 方法 | 说明 | 返回 |
|------|------|------|
| `find_by_id(user_id)` | 按 ID 查找用户 | `Optional[User]` |
| `find_by_username(username)` | 按用户名查找 | `Optional[User]` |
| `save(user)` | 保存新用户（自动分配 ID） | `User` |
| `delete(user_id)` | 删除用户 | `bool` |

**Python 编程使用：**

```python
from src.repositories.user_repository import UserRepository
from src.models.user import User

repo = UserRepository()

# 创建用户
user = User(username="bob", email="bob@test.com", password_hash="hashed_pwd")
saved = repo.save(user)
print(f"用户已创建: id={saved.id}, username={saved.username}")

# 查询用户
found = repo.find_by_id(1)
print(f"找到用户: {found.username}")

# 按用户名查找
found = repo.find_by_username("bob")
print(f"找到用户: {found.email}")

# 删除用户
deleted = repo.delete(1)
print(f"删除{'成功' if deleted else '失败'}")
```

### 4.3 消息队列 API

#### 4.3.1 发送消息

```bash
# 发送单条消息
curl -X POST http://localhost:8000/api/v1/queue/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "body": {"url": "https://example.com/page1", "depth": 1},
    "priority": 5,
    "topic": "crawl:high",
    "ttl": 3600
  }'

# 响应示例
{
  "message_id": "msg_abc123",
  "status": "sent",
  "queue_size": 42
}
```

#### 4.3.2 批量发送消息

```bash
curl -X POST http://localhost:8000/api/v1/queue/send_batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "messages": [
      {"body": {"url": "https://example.com/page1"}, "priority": 5, "topic": "crawl:high"},
      {"body": {"url": "https://example.com/page2"}, "priority": 3, "topic": "crawl:normal"},
      {"body": {"url": "https://example.com/page3"}, "priority": 1, "topic": "crawl:low"}
    ]
  }'

# 响应示例
{
  "success_count": 3,
  "failed_count": 0,
  "message_ids": ["msg_1", "msg_2", "msg_3"]
}
```

#### 4.3.3 接收消息

```bash
curl -X GET "http://localhost:8000/api/v1/queue/receive?timeout=5" \
  -H "Authorization: Bearer $TOKEN"

# 响应示例
{
  "message_id": "msg_abc123",
  "body": {"url": "https://example.com/page1", "depth": 1},
  "priority": 5,
  "topic": "crawl:high",
  "status": "processing",
  "created_at": "2024-06-15T10:30:00",
  "received_at": "2024-06-15T10:30:05"
}
```

#### 4.3.4 确认消息

```bash
# 处理完成后确认消息
curl -X POST http://localhost:8000/api/v1/queue/ack/msg_abc123 \
  -H "Authorization: Bearer $TOKEN"

# 响应示例
{
  "status": "acknowledged",
  "message_id": "msg_abc123"
}
```

#### 4.3.5 拒绝消息

```bash
# 拒绝消息（可选择是否重新入队）
curl -X POST http://localhost:8000/api/v1/queue/nack/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"requeue": true, "reason": "处理超时"}'

# 响应示例
{
  "status": "nacknowledged",
  "message_id": "msg_abc123",
  "requeued": true
}
```

#### 4.3.6 队列监控

```bash
# 获取队列统计信息
curl http://localhost:8000/api/v1/queue/stats \
  -H "Authorization: Bearer $TOKEN"

# 响应示例
{
  "pending": 15,
  "processing": 3,
  "completed": 120,
  "failed": 2,
  "total": 140,
  "queue_size": 18
}

# 队列健康检查
curl http://localhost:8000/api/v1/queue/health \
  -H "Authorization: Bearer $TOKEN"

# 响应示例
{
  "status": "healthy",
  "queue_size": 18,
  "consumer_running": true,
  "uptime_seconds": 3600
}
```

#### 4.3.7 队列管理

```bash
# 获取队列配置
curl http://localhost:8000/api/v1/queue/config \
  -H "Authorization: Bearer $TOKEN"

# 更新队列配置
curl -X PUT http://localhost:8000/api/v1/queue/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"maxsize": 1000, "backend": "memory"}'

# 启动消费者
curl -X POST http://localhost:8000/api/v1/queue/start \
  -H "Authorization: Bearer $TOKEN"

# 停止消费者
curl -X POST http://localhost:8000/api/v1/queue/stop \
  -H "Authorization: Bearer $TOKEN"

# 查看消息列表
curl "http://localhost:8000/api/v1/queue/messages?status=pending&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 清空队列
curl -X POST http://localhost:8000/api/v1/queue/clear \
  -H "Authorization: Bearer $TOKEN"
```

### 4.4 队列服务层使用

`QueueService` 位于 `src/api/services/queue_service.py`，是消息队列的业务逻辑封装层，提供比直接使用 `Producer`/`Consumer` 更高级的 API。

#### 4.4.1 初始化队列服务

```python
from src.api.services.queue_service import QueueService
from src.api.interfaces.queue_interface import QueueConfig

# 使用默认配置（内存队列）
service = QueueService()

# 使用自定义配置
config = QueueConfig(
    backend='memory',       # 后端类型: memory/file/redis
    maxsize=1000,           # 队列最大容量（0=无限制）
    max_retries=3,          # 最大重试次数
    retry_delay=5,          # 重试延迟（秒）
    batch_size=10,          # 批量消费大小
    auto_start=False,       # 是否自动启动消费者
)
service = QueueService(config)

# 文件队列配置
file_config = QueueConfig(
    backend='file',
    data_dir='/var/data/queue',
    maxsize=0,
)
file_service = QueueService(file_config)

# Redis 队列配置
redis_config = QueueConfig(
    backend='redis',
    queue_name='my_queue',
    redis_host='redis.example.com',
    redis_port=6379,
    redis_db=0,
)
redis_service = QueueService(redis_config)
```

#### 4.4.2 发送和接收消息

```python
# 发送消息
msg_id = service.send_message(
    body={"url": "https://example.com", "depth": 1},
    priority=5,
    topic="crawl:high",
    max_retries=3,
)
print(f"消息已发送: {msg_id}")

# 批量发送
msg_ids = service.send_batch([
    {"url": "https://example.com/1"},
    {"url": "https://example.com/2"},
    {"url": "https://example.com/3"},
], priority=3, topic="crawl:normal")

# 接收消息
msg = service.receive_message(timeout=5.0)
if msg:
    print(f"收到消息: {msg.msg_id}, body={msg.body}")
    # 确认处理完成
    service.acknowledge_message(msg.msg_id)
else:
    print("队列为空")

# 拒绝消息（重新入队重试）
service.reject_message(msg_id, requeue=True)

# 拒绝消息（标记为失败）
service.reject_message(msg_id, requeue=False)
```

#### 4.4.3 设置消息处理器

```python
# 定义消息处理函数
def my_handler(body):
    """处理消息体，返回 True 表示成功，False 表示失败"""
    print(f"处理消息: {body}")
    # 模拟处理逻辑
    if isinstance(body, dict) and "url" in body:
        print(f"爬取: {body['url']}")
        return True
    return False

# 注册处理器
service.set_handler(my_handler)

# 启动消费循环（在后台线程运行）
service.start_consuming(interval=0.1)

# 停止消费循环
service.stop_consuming(wait=True)
```

#### 4.4.4 队列管理

```python
# 获取队列大小
size = service.queue_size()
print(f"待处理消息数: {size}")

# 清空队列
cleared = service.clear_queue()
print(f"已清空 {cleared} 条消息")

# 关闭服务
service.close()
```

#### 4.4.5 全局单例模式

`QueueService` 提供全局单例访问方式：

```python
from src.api.services.queue_service import get_queue_service, get_queue_monitor

# 获取全局队列服务实例
service = get_queue_service()

# 获取全局队列监控实例
monitor = get_queue_monitor()
```

### 4.5 队列监控使用

`QueueMonitor` 位于 `src/api/services/queue_service.py`，提供队列运行状态监控。

#### 4.5.1 获取统计信息

```python
from src.api.services.queue_service import QueueService, QueueMonitor

service = QueueService()
monitor = QueueMonitor(service)

# 获取详细统计
stats = monitor.get_stats()
print(f"待处理: {stats.pending_count}")
print(f"处理中: {stats.processing_count}")
print(f"已完成: {stats.completed_count}")
print(f"失败: {stats.failed_count}")
print(f"消费者运行中: {stats.is_running}")
print(f"后端类型: {stats.backend}")
print(f"运行时长: {stats.uptime_seconds:.1f} 秒")
```

#### 4.5.2 健康检查

```python
# 健康检查
health = monitor.health_check()
print(f"状态: {health['status']}")
print(f"运行时长: {health['uptime_seconds']} 秒")
if health['issues']:
    print(f"告警: {health['issues']}")
```

**健康检查返回格式：**

```json
{
  "status": "healthy",
  "timestamp": "2024-06-15T10:30:00.123456",
  "uptime_seconds": 3600.0,
  "issues": [],
  "stats": {
    "pending": 15,
    "processing": 3,
    "completed": 120,
    "failed": 2,
    "is_running": true,
    "backend": "memory"
  }
}
```

**健康检查告警条件：**

| 条件 | 告警信息 |
|------|----------|
| 队列未初始化 | "队列未初始化" |
| 待处理消息 > 1000 | "消息积压: N 条待处理" |
| 失败率 > 10% | "失败率过高: N%" |

### 4.6 错误处理

所有 API 错误返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

常见 HTTP 状态码：

| 状态码 | 含义 | 常见原因 |
|--------|------|----------|
| 200 | 成功 | 请求处理成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 参数无效、队列已满 |
| 401 | 未认证 | Token 缺失或无效 |
| 404 | 未找到 | 资源不存在 |
| 409 | 冲突 | 用户名已存在 |
| 422 | 参数校验失败 | 请求体格式错误 |
| 503 | 服务不可用 | 队列服务异常 |

---

## 5. 消息队列使用指南

### 5.1 消息队列概述

消息队列是爬虫系统的核心组件，位于 `message_queue.py`，支持三种后端实现：

| 后端类型 | 实现类 | 适用场景 | 特性 |
|----------|--------|----------|------|
| 内存 | `InMemoryQueue` | 单机开发/测试 | 快速、无持久化 |
| 文件 | `FileQueue` | 单机生产环境 | 持久化、崩溃恢复 |
| Redis | `RedisQueue` | 分布式生产环境 | 多进程消费、高可用 |

**队列抽象基类 `BaseQueue` 定义了统一接口：**

| 方法 | 说明 | 参数 | 返回 |
|------|------|------|------|
| `send(message)` | 发送消息 | `Message` 对象 | `str`（消息 ID） |
| `receive(timeout)` | 接收消息 | `timeout` 超时秒数 | `Optional[Message]` |
| `ack(message)` | 确认消息 | `Message` 对象 | `bool` |
| `nack(message, requeue)` | 拒绝消息 | `requeue` 是否重试 | `bool` |
| `size()` | 待处理消息数 | 无 | `int` |
| `clear()` | 清空队列 | 无 | `int` |
| `close()` | 关闭队列 | 无 | 无 |

### 5.2 消息生命周期

消息状态定义在 `MessageStatus` 枚举中：

```
创建 (NEW)
  │
  ▼
发送 → PENDING（待处理）
  │
  ▼
接收 → PROCESSING（处理中）
  │
  ├── 确认 (ack) → COMPLETED（已完成）
  │
  └── 拒绝 (nack)
        ├── requeue=true & retry_count < max_retries → RETRY（待重试）→ PENDING
        └── requeue=false 或 超过最大重试次数 → FAILED（失败）
```

**状态说明：**

| 状态 | 枚举值 | 说明 |
|------|--------|------|
| `PENDING` | `pending` | 消息已入队，等待消费者处理 |
| `PROCESSING` | `processing` | 消息已被消费者取出，正在处理中 |
| `COMPLETED` | `completed` | 消息处理成功，已确认完成 |
| `FAILED` | `failed` | 消息处理失败，或超过最大重试次数 |
| `RETRY` | `retry` | 消息处理失败，等待重新入队重试 |

### 5.3 消息属性

`Message` 数据类定义在 `message_queue.py` 第 57-114 行：

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `msg_id` | `str` | 消息唯一标识（自动生成 UUID） | 自动生成 |
| `body` | `Any` | 消息内容（任意可序列化对象） | 必填 |
| `status` | `MessageStatus` | 当前状态 | `PENDING` |
| `created_at` | `str` | 创建时间（ISO 格式） | 自动 |
| `updated_at` | `str` | 最后更新时间（ISO 格式） | 自动 |
| `retry_count` | `int` | 已重试次数 | `0` |
| `max_retries` | `int` | 最大重试次数 | `3` |
| `error` | `Optional[str]` | 错误信息 | `None` |
| `priority` | `int` | 优先级（数值越大优先级越高） | `0` |

**Message 对象方法：**

| 方法 | 说明 |
|------|------|
| `to_dict()` | 转换为字典（包含所有字段） |
| `from_dict(data)` | 类方法，从字典恢复 Message 对象 |

### 5.4 队列后端详解

#### 5.4.1 InMemoryQueue（内存队列）

**源码位置：** `message_queue.py` 第 172-308 行

**特点：**
- 使用 Python `list` 模拟优先级队列，按 `priority` 降序排列
- 线程安全（使用 `threading.Lock` + `Condition`）
- 支持消息状态追踪（待处理、处理中、已完成/失败）
- 保留最近 1000 条历史记录用于审计
- **不支持进程间通信**，仅适用于单进程

**内部数据结构：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `_queue` | `List[Message]` | 待处理消息队列（按优先级排序） |
| `_processing` | `dict` | 处理中的消息（msg_id -> Message） |
| `_history` | `List[Message]` | 已完成/失败的历史消息（最多 1000 条） |
| `_maxsize` | `int` | 队列最大容量（0=无限制） |

**额外属性：**

| 属性 | 说明 |
|------|------|
| `pending_count` | 待处理消息数（同 `size()`） |
| `processing_count` | 处理中消息数 |
| `history_count` | 历史消息数 |

#### 5.4.2 FileQueue（文件队列）

**源码位置：** `message_queue.py` 第 315-504 行

**特点：**
- 每个消息存储为独立的 JSON 文件
- 使用文件系统目录结构管理消息状态
- 支持进程间通信（文件锁机制）
- **崩溃恢复**：启动时自动恢复处理中的消息
- 适合开发/测试环境

**目录结构：**

```
data_dir/
├── pending/       # 待处理消息（JSON 文件）
├── processing/    # 处理中消息
├── completed/     # 已完成消息
└── failed/        # 失败消息
```

**崩溃恢复机制：**
- 初始化时调用 `_recover_processing()` 方法
- 扫描 `processing/` 目录中遗留的消息
- 未超过重试次数 → 移回 `pending/` 重新处理
- 超过重试次数 → 移至 `failed/` 标记为失败

#### 5.4.3 RedisQueue（Redis 队列）

**源码位置：** `message_queue.py` 第 511-651 行

**特点：**
- 使用 Redis List 作为底层存储
- 支持分布式部署，多进程消费
- 支持阻塞读取（`BRPOP`）
- 需要安装 `redis-py` 库

**Redis Key 设计：**

| Key | 类型 | 说明 |
|-----|------|------|
| `{name}` | List | 待处理消息队列 |
| `{name}:processing` | Hash | 处理中的消息（msg_id -> JSON） |
| `{name}:failed` | Hash | 失败的消息 |

### 5.5 创建队列

```python
from message_queue import create_queue

# 内存队列（默认）
queue = create_queue(backend='memory')

# 内存队列（带容量限制）
queue = create_queue(backend='memory', maxsize=1000)

# 文件队列（持久化）
queue = create_queue(backend='file', data_dir='/tmp/my_queue')

# Redis 队列（分布式）
queue = create_queue(
    backend='redis',
    name='my_queue',
    host='localhost',
    port=6379,
    db=0
)
```

#### 5.4.2 生产者使用

```python
from message_queue import create_producer_consumer

# 创建生产者和消费者
producer, consumer = create_producer_consumer(backend='memory')

# 发送单条消息
msg_id = producer.send(
    body={"task": "crawl", "url": "https://example.com"},
    priority=5,
    topic="crawl:high",
    ttl=3600
)

# 批量发送
msg_ids = producer.send_batch([
    {"task": "crawl", "url": "https://example.com/1"},
    {"task": "crawl", "url": "https://example.com/2"},
    {"task": "crawl", "url": "https://example.com/3"},
], priority=3)
```

#### 5.4.3 消费者使用

```python
# 接收单条消息
message = consumer.receive(timeout=5.0)
if message:
    print(f"处理消息: {message.body}")
    # 处理完成后确认
    consumer.ack(message)
else:
    print("队列为空")

# 使用处理函数自动消费
def my_handler(message):
    """自定义消息处理函数"""
    print(f"处理消息: {message.message_id}")
    print(f"内容: {message.body}")
    # 返回 True 表示处理成功，False 表示失败
    return True

# 启动消费者循环
consumer.start(interval=0.1)  # 每 0.1 秒检查一次

# 停止消费者
consumer.stop(wait=True)  # 等待当前消息处理完成
```

#### 5.4.4 完整工作流示例

```python
from message_queue import InMemoryQueue, Producer, Consumer

# 1. 创建队列
queue = InMemoryQueue(maxsize=100)

# 2. 创建生产者和消费者
producer = Producer(queue)
consumer = Consumer(queue)

# 3. 发送消息
for i in range(10):
    producer.send(
        body={"index": i, "data": f"task-{i}"},
        priority=i % 3,
        topic="high" if i % 2 == 0 else "normal"
    )

# 4. 定义处理函数
def process_task(message):
    print(f"处理任务 {message.body['index']}: {message.body['data']}")
    return True

# 5. 消费消息
while queue.size() > 0:
    message = consumer.receive(timeout=1.0)
    if message:
        success = consumer.process(message)
        if success:
            print(f"任务 {message.body['index']} 处理成功")
        else:
            print(f"任务 {message.body['index']} 处理失败")

print(f"队列状态: 待处理={queue.pending_count()}, "
      f"处理中={queue.processing_count()}, "
      f"已完成={queue.history_count()}")
```

### 5.5 优先级与主题

#### 5.5.1 优先级队列

```python
# 高优先级消息优先处理
producer.send(body="紧急任务", priority=10)
producer.send(body="普通任务", priority=0)
producer.send(body="低优先级任务", priority=-5)

# 接收时总是先拿到高优先级的消息
message = consumer.receive()
print(message.body)  # 输出: 紧急任务
```

#### 5.5.2 主题过滤

```python
# 发送带主题的消息
producer.send(body="爬虫任务", topic="crawl")
producer.send(body="分析任务", topic="analyze")
producer.send(body="导出任务", topic="export")

# 消费者只接收特定主题的消息
crawl_consumer = Consumer(queue, topic="crawl")
message = crawl_consumer.receive()
print(message.topic)  # 输出: crawl
```

### 5.6 文件队列持久化

```python
from message_queue import FileQueue

# 创建文件队列（数据存储在指定目录）
queue = FileQueue(data_dir='/var/data/message_queue')

# 发送消息
queue.send(Message(body={"task": "持久化任务"}))

# 即使程序重启，数据也不会丢失
# 重新创建队列时会自动恢复未处理的消息
queue2 = FileQueue(data_dir='/var/data/message_queue')
print(queue2.size())  # 输出: 1
```

### 5.7 Redis 分布式队列

```python
from message_queue import RedisQueue

# 创建 Redis 队列
queue = RedisQueue(
    name='shared_queue',
    host='redis.example.com',
    port=6379,
    db=0,
    password='optional_password'
)

# 多个进程可以同时消费同一个队列
# 消息会被负载均衡到各个消费者
```

### 5.8 异常处理

消息队列模块定义了以下异常类（`message_queue.py` 第 880-892 行）：

| 异常类 | 说明 | 触发条件 |
|--------|------|----------|
| `QueueFullError` | 队列已满 | `InMemoryQueue.send()` 当 `maxsize > 0` 且队列已满时 |
| `QueueEmptyError` | 队列为空 | 预留，当前未使用 |
| `QueueConnectionError` | 队列连接异常 | `RedisQueue` 连接 Redis 失败时 |

**异常处理示例：**

```python
from message_queue import InMemoryQueue, Producer, QueueFullError

queue = InMemoryQueue(maxsize=5)
producer = Producer(queue)

for i in range(10):
    try:
        producer.send(body=f"task-{i}")
    except QueueFullError as e:
        print(f"队列已满，停止发送: {e}")
        break

print(f"成功发送 {queue.size()} 条消息")
```

### 5.9 消息队列与 API 集成

消息队列 API 端点通过 `QueueService` 与底层队列交互，完整的请求流程如下：

```
HTTP 请求 → QueueController → QueueService → Producer/Consumer → BaseQueue
```

**队列配置通过 `QueueConfig` 数据类管理：**

```python
from src.api.interfaces.queue_interface import QueueConfig

# 默认配置
config = QueueConfig()

# 各字段说明
config.backend       = "memory"    # 后端类型: memory/file/redis
config.maxsize       = 0           # 最大容量（0=无限制）
config.max_retries   = 3           # 最大重试次数
config.retry_delay   = 5           # 重试延迟（秒）
config.batch_size    = 10          # 批量消费大小
config.auto_start    = False       # 是否自动启动消费者
config.data_dir      = None        # 文件队列数据目录
config.queue_name    = None        # Redis 队列名称
config.redis_host    = None        # Redis 主机
config.redis_port    = None        # Redis 端口
config.redis_db      = None        # Redis 数据库编号
config.redis_password = None       # Redis 密码
```

**消息 DTO (`QueueMessageDTO`) 数据结构：**

```python
from src.api.interfaces.queue_interface import QueueMessageDTO

dto = QueueMessageDTO(
    msg_id="uuid-string",       # 消息唯一 ID
    body={"key": "value"},      # 消息内容
    status="pending",           # 消息状态
    created_at="2024-...",      # 创建时间
    updated_at="2024-...",      # 更新时间
    retry_count=0,              # 已重试次数
    max_retries=3,              # 最大重试次数
    error=None,                 # 错误信息
    priority=0,                 # 优先级
)
```

### 5.10 便捷工厂函数

`message_queue.py` 第 899-943 行提供了两个便捷工厂函数：

#### create_queue

```python
def create_queue(backend='memory', **kwargs) -> BaseQueue:
    """
    创建消息队列实例
    
    Args:
        backend: 队列后端类型 ('memory', 'file', 'redis')
        **kwargs: 传递给队列构造函数的参数
    
    Returns:
        队列实例
    """
```

#### create_producer_consumer

```python
def create_producer_consumer(backend='memory', handler=None, **kwargs) -> tuple:
    """
    便捷创建生产者和消费者对
    
    Args:
        backend: 队列后端类型
        handler: 消息处理函数
        **kwargs: 传递给队列和消费者的参数
    
    Returns:
        (producer, consumer) 元组
    """
```

**使用示例：**

```python
from message_queue import create_producer_consumer

# 创建内存队列的生产者-消费者对
producer, consumer = create_producer_consumer(
    backend='memory',
    handler=lambda msg: print(f"处理: {msg.body}")
)

# 发送消息
producer.send(body="hello")

# 处理消息
msg = consumer.receive()
consumer.process(msg)
```

---

## 6. 爬虫数据模型使用指南

### 6.1 数据模型概述

项目提供三种爬虫数据模型：

| 模型 | 用途 | 关键字段 |
|------|------|----------|
| `TsItem` | 教师/学生信息 | `title`, `name`, `email`, `phone`, `department` |
| `CourseItem` | 课程信息 | `course_id`, `course_name`, `capacity`, `enrolled` |
| `ArticleItem` | 文章信息 | `article_id`, `title`, `content`, `author`, `tags` |

### 6.2 TsItem 使用

```python
from items import TsItem

# 创建教师/学生信息项
item = TsItem(
    title="教授",
    name="张三",
    email="zhangsan@example.com",
    phone="13800138000",
    department="计算机科学系",
    source_url="https://example.com/teachers/1"
)

# 自动生成的字段
print(item['item_hash'])      # 基于内容生成的唯一哈希
print(item['crawl_time'])     # 爬取时间（自动填充）
print(item['status'])         # 状态（默认: active）
print(item['created_at'])     # 创建时间（自动填充）

# 获取完整名称
print(item.get_full_name())   # 输出: 教授 - 张三

# 转换为字典
data = item.to_dict()         # 过滤 None 值
data_all = item.to_dict_all() # 保留所有字段

# 验证数据完整性
if item.validate():
    print("数据有效")
else:
    print("数据不完整，缺少必填字段")
    print(f"必填字段: {item.get_required_fields()}")
```

### 6.3 CourseItem 使用

```python
from items import CourseItem

# 创建课程信息项
course = CourseItem(
    course_id="CS101",
    course_name="数据结构与算法",
    teacher="李四",
    capacity=100,
    enrolled=85,
    semester="2024-春季",
    source_url="https://example.com/courses/CS101"
)

# 判断课程是否已满
if course.is_full():
    print("课程已满员")

# 获取占用率
rate = course.get_occupancy_rate()
print(f"占用率: {rate:.1%}")  # 输出: 85.0%

# 检查是否为完整数据
if course.is_full():
    print("课程数据完整")
```

### 6.4 ArticleItem 使用

```python
from items import ArticleItem

# 创建文章信息项
article = ArticleItem(
    article_id="ART001",
    title="Python 爬虫入门",
    content="本文介绍如何使用 Python 编写爬虫...",
    author="王五",
    tags="python,爬虫,教程",  # 支持逗号分隔字符串
    attachments="file1.pdf,file2.docx",
    source_url="https://example.com/articles/1"
)

# 获取标签列表
tags = article.get_tags_list()
print(tags)  # 输出: ['python', '爬虫', '教程']

# 获取附件列表
files = article.get_attachment_list()
print(files)  # 输出: ['file1.pdf', 'file2.docx']

# 判断是否有附件
if article.has_attachments():
    print(f"包含 {len(files)} 个附件")
```

### 6.5 辅助函数详解

`items.py` 提供了 8 个辅助函数，用于批量操作和数据导出。

#### 6.5.1 create_item — 工厂函数

```python
from items import create_item

# 创建 TsItem
ts = create_item('ts', title="教授", name="张三", department="计算机系")

# 创建 CourseItem
course = create_item('course', course_name="数据结构", teacher_name="李四")

# 创建 ArticleItem
article = create_item('article', title="Python 教程", author="王五")

# 错误类型
try:
    create_item('unknown', title="无效")
except ValueError as e:
    print(e)  # 输出: Unsupported item type: unknown...
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `item_type` | `str` | 是 | 类型名称：`'ts'`、`'course'`、`'article'` |
| `**kwargs` | `Any` | 否 | 对应 Item 的字段键值对 |

#### 6.5.2 merge_items — 合并 Item

```python
from items import merge_items, TsItem

# 合并两个 TsItem
base = TsItem(title="教授", name="张三", email="old@example.com")
override = TsItem(email="new@example.com", phone="13800138000")
merged = merge_items(base, override)

print(merged['title'])    # 输出: 教授（保留 base 的值）
print(merged['email'])    # 输出: new@example.com（被 override 覆盖）
print(merged['phone'])    # 输出: 13800138000（来自 override）

# 类型不一致会抛出 TypeError
try:
    merge_items(TsItem(), CourseItem())
except TypeError as e:
    print(e)  # 类型不匹配错误
```

#### 6.5.3 batch_validate — 批量验证

```python
from items import batch_validate, TsItem, CourseItem

items = [
    TsItem(title="教授", name="张三"),     # 有效
    TsItem(),                               # 无效（缺少 title 和 name）
    CourseItem(course_name="数据结构"),      # 有效
    CourseItem(),                           # 无效（缺少 course_name）
]

result = batch_validate(items)
print(f"有效: {len(result['valid'])} 条")    # 输出: 2
print(f"无效: {len(result['invalid'])} 条")  # 输出: 2

# 查看无效项
for item in result['invalid']:
    print(f"无效项: {type(item).__name__}")
```

#### 6.5.4 items_to_dicts — 批量转字典

```python
from items import items_to_dicts, TsItem

items = [
    TsItem(title="教授", name="张三", email="zhang@test.com"),
    TsItem(title="副教授", name="李四"),
]

# 过滤 None 值
dicts = items_to_dicts(items, exclude_none=True)
for d in dicts:
    print(d.keys())  # 只包含有值的字段

# 保留所有字段
dicts_all = items_to_dicts(items, exclude_none=False)
for d in dicts_all:
    print(d.keys())  # 包含所有字段（值为 None 的字段也在内）
```

#### 6.5.5 deduplicate_items — 去重

```python
from items import deduplicate_items, TsItem

items = [
    TsItem(title="教授", name="张三", item_hash="abc"),
    TsItem(title="教授", name="张三", item_hash="abc"),  # 重复
    TsItem(title="副教授", name="李四", item_hash="def"),
]

# 按 item_hash 去重
unique = deduplicate_items(items, key_field='item_hash')
print(f"去重后: {len(unique)} 条")  # 输出: 2

# 不指定 key_field 时使用 repr
unique2 = deduplicate_items(items)
```

#### 6.5.6 filter_items — 过滤

```python
from items import filter_items, TsItem

items = [
    TsItem(title="教授", name="张三", status="active", department="CS"),
    TsItem(title="副教授", name="李四", status="active", department="Math"),
    TsItem(title="讲师", name="王五", status="inactive", department="CS"),
]

# 过滤出 active 状态的
active = filter_items(items, status='active')
print(f"活跃用户: {len(active)}")  # 输出: 2

# 多条件过滤
cs_active = filter_items(items, status='active', department='CS')
print(f"CS 系活跃用户: {len(cs_active)}")  # 输出: 1
```

#### 6.5.7 sort_items — 排序

```python
from items import sort_items, TsItem

items = [
    TsItem(title="教授", name="张三"),
    TsItem(title="副教授", name="李四"),
    TsItem(title="讲师", name="王五"),
]

# 按 title 升序
sorted_asc = sort_items(items, key_field='title')
for item in sorted_asc:
    print(item['title'])  # 输出: 副教授, 讲师, 教授

# 按 title 降序
sorted_desc = sort_items(items, key_field='title', reverse=True)
for item in sorted_desc:
    print(item['title'])  # 输出: 教授, 讲师, 副教授
```

#### 6.5.8 export_items_json — 导出 JSON

```python
from items import export_items_json, TsItem

items = [
    TsItem(title="教授", name="张三", email="zhang@test.com"),
    TsItem(title="副教授", name="李四", email="li@test.com"),
]

# 导出为 JSON 文件
export_items_json(items, 'output.json')

# 指定编码和缩进
export_items_json(items, 'output.json', ensure_ascii=False, indent=4)

# 查看输出文件内容
# cat output.json
# [
#   {
#     "title": "教授",
#     "name": "张三",
#     "email": "zhang@test.com",
#     ...
#   },
#   ...
# ]
```

#### 6.5.9 export_items_csv — 导出 CSV

```python
from items import export_items_csv, TsItem

items = [
    TsItem(title="教授", name="张三", email="zhang@test.com", department="CS"),
    TsItem(title="副教授", name="李四", email="li@test.com", department="Math"),
]

# 导出所有字段
export_items_csv(items, 'output.csv')

# 只导出指定字段
export_items_csv(items, 'output.csv', fields=['title', 'name', 'email'])

# 查看输出文件内容
# cat output.csv
# title,name,email,department
# 教授,张三,zhang@test.com,CS
# 副教授,李四,li@test.com,Math
```

### 6.6 完整工作流示例

```python
from items import (
    TsItem, CourseItem, ArticleItem,
    create_item, batch_validate, deduplicate_items,
    filter_items, export_items_json
)

# 1. 创建爬虫数据
ts_items = [
    TsItem(title="教授", name="张三", email="zhang@test.com", department="计算机系"),
    TsItem(title="副教授", name="李四", email="li@test.com", department="数学系"),
    TsItem(),  # 无效数据
]

course_items = [
    CourseItem(course_id="CS101", course_name="数据结构", teacher_name="张三"),
    CourseItem(course_id="MATH201", course_name="高等数学", teacher_name="李四"),
]

# 2. 批量验证
valid_ts = batch_validate(ts_items)['valid']
print(f"有效教师数据: {len(valid_ts)} 条")

# 3. 去重
unique_ts = deduplicate_items(valid_ts, key_field='email')

# 4. 过滤
cs_teachers = filter_items(unique_ts, department='计算机系')

# 5. 导出
export_items_json(cs_teachers, 'cs_teachers.json')
export_items_json(course_items, 'courses.json')

print("数据导出完成")
```

---

## 7. 配置管理

### 7.1 Scrapy 配置

`settings.py` 中的关键配置项：

```python
# 爬虫名称
BOT_NAME = 'TS'

# 遵守 robots.txt（建议开启）
ROBOTSTXT_OBEY = True

# 日志级别
LOG_LEVEL = 'INFO'  # 开发时可用 DEBUG

# 并发请求数（按需调整）
# CONCURRENT_REQUESTS = 16

# 下载延迟（秒），避免被封
# DOWNLOAD_DELAY = 3

# Item Pipeline 配置
ITEM_PIPELINES = {
   'TS.pipelines.TsPipeline': 300,
}
```

### 7.2 队列配置

```python
from src.api.interfaces.queue_interface import QueueConfig

# 队列配置参数
config = QueueConfig(
    backend='memory',      # 后端类型: memory/file/redis
    maxsize=1000,          # 队列最大容量（0 表示无限制）
    data_dir='/tmp/queue', # 文件队列数据目录
    redis_url='redis://localhost:6379/0',  # Redis 连接地址
    batch_size=10,         # 批量操作大小
    poll_interval=0.1      # 消费者轮询间隔（秒）
)
```

### 7.3 队列服务配置

`QueueService` 通过 `QueueConfig` 数据类进行配置：

```python
from src.api.interfaces.queue_interface import QueueConfig

# 完整配置项
config = QueueConfig(
    # === 通用配置 ===
    backend="memory",          # 后端类型: "memory" / "file" / "redis"
    maxsize=0,                 # 队列最大容量（0=无限制）
    max_retries=3,             # 消息最大重试次数
    retry_delay=5,             # 重试延迟（秒）
    batch_size=10,             # 批量消费大小
    auto_start=False,          # 是否自动启动消费者

    # === 文件队列配置 ===
    data_dir="/tmp/message_queue",  # 文件队列数据存储目录

    # === Redis 队列配置 ===
    queue_name="default_queue",     # Redis 队列名称
    redis_host="localhost",         # Redis 主机地址
    redis_port=6379,                # Redis 端口
    redis_db=0,                     # Redis 数据库编号
    redis_password=None,            # Redis 密码
)
```

**配置项详细说明：**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `backend` | `str` | `"memory"` | 队列后端类型，可选 `memory`/`file`/`redis` |
| `maxsize` | `int` | `0` | 队列最大容量，`0` 表示无限制 |
| `max_retries` | `int` | `3` | 消息处理失败最大重试次数 |
| `retry_delay` | `int` | `5` | 重试延迟时间（秒） |
| `batch_size` | `int` | `10` | 批量消费时每次拉取的消息数量 |
| `auto_start` | `bool` | `False` | 初始化时是否自动启动消费者线程 |
| `data_dir` | `Optional[str]` | `None` | 文件队列的数据存储目录路径 |
| `queue_name` | `Optional[str]` | `None` | Redis 队列的名称 |
| `redis_host` | `Optional[str]` | `None` | Redis 服务器主机地址 |
| `redis_port` | `Optional[int]` | `None` | Redis 服务器端口 |
| `redis_db` | `Optional[int]` | `None` | Redis 数据库编号 |
| `redis_password` | `Optional[str]` | `None` | Redis 认证密码 |

### 7.4 环境变量配置

```bash
# .env 文件示例
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key-here
JWT_EXPIRATION=3600
LOG_LEVEL=INFO
```

### 7.5 配置优先级

```
硬编码默认值 < QueueConfig 默认值 < 用户传入配置
```

配置加载顺序：
1. `QueueConfig` 数据类定义的默认值
2. 用户创建 `QueueConfig` 时传入的参数
3. 调用 `QueueService(config)` 时传入的配置

---

## 8. 系统架构说明

### 8.1 三层架构

项目采用经典的三层架构设计，各层职责清晰：

```
┌──────────────────────────────────────────────────┐
│                  API 层 (src/api/)                 │
│  ┌──────────────┐  ┌────────────┐  ┌──────────┐  │
│  │ Controllers   │  │ Middleware  │  │ Services │  │
│  │ (路由/参数)   │  │ (认证/错误) │  │ (业务)   │  │
│  └──────┬───────┘  └────────────┘  └────┬─────┘  │
├─────────┼────────────────────────────────┼────────┤
│         ▼                                ▼        │
│  ┌─────────────────────────────────────────────┐  │
│  │             服务层 (src/services/)            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │AuthService│  │UserService│  │QueueService│ │  │
│  │  └─────┬────┘  └────┬─────┘  └─────┬────┘  │  │
│  │        │             │              │       │  │
│  │  ┌─────┴─────────────┴──────────────┴───┐  │  │
│  │  │        Exceptions (领域异常)          │  │  │
│  │  └──────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────┤
│         ▼                                          │
│  ┌─────────────────────────────────────────────┐  │
│  │             数据层 (src/repositories/)        │  │
│  │  ┌──────────────────────────────────────┐   │  │
│  │  │         UserRepository               │   │  │
│  │  │  (内存存储，可替换为数据库实现)        │   │  │
│  │  └──────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────┤
│         ▼                                          │
│  ┌─────────────────────────────────────────────┐  │
│  │           数据模型 (src/models/)              │  │
│  │  ┌──────────────────────────────────────┐   │  │
│  │  │     User (dataclass)                │   │  │
│  │  └──────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────┘
```

### 8.2 各层职责

| 层级 | 目录 | 职责 | 关键文件 |
|------|------|------|----------|
| **API 层** | `src/api/controllers/` | 路由定义、参数校验、HTTP 响应 | `auth_controller.py`, `user_controller.py`, `queue_controller.py` |
| **API 层** | `src/api/middleware/` | 认证拦截、统一错误处理 | `auth_middleware.py`, `error_handler.py` |
| **API 层** | `src/api/services/` | 队列业务逻辑封装 | `queue_service.py` |
| **API 层** | `src/api/interfaces/` | 接口契约定义（DTO、抽象类） | `queue_interface.py`, `dto_interface.py` |
| **服务层** | `src/services/` | 核心业务逻辑 | `auth_service.py`, `user_service.py`, `exceptions.py` |
| **数据层** | `src/repositories/` | 数据持久化抽象 | `user_repository.py` |
| **数据模型** | `src/models/` | 领域模型定义 | `user.py` |

### 8.3 请求处理流程

```
客户端请求
    │
    ▼
┌─────────────────────┐
│   FastAPI 路由匹配   │  ← src/main.py 中注册的路由
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  认证中间件验证 Token │  ← auth_middleware.py (HTTPBearer)
│  (401 未认证)        │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  控制器处理请求       │  ← 参数校验、调用服务层
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  服务层执行业务逻辑   │  ← 调用仓储层、抛出领域异常
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  仓储层操作数据       │  ← 内存/数据库 CRUD
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  统一错误处理         │  ← error_handler.py 捕获异常
│  返回 JSON 响应      │     映射为 HTTP 状态码
└─────────────────────┘
```

### 8.4 依赖注入模式

服务层通过构造函数接收仓储依赖，便于单元测试：

```python
# 服务层依赖注入示例
class UserService:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        # 允许外部注入，默认使用真实实现
        self.user_repo = user_repo or UserRepository()

# 测试时注入 Mock
def test_create_user():
    mock_repo = MagicMock(spec=UserRepository)
    service = UserService(user_repo=mock_repo)
    # ...
```

### 8.5 异常处理机制

```
领域异常 (DomainException)
    ├── AuthenticationError (401)  — 认证失败
    │
    └── 其他领域异常 (400/409)     — 业务规则违反
        ├── 用户名已存在 → 409
        └── 参数无效 → 400

统一错误响应格式:
{
    "error": "ERROR_CODE",
    "message": "人类可读的错误描述",
    "status_code": 400
}
```

### 8.6 消息队列架构

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ Producer  │ ──▶ │   Queue      │ ──▶ │ Consumer  │
│ (生产者)  │     │ (队列后端)    │     │ (消费者)  │
└──────────┘     └──────┬───────┘     └──────────┘
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
      ┌─────────┐ ┌─────────┐ ┌─────────┐
      │ InMemory │ │  File   │ │  Redis  │
      │ (内存)   │ │ (文件)   │ │ (分布式)│
      └─────────┘ └─────────┘ └─────────┘

API 层封装:
┌─────────────────────────────────────┐
│         QueueController             │  ← REST API 端点
├─────────────────────────────────────┤
│         QueueService                │  ← 业务逻辑封装
├─────────────────────────────────────┤
│   Producer / Consumer / BaseQueue   │  ← 核心队列实现
└─────────────────────────────────────┘
```

---

## 9. 测试指南

### 9.1 测试环境配置

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-mock httpx

# 验证 pytest 配置
pytest --version
# pytest 7.x
```

### 9.2 测试文件结构

```
python-AI/
├── tests/                          # 单元测试目录
│   ├── __init__.py
│   ├── conftest.py                 # 共享 fixtures
│   ├── test_items.py               # 爬虫数据模型测试
│   ├── test_controllers.py         # API 控制器测试
│   ├── test_integration.py         # 集成测试
│   ├── test_middleware.py          # 中间件测试
│   ├── test_repositories.py        # 仓储层测试
│   └── test_services.py            # 服务层测试
├── test_message_queue.py           # 消息队列测试（根目录）
├── test_settings.py                # 配置测试（根目录）
└── pytest.ini                      # pytest 配置
```

### 9.3 运行测试

```bash
# 运行所有测试
pytest -v

# 运行指定测试文件
pytest tests/test_items.py -v
pytest test_message_queue.py -v

# 运行指定测试类
pytest tests/test_items.py::TestTsItem -v

# 运行指定测试函数
pytest tests/test_items.py::test_ts_item_creation -v

# 带覆盖率运行
pytest --cov=. --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=. --cov-report=html
open htmlcov/index.html

# 显示 print 输出（调试用）
pytest -v -s

# 只运行标记的测试
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "slow" -v
```

### 9.4 测试标记说明

`pytest.ini` 中定义了以下测试标记：

| 标记 | 说明 | 使用场景 |
|------|------|----------|
| `unit` | 单元测试（默认） | 单个函数/类测试 |
| `integration` | 集成测试 | 模块间交互测试 |
| `slow` | 慢速测试 | 需要较长时间的测试 |
| `redis` | Redis 相关测试 | 需要 Redis 连接 |
| `file_queue` | 文件队列测试 | 需要文件系统操作 |

### 9.5 测试用例速查

#### 消息队列测试 (`test_message_queue.py`)

```bash
# 运行消息队列测试
pytest test_message_queue.py -v

# 测试覆盖范围:
# - Message 数据类创建、序列化、状态转换
# - InMemoryQueue 入队出队、优先级排序、批量操作
# - FileQueue 文件持久化、崩溃恢复
# - RedisQueue 连接、发送接收（需 Redis）
# - Producer/Consumer 生产消费流程
# - 异常处理（队列满、队列空）
```

#### 爬虫数据模型测试 (`tests/test_items.py`)

```bash
# 运行数据模型测试
pytest tests/test_items.py -v

# 测试覆盖范围:
# - TsItem 创建、字段自动填充、哈希生成
# - CourseItem 课程容量、占用率计算
# - ArticleItem 标签解析、附件列表
# - 辅助函数：create_item, merge_items, batch_validate
# - 导出功能：export_items_json, export_items_csv
```

#### API 控制器测试 (`tests/test_controllers.py`)

```bash
# 运行控制器测试
pytest tests/test_controllers.py -v

# 测试覆盖范围:
# - 登录端点（成功/失败）
# - 用户创建（成功/用户名冲突）
# - 用户查询（成功/未找到）
# - 消息队列 API 端点
```

#### 服务层测试 (`tests/test_services.py`)

```bash
# 运行服务层测试
pytest tests/test_services.py -v

# 测试覆盖范围:
# - AuthService 认证逻辑
# - UserService 用户 CRUD
# - 异常抛出场景
```

#### 仓储层测试 (`tests/test_repositories.py`)

```bash
# 运行仓储层测试
pytest tests/test_repositories.py -v

# 测试覆盖范围:
# - UserRepository CRUD 操作
# - 按 ID/用户名查找
# - 删除操作
```

#### 中间件测试 (`tests/test_middleware.py`)

```bash
# 运行中间件测试
pytest tests/test_middleware.py -v

# 测试覆盖范围:
# - 认证中间件（有效 Token / 无效 Token / 缺失 Token）
# - 错误处理中间件（领域异常 / 通用异常）
```

#### 集成测试 (`tests/test_integration.py`)

```bash
# 运行集成测试
pytest tests/test_integration.py -v

# 测试覆盖范围:
# - 完整用户注册登录流程
# - 消息队列端到端流程
```

### 9.6 编写测试示例

```python
# tests/test_items.py 示例
import pytest
from items import TsItem, CourseItem, ArticleItem

class TestTsItem:
    """TsItem 数据模型测试"""

    def test_creation_with_required_fields(self):
        """测试使用必填字段创建 TsItem"""
        item = TsItem(title="教授", name="张三")
        assert item['title'] == "教授"
        assert item['name'] == "张三"
        assert item['status'] == "active"  # 自动填充
        assert item['crawl_time'] is not None  # 自动填充

    def test_auto_generated_hash(self):
        """测试自动生成的 item_hash"""
        item = TsItem(title="教授", name="张三", email="zhang@test.com")
        assert item['item_hash'] is not None
        assert len(item['item_hash']) == 32  # MD5 长度

    @pytest.mark.parametrize("title,name,expected", [
        ("教授", "张三", "教授 - 张三"),
        ("", "张三", "张三"),
        ("教授", "", "教授"),
        ("", "", ""),
    ])
    def test_get_full_name(self, title, name, expected):
        """测试 get_full_name 方法"""
        item = TsItem(title=title, name=name)
        assert item.get_full_name() == expected
```

### 9.7 测试 Fixtures 说明

`tests/conftest.py` 中定义了共享 fixtures：

```python
# conftest.py 示例
import pytest
from items import TsItem, CourseItem, ArticleItem

@pytest.fixture
def sample_ts_item():
    """创建一个示例 TsItem"""
    return TsItem(
        title="教授",
        name="张三",
        email="zhang@example.com",
        department="计算机系"
    )

@pytest.fixture
def sample_course_item():
    """创建一个示例 CourseItem"""
    return CourseItem(
        course_id="CS101",
        course_name="数据结构",
        teacher_name="李四",
        capacity=100,
        enrolled=85
    )

@pytest.fixture
def sample_article_item():
    """创建一个示例 ArticleItem"""
    return ArticleItem(
        article_id="ART001",
        title="Python 教程",
        author="王五",
        tags="python,编程,教程"
    )
```

---

## 10. 常见问题

### 10.1 启动问题

**Q: 启动时提示模块找不到**
```bash
# 确保在项目根目录运行
cd /path/to/python-AI
export PYTHONPATH=$PYTHONPATH:$(pwd)  # Linux/Mac
# 或
set PYTHONPATH=%PYTHONPATH%;%CD%      # Windows
```

**Q: 端口被占用**
```bash
# 查看端口占用
lsof -i :8000
# 或使用其他端口
uvicorn src.main:app --port 8001
```

### 8.2 认证问题

**Q: 返回 401 未认证**
```bash
# 检查 Token 是否有效
# 1. 重新登录获取新 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'

# 2. 确保请求头格式正确
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 8.3 消息队列问题

**Q: 消息发送失败**
- 检查队列是否已满（`maxsize` 限制）
- 检查消息体是否可序列化（JSON 格式）
- 检查认证 Token 是否有效

**Q: 消费者收不到消息**
- 检查消费者是否设置了 `topic` 过滤
- 检查队列是否为空
- 检查消费者是否已启动

**Q: 文件队列数据丢失**
- 检查 `data_dir` 目录权限
- 检查磁盘空间是否充足
- 文件队列在启动时会自动恢复未处理的消息

### 8.4 爬虫问题

**Q: 数据验证失败**
```python
# 检查必填字段
item = TsItem(title="教授", name="张三")
if not item.validate():
    print(f"缺少必填字段: {item.get_required_fields()}")
```

**Q: 导出数据为空**
```python
# 确保 Item 有数据
items = [item for item in items if item.validate()]
export_items_json(items, 'output.json')
```

---

## 9. 附录

### 9.1 常用命令速查

```bash
# 启动服务
uvicorn src.main:app --reload

# 运行测试
pytest test_message_queue.py -v
pytest test_settings.py -v

# 运行所有测试
pytest -v

# 带覆盖率运行测试
pytest --cov=. --cov-report=term-missing

# 健康检查
curl http://localhost:8000/health

# API 文档
open http://localhost:8000/docs  # Mac
# 或手动访问
```

### 9.2 项目文件结构

```
python-AI/
├── src/
│   ├── main.py                    # 应用入口
│   ├── api/
│   │   ├── controllers/           # API 控制器
│   │   │   ├── auth_controller.py
│   │   │   ├── user_controller.py
│   │   │   └── queue_controller.py
│   │   ├── interfaces/            # 接口定义
│   │   │   ├── controller_interface.py
│   │   │   ├── dto_interface.py
│   │   │   ├── middleware_interface.py
│   │   │   ├── queue_interface.py
│   │   │   ├── repository_interface.py
│   │   │   └── service_interface.py
│   │   ├── middleware/            # 中间件
│   │   │   ├── auth_middleware.py
│   │   │   └── error_handler.py
│   │   └── services/              # 服务层
│   │       └── queue_service.py
│   ├── models/                    # 数据模型
│   │   └── user.py
│   ├── repositories/              # 仓储层
│   │   └── user_repository.py
│   └── services/                  # 业务服务
│       ├── auth_service.py
│       ├── user_service.py
│       └── exceptions.py
├── docs/                          # 文档
│   ├── API.md
│   ├── USAGE.md                   # 本文件
│   ├── architecture.md
│   ├── interfaces.md
│   ├── REQUIREMENTS.md
│   ├── TECHNICAL_DESIGN.md
│   └── TESTING.md
├── message_queue.py               # 消息队列核心
├── items.py                       # 爬虫数据模型
├── settings.py                    # 配置文件
├── test_message_queue.py          # 消息队列测试
├── test_settings.py               # 配置测试
└── README.md
```

### 9.3 相关文档

| 文档 | 说明 |
|------|------|
| `docs/API.md` | 接口 API 详细文档 |
| `docs/architecture.md` | 系统架构说明 |
| `docs/interfaces.md` | 接口规范定义 |
| `docs/REQUIREMENTS.md` | 需求规格说明书 |
| `docs/TECHNICAL_DESIGN.md` | 技术架构设计 |
| `docs/TESTING.md` | 测试文档 |
| `README.md` | 项目简介 |
