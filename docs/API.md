# 接口API文档
# 高性能爬虫系统 — 接口API文档

**版本**: 1.0.0
**更新日期**: 2024-06-15
**项目**: python-AI 爬虫系统

---

## 项目概述
## 项目概述

python-AI 是一个基于 Scrapy 框架的爬虫项目，用于爬取教师/学生（TS）信息、课程信息和文章信息。项目提供了完整的数据模型定义、数据库 ORM 模型、消息队列系统以及配置管理。

本文档描述了项目中所有可用的 API 端点、数据模型、请求/响应格式及错误码说明。

---

## 目录

1. [API 端点总览](#api-端点总览)
2. [认证 API](#1-认证-api)
3. [用户管理 API](#2-用户管理-api)
4. [消息队列 API](#3-消息队列-api)
5. [健康检查 API](#4-健康检查-api)
6. [数据模型](#5-数据模型)
7. [错误码说明](#6-错误码说明)

---

## API 端点总览

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| GET | `/api/v1/users/{user_id}` | 获取用户信息 | 是 |
| POST | `/api/v1/users` | 创建用户 | 否 |
| POST | `/api/v1/queue/send` | 发送消息 | 是 |
| POST | `/api/v1/queue/send_batch` | 批量发送消息 | 是 |
| GET | `/api/v1/queue/receive` | 接收消息 | 是 |
| POST | `/api/v1/queue/ack/{message_id}` | 确认消息 | 是 |
| POST | `/api/v1/queue/nack/{message_id}` | 拒绝消息 | 是 |
| GET | `/api/v1/queue/stats` | 队列统计 | 是 |
| GET | `/api/v1/queue/config` | 获取队列配置 | 是 |
| PUT | `/api/v1/queue/config` | 更新队列配置 | 是 |
| POST | `/api/v1/queue/start` | 启动消费者 | 是 |
| POST | `/api/v1/queue/stop` | 停止消费者 | 是 |
| GET | `/api/v1/queue/messages` | 查看消息列表 | 是 |
| POST | `/api/v1/queue/clear` | 清空队列 | 是 |
| GET | `/api/v1/queue/health` | 队列健康检查 | 是 |
| GET | `/health` | 服务健康检查 | 否 |

---

## 1. 认证 API
### 1.1 用户登录

**端点**: `POST /api/v1/auth/login`

**请求体** (`LoginRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | `string` | 是 | 用户名 |
| `password` | `string` | 是 | 密码 |

**请求示例**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应** (`LoginResponse`):

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | `string` | JWT 访问令牌 |
| `token_type` | `string` | 令牌类型（固定为 `bearer`） |
| `expires_in` | `int` | 过期时间（秒） |

**成功响应示例** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**错误响应示例** (401):
```json
{
  "detail": "用户名或密码错误"
}
```

---

## 2. 用户管理 API

### 2.1 获取用户信息

**端点**: `GET /api/v1/users/{user_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | `int` | 是 | 用户 ID |

**请求头**:
| 头 | 值 | 必填 |
|----|-----|------|
| `Authorization` | `Bearer <token>` | 是 |

**成功响应示例** (200):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应示例** (404):
```json
{
  "detail": "用户不存在"
}
```

### 2.2 创建用户

**端点**: `POST /api/v1/users`

**请求体** (`CreateUserRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | `string` | 是 | 用户名（唯一） |
| `email` | `string` | 是 | 电子邮箱 |
| `password` | `string` | 是 | 密码 |

**请求示例**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123"
}
```

**成功响应示例** (201):
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "created_at": "2024-06-15T10:30:00"
}
```

**错误响应示例** (409):
```json
{
  "detail": "用户名已存在"
}
```

---

## 3. 消息队列 API

消息队列 API 是爬虫系统的核心，支持消息的发送、接收、确认、拒绝、批量操作以及队列监控管理。所有队列端点均需认证。

### 3.1 发送消息

**端点**: `POST /api/v1/queue/send`

**请求体** (`SendMessageRequest`):

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `body` | `any` | 是 | - | 消息内容（任意可序列化对象） |
| `priority` | `int` | 否 | `0` | 消息优先级（数值越大优先级越高） |
| `topic` | `string` | 否 | `null` | 消息主题标签，用于消费者路由过滤 |
| `message_id` | `string` | 否 | `null` | 自定义消息 ID（不指定则自动生成 UUID） |
| `ttl` | `int` | 否 | `null` | 消息生存时间（秒），过期后自动丢弃 |

**请求示例**:
```json
{
  "body": {"url": "https://example.com/page1", "depth": 1},
  "priority": 5,
  "topic": "crawl:high",
  "ttl": 3600
}
```

**成功响应** (200):
```json
{
  "message_id": "msg_abc123",
  "status": "sent",
  "queue_size": 42
}
```

**错误响应**:
- `400` — 消息格式无效或队列已满
- `401` — 未认证
- `503` — 队列服务不可用

### 3.2 批量发送消息

**端点**: `POST /api/v1/queue/send_batch`

**请求体** (`BatchSendRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `messages` | `array` | 是 | 消息对象数组（每个对象同 SendMessageRequest） |

**请求示例**:
```json
{
  "messages": [
    {"body": {"url": "https://example.com/page1"}, "priority": 1, "topic": "crawl:normal"},
    {"body": {"url": "https://example.com/page2"}, "priority": 2, "topic": "crawl:high"},
    {"body": {"url": "https://example.com/page3"}, "priority": 0, "topic": "crawl:low"}
  ]
}
```

**成功响应** (200):
```json
{
  "message_ids": ["msg_001", "msg_002", "msg_003"],
  "success_count": 3,
  "failed_count": 0
}
```

> **说明**: 批量发送是逐条发送的，如果队列已满会中断并返回已成功发送的消息 ID。

### 3.3 接收消息

**端点**: `GET /api/v1/queue/receive`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `topic` | `string` | 否 | `null` | 按主题过滤消息 |
| `timeout` | `float` | 否 | `0.0` | 等待超时时间（秒），0=不等待立即返回 |

**成功响应** (200):
```json
{
  "message_id": "msg_abc123",
  "body": {"url": "https://example.com/page1"},
  "priority": 5,
  "topic": "crawl:high",
  "created_at": "2024-06-15T10:30:00.123456",
  "retry_count": 0
}
```

**空队列响应** (200):
```json
null
```

### 3.4 确认消息

**端点**: `POST /api/v1/queue/ack/{message_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | `string` | 是 | 消息 ID |

**成功响应** (200):
```json
{
  "status": "acknowledged",
  "message_id": "msg_abc123"
}
```

**错误响应** (404):
```json
{
  "detail": "消息 msg_abc123 不存在或已被确认"
}
```

### 3.5 拒绝消息

**端点**: `POST /api/v1/queue/nack/{message_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | `string` | 是 | 消息 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `requeue` | `bool` | 否 | `true` | 是否重新入队重试（超过最大重试次数后标记为失败） |

**成功响应** (200):
```json
{
  "status": "nacknowledged",
  "message_id": "msg_abc123",
  "requeued": true
}
```

**错误响应** (404):
```json
{
  "detail": "消息 msg_abc123 不存在或已被处理"
}
```

### 3.6 队列统计

**端点**: `GET /api/v1/queue/stats`

**成功响应** (200):
```json
{
  "total_sent": 150,
  "total_received": 145,
  "total_acked": 140,
  "total_nacked": 5,
  "total_failed": 3,
  "pending_count": 10,
  "processing_count": 2,
  "avg_process_time": 0.35,
  "error_rate": 0.02,
  "queue_size": 12,
  "is_running": true
}
```

### 3.7 获取队列配置

**端点**: `GET /api/v1/queue/config`

**成功响应** (200):
```json
{
  "backend": "memory",
  "maxsize": 10000,
  "max_retries": 3,
  "retry_delay": 5,
  "batch_size": 10,
  "auto_start": false
}
```

### 3.8 更新队列配置

**端点**: `PUT /api/v1/queue/config`

**请求体** (`QueueConfig`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `backend` | `string` | 否 | 后端类型：`memory` / `file` / `redis` |
| `maxsize` | `int` | 否 | 队列最大容量（0=无限制） |
| `max_retries` | `int` | 否 | 最大重试次数 |
| `retry_delay` | `int` | 否 | 重试延迟（秒） |
| `batch_size` | `int` | 否 | 批量消费大小 |
| `auto_start` | `bool` | 否 | 是否自动启动消费者 |

**成功响应** (200):
```json
{
  "status": "updated",
  "config": {
    "backend": "memory",
    "maxsize": 20000,
    "max_retries": 5,
    "retry_delay": 10,
    "batch_size": 20,
    "auto_start": true
  }
}
```

### 3.9 启动消费者

**端点**: `POST /api/v1/queue/start`

**成功响应** (200):
```json
{
  "status": "started"
}
```

### 3.10 停止消费者

**端点**: `POST /api/v1/queue/stop`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `wait` | `bool` | 否 | `true` | 是否等待当前消息处理完成后再停止 |

**成功响应** (200):
```json
{
  "status": "stopped"
}
```

### 3.11 查看消息列表

**端点**: `GET /api/v1/queue/messages`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `status` | `string` | 否 | `null` | 按状态过滤：`pending` / `processing` / `done` / `failed` |
| `topic` | `string` | 否 | `null` | 按主题过滤 |
| `skip` | `int` | 否 | `0` | 分页偏移 |
| `limit` | `int` | 否 | `20` | 每页数量（最大 100） |

**成功响应** (200):
```json
{
  "messages": [
    {
      "message_id": "msg_abc123",
      "body": "crawl_task",
      "status": "pending",
      "priority": 5,
      "topic": "crawl:high",
      "created_at": "2024-06-15T10:30:00",
      "retry_count": 0
    }
  ],
  "total": 1
}
```

### 3.12 清空队列

**端点**: `POST /api/v1/queue/clear`

**成功响应** (200):
```json
{
  "status": "cleared",
  "cleared_count": 42
}
```

### 3.13 队列健康检查

**端点**: `GET /api/v1/queue/health`

**成功响应** (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-06-15T10:30:00.123456",
  "uptime_seconds": 3600.5,
  "issues": [],
  "stats": {
    "pending": 10,
    "processing": 2,
    "completed": 140,
    "failed": 3
  }
}
```

**异常状态响应** (200):
```json
{
  "status": "unhealthy",
  "timestamp": "2024-06-15T10:30:00.123456",
  "uptime_seconds": 3600.5,
  "issues": [
    "消息积压: 1500 条待处理",
    "失败率过高: 15.0%"
  ],
  "stats": {
    "pending": 1500,
    "processing": 5,
    "completed": 850,
    "failed": 150
  }
}
```

---

## 4. 健康检查 API

### 4.1 服务健康检查

**端点**: `GET /health`

**成功响应** (200):
```json
{
  "status": "healthy"
}
```

---

## 5. 数据模型

### 5.1 TsItem（教师/学生信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | `scrapy.Field` | 是 | 标题 |
| `name` | `scrapy.Field` | 是 | 姓名 |
| `email` | `scrapy.Field` | 否 | 电子邮箱 |
| `source_url` | `scrapy.Field` | 是 | 来源 URL |
| `item_hash` | `scrapy.Field` | 自动 | MD5 去重哈希 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典（过滤 None） |
| `to_dict_all()` | `dict` | 转换为字典（包含所有字段） |
| `validate()` | `bool` | 验证必填字段 |
| `get_summary()` | `str` | 获取摘要信息 |

### 5.2 CourseItem（课程信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `course_id` | `scrapy.Field` | 否 | 课程 ID |
| `course_name` | `scrapy.Field` | 是 | 课程名称 |
| `capacity` | `scrapy.Field` | 否 | 课程容量 |
| `enrolled` | `scrapy.Field` | 否 | 已报名人数 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典 |
| `validate()` | `bool` | 验证必填字段 |
| `get_occupancy_rate()` | `float` | 获取课程占用率 |

### 5.3 ArticleItem（文章信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `article_id` | `scrapy.Field` | 否 | 文章 ID |
| `title` | `scrapy.Field` | 是 | 文章标题 |
| `content` | `scrapy.Field` | 否 | 文章内容 |
| `tags` | `scrapy.Field` | 否 | 标签列表 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典 |
| `validate()` | `bool` | 验证必填字段 |
| `get_tags_list()` | `list` | 获取标签列表 |

### 5.4 工具函数

| 函数 | 说明 |
|------|------|
| `create_item(item_type, **kwargs)` | 工厂方法创建 Item |
| `merge_items(base, override)` | 合并两个 Item |
| `batch_validate(items)` | 批量验证 |
| `deduplicate_items(items, key_field)` | 去重 |
| `filter_items(items, **conditions)` | 过滤 |
| `sort_items(items, key_field, reverse)` | 排序 |
| `export_items_json(items, filepath)` | 导出为 JSON |
| `export_items_csv(items, filepath)` | 导出为 CSV |

---

## 6. 错误码说明

| HTTP 状态码 | 说明 | 常见原因 |
|-------------|------|----------|
| `200` | 请求成功 | - |
| `201` | 创建成功 | 用户创建 |
| `400` | 请求参数错误 | 消息格式无效、队列已满、配置参数无效 |
| `401` | 未认证 | Token 缺失或无效 |
| `404` | 资源不存在 | 用户/消息不存在 |
| `409` | 资源冲突 | 用户名已存在 |
| `422` | 请求体验证失败 | 字段类型错误、缺少必填字段 |
| `500` | 服务器内部错误 | 未预期的异常 |
| `503` | 服务不可用 | 队列服务异常 |

### 统一错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

对于领域异常，格式为：
```json
{
  "error": "DOMAIN_ERROR",
  "message": "错误描述",
  "status_code": 400
}
```

---

## 7. 附录：消息队列架构

### 7.1 队列后端对比

| 特性 | InMemoryQueue | FileQueue | RedisQueue |
|------|---------------|-----------|------------|
| 数据持久化 | ❌ | ✅ (JSON 文件) | ✅ (Redis) |
| 进程间通信 | ❌ | ✅ (文件锁) | ✅ (网络) |
| 分布式支持 | ❌ | ❌ | ✅ |
| 性能 | ⚡ 极高 | 🐢 中等 | 🚀 高 |
| 适用场景 | 单进程测试/开发 | 开发/小规模生产 | 生产环境 |
| 消息上限 | 内存限制 | 磁盘限制 | Redis 内存限制 |

### 7.2 消息生命周期

```
发送 → PENDING → 接收 → PROCESSING → ACK → COMPLETED
                              ↓
                           NACK → 重试 → PENDING (循环)
                              ↓
                           超过重试次数 → FAILED
```

### 7.3 消息状态说明

| 状态 | 说明 |
|------|------|
| `PENDING` | 待处理，在队列中等待消费者接收 |
| `PROCESSING` | 处理中，已被消费者取出正在处理 |
| `COMPLETED` | 已完成，处理成功 |
| `FAILED` | 失败，超过最大重试次数 |
| `RETRY` | 待重试，即将重新入队 |

### 7.4 优先级机制

消息支持优先级（`priority` 字段），数值越大优先级越高。队列内部按优先级降序排列，高优先级的消息会被优先消费。

```python
# 高优先级消息（优先处理）
{"body": "紧急任务", "priority": 10}

# 普通消息
{"body": "普通任务", "priority": 0}

# 低优先级消息
{"body": "后台任务", "priority": -5}
```

### 7.5 重试机制

消息处理失败（NACK）时，如果 `requeue=true` 且重试次数未超过 `max_retries`，消息会重新入队等待再次处理。超过最大重试次数后，消息标记为 `FAILED`。

### 7.6 线程安全

`InMemoryQueue` 使用 `threading.Lock` 和 `Condition` 实现线程安全的生产者-消费者模式，支持多线程并发发送和接收。

### 7.7 文件队列持久化

`FileQueue` 将消息存储为独立的 JSON 文件，目录结构：
```
/tmp/message_queue/
├── pending/       # 待处理消息
├── processing/    # 处理中消息
├── completed/     # 已完成消息
└── failed/        # 失败消息
```
支持崩溃恢复：启动时自动将 `processing/` 中的消息移回 `pending/`。

### 1.1 用户登录

**端点**: `POST /api/v1/auth/login`

**请求体** (`LoginRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | `string` | 是 | 用户名 |
| `password` | `string` | 是 | 密码 |

**请求示例**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应** (`LoginResponse`):

| 字段 | 类型 | 说明 |
|------|------|------|
| `access_token` | `string` | JWT 访问令牌 |
| `token_type` | `string` | 令牌类型（固定为 `bearer`） |
| `expires_in` | `int` | 过期时间（秒） |

**成功响应示例** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**错误响应示例** (401):
```json
{
  "detail": "用户名或密码错误"
}
```

---

## 2. 用户管理 API

### 2.1 获取用户信息

**端点**: `GET /api/v1/users/{user_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | `int` | 是 | 用户 ID |

**请求头**:
| 头 | 值 | 必填 |
|----|-----|------|
| `Authorization` | `Bearer <token>` | 是 |

**成功响应示例** (200):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

**错误响应示例** (404):
```json
{
  "detail": "用户不存在"
}
```

### 2.2 创建用户

**端点**: `POST /api/v1/users`

**请求体** (`CreateUserRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `username` | `string` | 是 | 用户名（唯一） |
| `email` | `string` | 是 | 电子邮箱 |
| `password` | `string` | 是 | 密码 |

**请求示例**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123"
}
```

**成功响应示例** (201):
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "created_at": "2024-06-15T10:30:00"
}
```

**错误响应示例** (409):
```json
{
  "detail": "用户名已存在"
}
```

---

## 3. 消息队列 API

### 3.1 发送消息

**端点**: `POST /api/v1/queue/send`

**请求体** (`SendMessageRequest`):

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `body` | `any` | 是 | - | 消息内容 |
| `priority` | `int` | 否 | `0` | 优先级（数值越大优先级越高） |
| `topic` | `string` | 否 | `null` | 消息主题标签 |
| `message_id` | `string` | 否 | `null` | 自定义消息 ID |
| `ttl` | `int` | 否 | `null` | 消息生存时间（秒） |

**请求示例**:
```json
{
  "body": {"url": "https://example.com/page1", "depth": 1},
  "priority": 5,
  "topic": "crawl:high"
}
```

**成功响应** (200):
```json
{
  "message_id": "msg_abc123",
  "status": "sent",
  "queue_size": 42
}
```

### 3.2 批量发送消息

**端点**: `POST /api/v1/queue/send_batch`

**请求体** (`BatchSendRequest`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `messages` | `array` | 是 | 消息对象数组（每个对象同 SendMessageRequest） |

**请求示例**:
```json
{
  "messages": [
    {"body": "msg1", "priority": 1},
    {"body": "msg2", "priority": 2, "topic": "urgent"}
  ]
}
```

**成功响应** (200):
```json
{
  "message_ids": ["msg_001", "msg_002"],
  "success_count": 2,
  "failed_count": 0
}
```

### 3.3 接收消息

**端点**: `GET /api/v1/queue/receive`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `topic` | `string` | 否 | `null` | 按主题过滤消息 |
| `timeout` | `float` | 否 | `0.0` | 等待超时时间（秒），0=不等待 |

**成功响应** (200):
```json
{
  "message_id": "msg_abc123",
  "body": {"url": "https://example.com/page1"},
  "priority": 5,
  "topic": "crawl:high",
  "created_at": "2024-06-15T10:30:00.123456",
  "retry_count": 0
}
```

**空队列响应** (200):
```json
null
```

### 3.4 确认消息

**端点**: `POST /api/v1/queue/ack/{message_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | `string` | 是 | 消息 ID |

**成功响应** (200):
```json
{
  "status": "acknowledged",
  "message_id": "msg_abc123"
}
```

### 3.5 拒绝消息

**端点**: `POST /api/v1/queue/nack/{message_id}`

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | `string` | 是 | 消息 ID |

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `requeue` | `bool` | 否 | `true` | 是否重新入队重试 |

**成功响应** (200):
```json
{
  "status": "nacknowledged",
  "message_id": "msg_abc123",
  "requeued": true
}
```

### 3.6 队列统计

**端点**: `GET /api/v1/queue/stats`

**成功响应** (200):
```json
{
  "total_sent": 150,
  "total_received": 145,
  "total_acked": 140,
  "total_nacked": 5,
  "total_failed": 3,
  "pending_count": 10,
  "processing_count": 2,
  "avg_process_time": 0.35,
  "error_rate": 0.02,
  "queue_size": 12,
  "is_running": true
}
```

### 3.7 获取队列配置

**端点**: `GET /api/v1/queue/config`

**成功响应** (200):
```json
{
  "backend": "memory",
  "maxsize": 10000,
  "max_retries": 3,
  "retry_delay": 5,
  "batch_size": 10,
  "auto_start": false
}
```

### 3.8 更新队列配置

**端点**: `PUT /api/v1/queue/config`

**请求体** (`QueueConfig`):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `backend` | `string` | 否 | 后端类型（memory/file/redis） |
| `maxsize` | `int` | 否 | 队列最大容量 |
| `max_retries` | `int` | 否 | 最大重试次数 |
| `retry_delay` | `int` | 否 | 重试延迟（秒） |
| `batch_size` | `int` | 否 | 批量消费大小 |
| `auto_start` | `bool` | 否 | 是否自动启动消费者 |

**成功响应** (200):
```json
{
  "status": "updated",
  "config": {
    "backend": "memory",
    "maxsize": 20000,
    "max_retries": 5,
    "retry_delay": 10,
    "batch_size": 20,
    "auto_start": true
  }
}
```

### 3.9 启动消费者

**端点**: `POST /api/v1/queue/start`

**成功响应** (200):
```json
{
  "status": "started"
}
```

### 3.10 停止消费者

**端点**: `POST /api/v1/queue/stop`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `wait` | `bool` | 否 | `true` | 是否等待当前消息处理完成 |

**成功响应** (200):
```json
{
  "status": "stopped"
}
```

### 3.11 查看消息列表

**端点**: `GET /api/v1/queue/messages`

**查询参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `status` | `string` | 否 | `null` | 按状态过滤：pending/processing/done/failed |
| `topic` | `string` | 否 | `null` | 按主题过滤 |
| `skip` | `int` | 否 | `0` | 分页偏移 |
| `limit` | `int` | 否 | `20` | 每页数量（最大 100） |

**成功响应** (200):
```json
{
  "messages": [
    {
      "message_id": "msg_abc123",
      "body": "crawl_task",
      "status": "pending",
      "priority": 5,
      "topic": "crawl:high",
      "created_at": "2024-06-15T10:30:00",
      "retry_count": 0
    }
  ],
  "total": 1
}
```

### 3.12 清空队列

**端点**: `POST /api/v1/queue/clear`

**成功响应** (200):
```json
{
  "status": "cleared",
  "cleared_count": 42
}
```

### 3.13 队列健康检查

**端点**: `GET /api/v1/queue/health`

**成功响应** (200):
```json
{
  "status": "healthy",
  "timestamp": "2024-06-15T10:30:00.123456",
  "uptime_seconds": 3600.5,
  "issues": [],
  "stats": {
    "pending": 10,
    "processing": 2,
    "completed": 140,
    "failed": 3
  }
}
```

---

## 4. 健康检查 API

### 4.1 服务健康检查

**端点**: `GET /health`

**成功响应** (200):
```json
{
  "status": "healthy"
}
```

---

## 5. 数据模型

### 5.1 TsItem（教师/学生信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | `scrapy.Field` | 是 | 标题 |
| `name` | `scrapy.Field` | 是 | 姓名 |
| `email` | `scrapy.Field` | 否 | 电子邮箱 |
| `source_url` | `scrapy.Field` | 是 | 来源 URL |
| `item_hash` | `scrapy.Field` | 自动 | MD5 去重哈希 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典（过滤 None） |
| `to_dict_all()` | `dict` | 转换为字典（包含所有字段） |
| `validate()` | `bool` | 验证必填字段 |
| `get_summary()` | `str` | 获取摘要信息 |

### 5.2 CourseItem（课程信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `course_id` | `scrapy.Field` | 否 | 课程 ID |
| `course_name` | `scrapy.Field` | 是 | 课程名称 |
| `capacity` | `scrapy.Field` | 否 | 课程容量 |
| `enrolled` | `scrapy.Field` | 否 | 已报名人数 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典 |
| `validate()` | `bool` | 验证必填字段 |
| `get_occupancy_rate()` | `float` | 获取课程占用率 |

### 5.3 ArticleItem（文章信息）

**继承**: `scrapy.Item`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `article_id` | `scrapy.Field` | 否 | 文章 ID |
| `title` | `scrapy.Field` | 是 | 文章标题 |
| `content` | `scrapy.Field` | 否 | 文章内容 |
| `tags` | `scrapy.Field` | 否 | 标签列表 |

**方法**:

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `to_dict()` | `dict` | 转换为字典 |
| `validate()` | `bool` | 验证必填字段 |
| `get_tags_list()` | `list` | 获取标签列表 |

### 5.4 工具函数

| 函数 | 说明 |
|------|------|
| `create_item(item_type, **kwargs)` | 工厂方法创建 Item |
| `merge_items(base, override)` | 合并两个 Item |
| `batch_validate(items)` | 批量验证 |
| `deduplicate_items(items, key_field)` | 去重 |
| `filter_items(items, **conditions)` | 过滤 |
| `sort_items(items, key_field, reverse)` | 排序 |
| `export_items_json(items, filepath)` | 导出为 JSON |
| `export_items_csv(items, filepath)` | 导出为 CSV |

---

## 6. 错误码说明

| HTTP 状态码 | 说明 | 常见原因 |
|-------------|------|----------|
| `200` | 请求成功 | - |
| `201` | 创建成功 | 用户创建 |
| `400` | 请求参数错误 | 消息格式无效、队列已满 |
| `401` | 未认证 | Token 缺失或无效 |
| `404` | 资源不存在 | 用户/消息不存在 |
| `409` | 资源冲突 | 用户名已存在 |
| `422` | 请求体验证失败 | 字段类型错误、缺少必填字段 |
| `500` | 服务器内部错误 | 未预期的异常 |
| `503` | 服务不可用 | 队列服务异常 |

### 统一错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

对于领域异常，格式为：
```json
{
  "error": "DOMAIN_ERROR",
  "message": "错误描述",
  "status_code": 400
}
```
# 接口API文档

## 项目概述

python-AI 是一个基于 Scrapy 框架的爬虫项目，用于爬取教师/学生（TS）信息、课程信息和文章信息。项目提供了完整的数据模型定义、数据库 ORM 模型、消息队列系统以及配置管理。

本文档描述了项目中所有可用的 API 端点、数据模型、请求/响应格式及错误码说明。

---

## 目录

1. [RESTful API 端点](#1-restful-api-端点)
   - [1.1 健康检查](#11-健康检查)
   - [1.2 用户认证](#12-用户认证)
   - [1.3 用户管理](#13-用户管理)
2. [数据模型](#2-数据模型)
   - [2.1 TsItem — 教师/学生数据模型](#21-tsitem--教师学生数据模型)
   - [2.2 CourseItem — 课程信息数据模型](#22-courseitem--课程信息数据模型)
   - [2.3 ArticleItem — 文章信息数据模型](#23-articleitem--文章信息数据模型)
3. [数据库 ORM 模型](#3-数据库-orm-模型)
   - [3.1 TsModel](#31-tsmodel)
   - [3.2 CourseModel](#32-coursemodel)
4. [消息队列系统](#4-消息队列系统)
   - [4.1 Message 类](#41-message-类)
   - [4.2 BaseQueue 接口](#42-basequeue-接口)
   - [4.3 InMemoryQueue](#43-inmemoryqueue)
   - [4.4 FileQueue](#44-filequeue)
   - [4.5 RedisQueue](#45-redisqueue)
   - [4.6 Producer 类](#46-producer-类)
   - [4.7 Consumer 类](#47-consumer-类)
5. [配置管理](#5-配置管理)
6. [错误码说明](#6-错误码说明)

---

## 1. RESTful API 端点

**基础 URL**: `http://localhost:8000/api/v1`

**认证方式**: 除 `/auth/login` 外，所有端点需要在 `Authorization` 头中携带 Bearer Token。

### 1.1 健康检查

检查服务是否正常运行。

**请求方法**: `GET`

**请求路径**: `/health`

**请求参数**: 无

**请求体**: 无

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "status": "healthy"
}
```

---

### 1.2 用户认证

#### POST /auth/login

用户登录，验证身份并返回 JWT Token。

**请求方法**: `POST`

**请求路径**: `/auth/login`

**请求参数**: 无

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "token": "valid-token",
  "expires_in": 3600
}
```

**错误响应 (401)**:
```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Authentication failed",
  "status_code": 401
}
```

---

### 1.3 用户管理

#### GET /users/{user_id}

根据用户 ID 获取用户信息。

**请求方法**: `GET`

**请求路径**: `/users/{user_id}`

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| user_id | path | integer | 是 | 用户 ID |

**请求头**: `Authorization: Bearer <token>`

**请求体**: 无

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

**错误响应 (404)**:
```json
{
  "error": "NOT_FOUND",
  "message": "User not found",
  "status_code": 404
}
```

---

#### POST /users

创建新用户。

**请求方法**: `POST`

**请求路径**: `/users`

**请求参数**: 无

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应格式**: JSON

**响应示例 (201)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

**错误响应 (409)**:
```json
{
  "error": "USERNAME_CONFLICT",
  "message": "Username already exists",
  "status_code": 409
}
```

---

## 2. 数据模型

### 2.1 TsItem — 教师/学生数据模型

**类说明**: TS (Teacher/Student) 信息数据模型，用于存储爬取的教师或学生相关信息。

**继承**: `scrapy.Item`

**关联模型**: 数据持久化对应 [TsModel](#31-tsmodel)（表 `ts_items`）

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `title` | `scrapy.Field` | 是 | 标题 |
| | `name` | `scrapy.Field` | 是 | 姓名 |
| | `email` | `scrapy.Field` | 否 | 邮箱 |
| | `phone` | `scrapy.Field` | 否 | 电话 |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| | `source_name` | `scrapy.Field` | 否 | 来源名称 |
| 元数据 | `item_hash` | `scrapy.Field` | 否 | 数据唯一哈希（自动生成） |
| | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 构造行为

初始化时自动填充以下字段：

| 字段 | 默认值 | 条件 |
|------|--------|------|
| `item_hash` | `_generate_hash()` 返回值 | 始终 |
| `crawled_at` | 当前 UTC 时间 | 始终 |
| `updated_at` | 当前 UTC 时间 | 始终 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `_generate_hash() -> str` | `str` | 基于 `title`、`name`、`email`、`source_url` 生成 MD5 哈希值，用于数据去重 |
| `get_full_name() -> str` | `str` | 返回 `title + " " + name` 格式的全名 |
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回摘要信息字符串 |

---

### 2.2 CourseItem — 课程信息数据模型

**类说明**: 课程信息数据模型，用于存储爬取的课程相关信息。

**继承**: `scrapy.Item`

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `course_id` | `scrapy.Field` | 否 | 课程ID |
| | `course_name` | `scrapy.Field` | 是 | 课程名称 |
| | `teacher` | `scrapy.Field` | 否 | 授课教师 |
| | `department` | `scrapy.Field` | 否 | 所属院系 |
| 时间地点 | `schedule` | `scrapy.Field` | 否 | 上课时间安排 |
| | `location` | `scrapy.Field` | 否 | 上课地点 |
| 容量信息 | `capacity` | `scrapy.Field` | 否 | 课程容量 |
| | `enrolled` | `scrapy.Field` | 否 | 已选课人数 |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| 元数据 | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回课程摘要信息 |
| `is_full() -> bool` | `bool` | 判断课程是否已满（enrolled >= capacity） |
| `get_occupancy_rate() -> Optional[float]` | `Optional[float]` | 计算课程占用率 |

---

### 2.3 ArticleItem — 文章信息数据模型

**类说明**: 文章信息数据模型，用于存储爬取的文章相关信息。

**继承**: `scrapy.Item`

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `article_id` | `scrapy.Field` | 否 | 文章ID |
| | `title` | `scrapy.Field` | 是 | 文章标题 |
| | `author` | `scrapy.Field` | 否 | 作者 |
| | `content` | `scrapy.Field` | 否 | 文章内容 |
| | `summary` | `scrapy.Field` | 否 | 文章摘要 |
| 分类信息 | `category` | `scrapy.Field` | 否 | 文章分类 |
| | `tags` | `scrapy.Field` | 否 | 标签（逗号分隔字符串） |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| 附件信息 | `attachments` | `scrapy.Field` | 否 | 附件列表（逗号分隔字符串） |
| 元数据 | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回文章摘要信息 |
| `get_tags_list() -> List[str]` | `List[str]` | 将 tags 字段按逗号分割为列表 |
| `get_attachment_list() -> List[str]` | `List[str]` | 将 attachments 字段按逗号分割为列表 |
| `has_attachments() -> bool` | `bool` | 判断是否有附件 |

---

## 3. 数据库 ORM 模型

### 3.1 TsModel

**类说明**: TS (Teacher/Student) 数据库模型，对应表 `ts_items`。

**继承**: `sqlalchemy.ext.declarative.declarative_base`

#### 字段定义

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `Integer` | PK, autoincrement | 主键 |
| `title` | `String(200)` | nullable | 标题 |
| `name` | `String(100)` | nullable | 姓名 |
| `email` | `String(200)` | nullable | 邮箱 |
| `phone` | `String(50)` | nullable | 电话 |
| `source_url` | `Text` | nullable | 来源 URL |
| `source_name` | `String(200)` | nullable | 来源名称 |
| `item_hash` | `String(64)` | unique, nullable | 数据唯一哈希 |
| `crawled_at` | `DateTime` | default=utcnow | 爬取时间 |
| `updated_at` | `DateTime` | default=utcnow, onupdate=utcnow | 更新时间 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将模型转换为字典 |

### 3.2 CourseModel

**类说明**: 课程信息数据库模型，对应表 `course_items`。

**继承**: `sqlalchemy.ext.declarative.declarative_base`

#### 字段定义

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `Integer` | PK, autoincrement | 主键 |
| `course_id` | `String(100)` | nullable | 课程ID |
| `course_name` | `String(200)` | nullable | 课程名称 |
| `teacher` | `String(100)` | nullable | 授课教师 |
| `department` | `String(200)` | nullable | 所属院系 |
| `schedule` | `Text` | nullable | 上课时间安排 |
| `location` | `String(200)` | nullable | 上课地点 |
| `capacity` | `Integer` | nullable | 课程容量 |
| `enrolled` | `Integer` | nullable | 已选课人数 |
| `source_url` | `Text` | nullable | 来源 URL |
| `crawled_at` | `DateTime` | default=utcnow | 爬取时间 |
| `updated_at` | `DateTime` | default=utcnow, onupdate=utcnow | 更新时间 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将模型转换为字典 |

---

## 4. 消息队列系统

### 4.1 Message 类

**类说明**: 消息队列中的消息单元。

**继承**: 无

#### 字段定义

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | `str` | UUID 自动生成 | 消息唯一标识 |
| `body` | `Any` | 必填 | 消息体 |
| `priority` | `int` | 0 | 优先级（数值越大优先级越高） |
| `topic` | `str` | `"default"` | 消息主题 |
| `status` | `MessageStatus` | `PENDING` | 消息状态 |
| `created_at` | `datetime` | 当前时间 | 创建时间 |
| `updated_at` | `datetime` | 当前时间 | 更新时间 |
| `retry_count` | `int` | 0 | 重试次数 |
| `max_retries` | `int` | 3 | 最大重试次数 |
| `error_message` | `Optional[str]` | None | 错误信息 |

#### 消息状态枚举 (MessageStatus)

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待处理 |
| `PROCESSING` | 正在处理 |
| `DONE` | 处理完成 |
| `FAILED` | 处理失败 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将消息转换为字典 |
| `from_dict(data: dict) -> Message` | `Message` | 从字典创建消息（类方法） |
| `is_expired() -> bool` | `bool` | 检查消息是否过期 |
| `mark_processing()` | `None` | 标记为处理中 |
| `mark_done()` | `None` | 标记为已完成 |
| `mark_failed(error: str = "")` | `None` | 标记为失败 |
| `increment_retry()` | `None` | 增加重试计数 |

---

### 4.2 BaseQueue 接口

**类说明**: 消息队列的抽象基类，定义了所有队列实现必须遵循的接口。

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `send(message: Message) -> str` | `str` | 发送消息，返回消息 ID |
| `receive(timeout: float = 0) -> Optional[Message]` | `Optional[Message]` | 接收消息 |
| `ack(message: Message) -> bool` | `bool` | 确认消息处理成功 |
| `nack(message: Message, requeue: bool = False) -> bool` | `bool` | 拒绝消息（可选择重新入队） |
| `size() -> int` | `int` | 获取队列大小 |
| `clear() -> int` | `int` | 清空队列 |
| `close()` | `None` | 关闭队列 |

---

### 4.3 InMemoryQueue

**类说明**: 基于内存的消息队列实现，支持优先级排序和主题过滤。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `maxsize` | `int` | 0 | 队列最大容量（0 表示无限制） |

#### 特性

- 支持优先级排序（高优先级消息优先出队）
- 支持主题过滤
- 线程安全
- 支持上下文管理器
- 提供统计信息（pending、processing、history 计数）

---

### 4.4 FileQueue

**类说明**: 基于文件系统的持久化消息队列实现。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|------|------|
| `data_dir` | `str` | `/tmp/message_queue` | 数据存储目录 |

#### 特性

- 消息持久化到文件系统
- 支持崩溃恢复（重启时自动恢复处理中的消息）
- 每个消息存储为独立文件

---

### 4.5 RedisQueue

**类说明**: 基于 Redis 的消息队列实现。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|------|------|
| `name` | `str` | `"default_queue"` | 队列名称 |
| `host` | `str` | `"localhost"` | Redis 主机 |
| `port` | `int` | 6379 | Redis 端口 |
| `db` | `int` | 0 | Redis 数据库编号 |
| `password` | `Optional[str]` | None | Redis 密码 |

#### 特性

- 支持分布式部署
- 消息持久化
- 支持优先级排序

---

### 4.6 Producer 类

**类说明**: 消息生产者，用于向队列发送消息。

#### 构造参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `queue` | `BaseQueue` | 目标队列实例 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `send(body, priority=0, topic="default", ...) -> str` | `str` | 发送单条消息 |
| `send_batch(items, priority=0) -> List[str]` | `List[str]` | 批量发送消息 |
| `queue() -> BaseQueue` | `BaseQueue` | 获取关联队列 |

---

### 4.7 Consumer 类

**类说明**: 消息消费者，用于从队列接收和处理消息。

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `queue` | `BaseQueue` | 必填 | 源队列实例 |
| `handler` | `Optional[Callable]` | None | 消息处理函数 |
| `auto_ack` | `bool` | True | 是否自动确认 |
| `max_retries` | `int` | 3 | 最大重试次数 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `receive(timeout=0) -> Optional[Message]` | `Optional[Message]` | 接收单条消息 |
| `receive_batch(max_count=None, timeout=0) -> List[Message]` | `List[Message]` | 批量接收消息 |
| `ack(message) -> bool` | `bool` | 确认消息 |
| `nack(message, requeue=False) -> bool` | `bool` | 拒绝消息 |
| `process(message) -> bool` | `bool` | 处理单条消息 |
| `start(interval=0.1)` | `None` | 启动消费循环 |
| `stop(wait=True)` | `None` | 停止消费循环 |
| `is_running() -> bool` | `bool` | 检查是否正在运行 |

---

## 5. 配置管理

项目配置通过 `settings.py` 文件管理，主要配置项如下：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `LOG_LEVEL` | `str` | `"INFO"` | 日志级别 |
| `LOG_FORMAT` | `str` | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` | 日志格式 |
| `LOG_FILE` | `str` | `"scrapy.log"` | 日志文件路径 |
| `DATABASE_URL` | `str` | `"sqlite:///data.db"` | 数据库连接 URL |
| `QUEUE_BACKEND` | `str` | `"memory"` | 消息队列后端类型 |
| `QUEUE_MAXSIZE` | `int` | `1000` | 队列最大容量 |
| `CRAWL_INTERVAL` | `int` | `3600` | 爬取间隔（秒） |
| `REQUEST_DELAY` | `float` | `1.0` | 请求延迟（秒） |
| `USER_AGENT` | `str` | `"Mozilla/5.0 ..."` | 用户代理字符串 |
| `ITEM_PIPELINES` | `dict` | `{}` | Item Pipeline 配置 |

---

## 6. 错误码说明

所有 API 错误响应遵循统一格式：

```json
{
  "error": "string",
  "message": "string",
  "status_code": "integer"
}
```

### 错误码列表

| HTTP 状态码 | error_code | 说明 |
|-------------|------------|------|
| 400 | `DOMAIN_ERROR` | 通用业务逻辑错误 |
| 401 | `AUTHENTICATION_ERROR` | 认证失败（用户名或密码错误） |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `USERNAME_CONFLICT` | 用户名已存在 |
| 500 | `INTERNAL_SERVER_ERROR` | 服务器内部错误 |
# 接口API文档

## 项目概述

python-AI 是一个基于 Scrapy 框架的爬虫项目，用于爬取教师/学生（TS）信息、课程信息和文章信息。项目提供了完整的数据模型定义、数据库 ORM 模型、消息队列系统以及配置管理。

本文档描述了项目中所有可用的 API 端点、数据模型、请求/响应格式及错误码说明。

---

## 目录

1. [RESTful API 端点](#1-restful-api-端点)
   - [1.1 健康检查](#11-健康检查)
   - [1.2 用户认证](#12-用户认证)
   - [1.3 用户管理](#13-用户管理)
2. [数据模型](#2-数据模型)
   - [2.1 TsItem — 教师/学生数据模型](#21-tsitem--教师学生数据模型)
   - [2.2 CourseItem — 课程信息数据模型](#22-courseitem--课程信息数据模型)
   - [2.3 ArticleItem — 文章信息数据模型](#23-articleitem--文章信息数据模型)
3. [数据库 ORM 模型](#3-数据库-orm-模型)
   - [3.1 TsModel](#31-tsmodel)
   - [3.2 CourseModel](#32-coursemodel)
4. [消息队列系统](#4-消息队列系统)
   - [4.1 Message 类](#41-message-类)
   - [4.2 BaseQueue 接口](#42-basequeue-接口)
   - [4.3 InMemoryQueue](#43-inmemoryqueue)
   - [4.4 FileQueue](#44-filequeue)
   - [4.5 RedisQueue](#45-redisqueue)
   - [4.6 Producer 类](#46-producer-类)
   - [4.7 Consumer 类](#47-consumer-类)
5. [配置管理](#5-配置管理)
6. [错误码说明](#6-错误码说明)

---

## 1. RESTful API 端点

**基础 URL**: `http://localhost:8000/api/v1`

**认证方式**: 除 `/auth/login` 外，所有端点需要在 `Authorization` 头中携带 Bearer Token。

### 1.1 健康检查

检查服务是否正常运行。

**请求方法**: `GET`

**请求路径**: `/health`

**请求参数**: 无

**请求体**: 无

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "status": "healthy"
}
```

---

### 1.2 用户认证

#### POST /auth/login

用户登录，验证身份并返回 JWT Token。

**请求方法**: `POST`

**请求路径**: `/auth/login`

**请求参数**: 无

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "token": "valid-token",
  "expires_in": 3600
}
```

**错误响应 (401)**:
```json
{
  "error": "AUTHENTICATION_ERROR",
  "message": "Authentication failed",
  "status_code": 401
}
```

---

### 1.3 用户管理

#### GET /users/{user_id}

根据用户 ID 获取用户信息。

**请求方法**: `GET`

**请求路径**: `/users/{user_id}`

**请求参数**:

| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| user_id | path | integer | 是 | 用户 ID |

**请求头**: `Authorization: Bearer <token>`

**请求体**: 无

**响应格式**: JSON

**响应示例 (200)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

**错误响应 (404)**:
```json
{
  "error": "NOT_FOUND",
  "message": "User not found",
  "status_code": 404
}
```

---

#### POST /users

创建新用户。

**请求方法**: `POST`

**请求路径**: `/users`

**请求参数**: 无

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应格式**: JSON

**响应示例 (201)**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-15T10:30:00"
}
```

**错误响应 (409)**:
```json
{
  "error": "USERNAME_CONFLICT",
  "message": "Username already exists",
  "status_code": 409
}
```

---

## 2. 数据模型

### 2.1 TsItem — 教师/学生数据模型

**类说明**: TS (Teacher/Student) 信息数据模型，用于存储爬取的教师或学生相关信息。

**继承**: `scrapy.Item`

**关联模型**: 数据持久化对应 [TsModel](#31-tsmodel)（表 `ts_items`）

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `title` | `scrapy.Field` | 是 | 标题 |
| | `name` | `scrapy.Field` | 是 | 姓名 |
| | `email` | `scrapy.Field` | 否 | 邮箱 |
| | `phone` | `scrapy.Field` | 否 | 电话 |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| | `source_name` | `scrapy.Field` | 否 | 来源名称 |
| 元数据 | `item_hash` | `scrapy.Field` | 否 | 数据唯一哈希（自动生成） |
| | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 构造行为

初始化时自动填充以下字段：

| 字段 | 默认值 | 条件 |
|------|--------|------|
| `item_hash` | `_generate_hash()` 返回值 | 始终 |
| `crawled_at` | 当前 UTC 时间 | 始终 |
| `updated_at` | 当前 UTC 时间 | 始终 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `_generate_hash() -> str` | `str` | 基于 `title`、`name`、`email`、`source_url` 生成 MD5 哈希值，用于数据去重 |
| `get_full_name() -> str` | `str` | 返回 `title + " " + name` 格式的全名 |
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回摘要信息字符串 |

---

### 2.2 CourseItem — 课程信息数据模型

**类说明**: 课程信息数据模型，用于存储爬取的课程相关信息。

**继承**: `scrapy.Item`

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `course_id` | `scrapy.Field` | 否 | 课程ID |
| | `course_name` | `scrapy.Field` | 是 | 课程名称 |
| | `teacher` | `scrapy.Field` | 否 | 授课教师 |
| | `department` | `scrapy.Field` | 否 | 所属院系 |
| 时间地点 | `schedule` | `scrapy.Field` | 否 | 上课时间安排 |
| | `location` | `scrapy.Field` | 否 | 上课地点 |
| 容量信息 | `capacity` | `scrapy.Field` | 否 | 课程容量 |
| | `enrolled` | `scrapy.Field` | 否 | 已选课人数 |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| 元数据 | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回课程摘要信息 |
| `is_full() -> bool` | `bool` | 判断课程是否已满（enrolled >= capacity） |
| `get_occupancy_rate() -> Optional[float]` | `Optional[float]` | 计算课程占用率 |

---

### 2.3 ArticleItem — 文章信息数据模型

**类说明**: 文章信息数据模型，用于存储爬取的文章相关信息。

**继承**: `scrapy.Item`

#### 字段定义

| 分类 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 基本信息 | `article_id` | `scrapy.Field` | 否 | 文章ID |
| | `title` | `scrapy.Field` | 是 | 文章标题 |
| | `author` | `scrapy.Field` | 否 | 作者 |
| | `content` | `scrapy.Field` | 否 | 文章内容 |
| | `summary` | `scrapy.Field` | 否 | 文章摘要 |
| 分类信息 | `category` | `scrapy.Field` | 否 | 文章分类 |
| | `tags` | `scrapy.Field` | 否 | 标签（逗号分隔字符串） |
| 来源信息 | `source_url` | `scrapy.Field` | 是 | 来源 URL |
| 附件信息 | `attachments` | `scrapy.Field` | 否 | 附件列表（逗号分隔字符串） |
| 元数据 | `crawled_at` | `scrapy.Field` | 否 | 爬取时间（自动填充） |
| | `updated_at` | `scrapy.Field` | 否 | 更新时间（自动填充） |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将 Item 转换为普通字典，过滤掉 None 值 |
| `to_dict_all() -> dict` | `dict` | 将 Item 转换为普通字典，包含所有字段（含 None） |
| `validate() -> bool` | `bool` | 验证必填字段是否完整 |
| `get_required_fields() -> List[str]` | `List[str]` | 返回必填字段列表 |
| `get_summary() -> str` | `str` | 返回文章摘要信息 |
| `get_tags_list() -> List[str]` | `List[str]` | 将 tags 字段按逗号分割为列表 |
| `get_attachment_list() -> List[str]` | `List[str]` | 将 attachments 字段按逗号分割为列表 |
| `has_attachments() -> bool` | `bool` | 判断是否有附件 |

---

## 3. 数据库 ORM 模型

### 3.1 TsModel

**类说明**: TS (Teacher/Student) 数据库模型，对应表 `ts_items`。

**继承**: `sqlalchemy.ext.declarative.declarative_base`

#### 字段定义

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `Integer` | PK, autoincrement | 主键 |
| `title` | `String(200)` | nullable | 标题 |
| `name` | `String(100)` | nullable | 姓名 |
| `email` | `String(200)` | nullable | 邮箱 |
| `phone` | `String(50)` | nullable | 电话 |
| `source_url` | `Text` | nullable | 来源 URL |
| `source_name` | `String(200)` | nullable | 来源名称 |
| `item_hash` | `String(64)` | unique, nullable | 数据唯一哈希 |
| `crawled_at` | `DateTime` | default=utcnow | 爬取时间 |
| `updated_at` | `DateTime` | default=utcnow, onupdate=utcnow | 更新时间 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将模型转换为字典 |

### 3.2 CourseModel

**类说明**: 课程信息数据库模型，对应表 `course_items`。

**继承**: `sqlalchemy.ext.declarative.declarative_base`

#### 字段定义

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `Integer` | PK, autoincrement | 主键 |
| `course_id` | `String(100)` | nullable | 课程ID |
| `course_name` | `String(200)` | nullable | 课程名称 |
| `teacher` | `String(100)` | nullable | 授课教师 |
| `department` | `String(200)` | nullable | 所属院系 |
| `schedule` | `Text` | nullable | 上课时间安排 |
| `location` | `String(200)` | nullable | 上课地点 |
| `capacity` | `Integer` | nullable | 课程容量 |
| `enrolled` | `Integer` | nullable | 已选课人数 |
| `source_url` | `Text` | nullable | 来源 URL |
| `crawled_at` | `DateTime` | default=utcnow | 爬取时间 |
| `updated_at` | `DateTime` | default=utcnow, onupdate=utcnow | 更新时间 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将模型转换为字典 |

---

## 4. 消息队列系统

### 4.1 Message 类

**类说明**: 消息队列中的消息单元。

**继承**: 无

#### 字段定义

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `id` | `str` | UUID 自动生成 | 消息唯一标识 |
| `body` | `Any` | 必填 | 消息体 |
| `priority` | `int` | 0 | 优先级（数值越大优先级越高） |
| `topic` | `str` | `"default"` | 消息主题 |
| `status` | `MessageStatus` | `PENDING` | 消息状态 |
| `created_at` | `datetime` | 当前时间 | 创建时间 |
| `updated_at` | `datetime` | 当前时间 | 更新时间 |
| `retry_count` | `int` | 0 | 重试次数 |
| `max_retries` | `int` | 3 | 最大重试次数 |
| `error_message` | `Optional[str]` | None | 错误信息 |

#### 消息状态枚举 (MessageStatus)

| 状态 | 说明 |
|------|------|
| `PENDING` | 等待处理 |
| `PROCESSING` | 正在处理 |
| `DONE` | 处理完成 |
| `FAILED` | 处理失败 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `to_dict() -> dict` | `dict` | 将消息转换为字典 |
| `from_dict(data: dict) -> Message` | `Message` | 从字典创建消息（类方法） |
| `is_expired() -> bool` | `bool` | 检查消息是否过期 |
| `mark_processing()` | `None` | 标记为处理中 |
| `mark_done()` | `None` | 标记为已完成 |
| `mark_failed(error: str = "")` | `None` | 标记为失败 |
| `increment_retry()` | `None` | 增加重试计数 |

---

### 4.2 BaseQueue 接口

**类说明**: 消息队列的抽象基类，定义了所有队列实现必须遵循的接口。

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `send(message: Message) -> str` | `str` | 发送消息，返回消息 ID |
| `receive(timeout: float = 0) -> Optional[Message]` | `Optional[Message]` | 接收消息 |
| `ack(message: Message) -> bool` | `bool` | 确认消息处理成功 |
| `nack(message: Message, requeue: bool = False) -> bool` | `bool` | 拒绝消息（可选择重新入队） |
| `size() -> int` | `int` | 获取队列大小 |
| `clear() -> int` | `int` | 清空队列 |
| `close()` | `None` | 关闭队列 |

---

### 4.3 InMemoryQueue

**类说明**: 基于内存的消息队列实现，支持优先级排序和主题过滤。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `maxsize` | `int` | 0 | 队列最大容量（0 表示无限制） |

#### 特性

- 支持优先级排序（高优先级消息优先出队）
- 支持主题过滤
- 线程安全
- 支持上下文管理器
- 提供统计信息（pending、processing、history 计数）

---

### 4.4 FileQueue

**类说明**: 基于文件系统的持久化消息队列实现。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|------|------|
| `data_dir` | `str` | `/tmp/message_queue` | 数据存储目录 |

#### 特性

- 消息持久化到文件系统
- 支持崩溃恢复（重启时自动恢复处理中的消息）
- 每个消息存储为独立文件

---

### 4.5 RedisQueue

**类说明**: 基于 Redis 的消息队列实现。

**继承**: `BaseQueue`

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|------|------|
| `name` | `str` | `"default_queue"` | 队列名称 |
| `host` | `str` | `"localhost"` | Redis 主机 |
| `port` | `int` | 6379 | Redis 端口 |
| `db` | `int` | 0 | Redis 数据库编号 |
| `password` | `Optional[str]` | None | Redis 密码 |

#### 特性

- 支持分布式部署
- 消息持久化
- 支持优先级排序

---

### 4.6 Producer 类

**类说明**: 消息生产者，用于向队列发送消息。

#### 构造参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `queue` | `BaseQueue` | 目标队列实例 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `send(body, priority=0, topic="default", ...) -> str` | `str` | 发送单条消息 |
| `send_batch(items, priority=0) -> List[str]` | `List[str]` | 批量发送消息 |
| `queue() -> BaseQueue` | `BaseQueue` | 获取关联队列 |

---

### 4.7 Consumer 类

**类说明**: 消息消费者，用于从队列接收和处理消息。

#### 构造参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `queue` | `BaseQueue` | 必填 | 源队列实例 |
| `handler` | `Optional[Callable]` | None | 消息处理函数 |
| `auto_ack` | `bool` | True | 是否自动确认 |
| `max_retries` | `int` | 3 | 最大重试次数 |

#### 方法列表

| 方法签名 | 返回值 | 说明 |
|----------|--------|------|
| `receive(timeout=0) -> Optional[Message]` | `Optional[Message]` | 接收单条消息 |
| `receive_batch(max_count=None, timeout=0) -> List[Message]` | `List[Message]` | 批量接收消息 |
| `ack(message) -> bool` | `bool` | 确认消息 |
| `nack(message, requeue=False) -> bool` | `bool` | 拒绝消息 |
| `process(message) -> bool` | `bool` | 处理单条消息 |
| `start(interval=0.1)` | `None` | 启动消费循环 |
| `stop(wait=True)` | `None` | 停止消费循环 |
| `is_running() -> bool` | `bool` | 检查是否正在运行 |

---

## 5. 配置管理

项目配置通过 `settings.py` 文件管理，主要配置项如下：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `LOG_LEVEL` | `str` | `"INFO"` | 日志级别 |
| `LOG_FORMAT` | `str` | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` | 日志格式 |
| `LOG_FILE` | `str` | `"scrapy.log"` | 日志文件路径 |
| `DATABASE_URL` | `str` | `"sqlite:///data.db"` | 数据库连接 URL |
| `QUEUE_BACKEND` | `str` | `"memory"` | 消息队列后端类型 |
| `QUEUE_MAXSIZE` | `int` | `1000` | 队列最大容量 |
| `CRAWL_INTERVAL` | `int` | `3600` | 爬取间隔（秒） |
| `REQUEST_DELAY` | `float` | `1.0` | 请求延迟（秒） |
| `USER_AGENT` | `str` | `"Mozilla/5.0 ..."` | 用户代理字符串 |
| `ITEM_PIPELINES` | `dict` | `{}` | Item Pipeline 配置 |

---

## 6. 错误码说明

所有 API 错误响应遵循统一格式：

```json
{
  "error": "string",
  "message": "string",
  "status_code": "integer"
}
```

### 错误码列表

| HTTP 状态码 | error_code | 说明 |
|-------------|------------|------|
| 400 | `DOMAIN_ERROR` | 通用业务逻辑错误 |
| 401 | `AUTHENTICATION_ERROR` | 认证失败（用户名或密码错误） |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `USERNAME_CONFLICT` | 用户名已存在 |
| 500 | `INTERNAL_SERVER_ERROR` | 服务器内部错误 |
