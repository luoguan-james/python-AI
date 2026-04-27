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
