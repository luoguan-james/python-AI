# 使用文档

**版本**: 1.0.0
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
8. [常见问题](#8-常见问题)
9. [附录](#9-附录)

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

#### 4.1.1 用户登录

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'

# 响应示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 4.1.2 使用 Token 访问受保护接口

```bash
# 将 Token 保存为变量
TOKEN="eyJhbGciOiJIUzI1NiIs..."

# 访问受保护接口
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 4.2 用户管理

#### 4.2.1 创建用户

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123"
  }'

# 响应示例 (201)
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "created_at": "2024-06-15T10:30:00"
}
```

#### 4.2.2 查询用户信息

```bash
curl http://localhost:8000/api/v1/users/1 \
  -H "Authorization: Bearer $TOKEN"

# 响应示例 (200)
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "created_at": "2024-01-01T00:00:00"
}
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

### 4.4 错误处理

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

消息队列是爬虫系统的核心组件，支持三种后端实现：

| 后端类型 | 实现类 | 适用场景 | 特性 |
|----------|--------|----------|------|
| 内存 | `InMemoryQueue` | 单机开发/测试 | 快速、无持久化 |
| 文件 | `FileQueue` | 单机生产环境 | 持久化、崩溃恢复 |
| Redis | `RedisQueue` | 分布式生产环境 | 多进程消费、高可用 |

### 5.2 消息生命周期

```
创建 (NEW)
  │
  ▼
发送 → PENDING（待处理）
  │
  ▼
接收 → PROCESSING（处理中）
  │
  ├── 确认 (ack) → DONE（已完成）
  │
  └── 拒绝 (nack)
        ├── requeue=true → PENDING（重新入队）
        └── requeue=false → FAILED（失败）
```

### 5.3 消息属性

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `message_id` | `str` | 消息唯一标识（自动生成 UUID） | 自动 |
| `body` | `Any` | 消息内容（任意可序列化对象） | 必填 |
| `priority` | `int` | 优先级（数值越大优先级越高） | `0` |
| `topic` | `str` | 消息主题标签 | `None` |
| `ttl` | `int` | 生存时间（秒），过期后自动丢弃 | `None`（永不过期） |
| `status` | `MessageStatus` | 当前状态 | `pending` |
| `retry_count` | `int` | 重试次数 | `0` |
| `created_at` | `datetime` | 创建时间 | 自动 |
| `source` | `str` | 来源标识 | `None` |

### 5.4 编程使用

#### 5.4.1 创建队列

```python
from message_queue import create_queue

# 内存队列（默认）
queue = create_queue(backend='memory')

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

### 6.5 批量操作工具

```python
from items import (
    create_item, merge_items, batch_validate,
    items_to_dicts, deduplicate_items,
    filter_items, sort_items,
    export_items_json, export_items_csv
)

# 工厂函数创建 Item
ts_item = create_item('ts', title="教授", name="张三")
course_item = create_item('course', course_name="数据结构")

# 合并两个 Item
base = TsItem(title="教授", name="张三")
override = TsItem(email="new@example.com")
merged = merge_items(base, override)
print(merged['email'])  # 输出: new@example.com

# 批量验证
items = [TsItem(title="有效"), TsItem()]
result = batch_validate(items)
print(f"有效: {len(result['valid'])}, 无效: {len(result['invalid'])}")

# 批量转字典
dicts = items_to_dicts(items)

# 去重
unique_items = deduplicate_items(items)

# 过滤
active_items = filter_items(items, status='active')

# 排序
sorted_items = sort_items(items, key_field='title')

# 导出
export_items_json(items, 'output.json')
export_items_csv(items, 'output.csv', fields=['title', 'name', 'email'])
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

### 7.3 环境变量配置

```bash
# .env 文件示例
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key-here
JWT_EXPIRATION=3600
LOG_LEVEL=INFO
```

---

## 8. 常见问题

### 8.1 启动问题

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
