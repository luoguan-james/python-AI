# 单元测试文档

**版本**: 1.0.0
**更新日期**: 2024-06-15
**项目**: python-AI 爬虫系统

---

## 目录

1. [测试概述](#1-测试概述)
2. [测试环境](#2-测试环境)
3. [测试框架与工具](#3-测试框架与工具)
4. [测试策略](#4-测试策略)
5. [测试用例设计](#5-测试用例设计)
6. [测试覆盖范围](#6-测试覆盖范围)
7. [运行测试](#7-运行测试)
8. [持续集成](#8-持续集成)
9. [附录](#9-附录)

---

## 1. 测试概述

### 1.1 测试目标

本文档定义了 python-AI 项目的单元测试规范，确保：

- **功能正确性**：所有核心模块按预期工作
- **边界覆盖**：覆盖正常路径、异常路径和边界条件
- **回归防护**：代码变更不会破坏已有功能
- **可维护性**：测试代码清晰、可读、易于维护

### 1.2 测试范围

| 模块 | 测试文件 | 优先级 |
|------|----------|--------|
| 消息队列核心 | `test_message_queue.py` | 高 |
| 配置管理 | `test_settings.py` | 高 |
| 数据模型 (Items) | `test_items.py` | 高 |
| API 控制器 | `test_controllers.py` | 中 |
| 服务层 | `test_services.py` | 中 |
| 仓储层 | `test_repositories.py` | 中 |
| 中间件 | `test_middleware.py` | 低 |
| 集成测试 | `test_integration.py` | 中 |

---

## 2. 测试环境

### 2.1 环境要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.9+ |
| pytest | 7.0+ |
| pytest-cov | 4.0+ |
| pytest-mock | 3.10+ |
| httpx | 0.24+ (用于 FastAPI 测试) |

### 2.2 安装依赖

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-mock httpx

# 安装项目依赖
pip install -r requirements.txt
```

### 2.3 目录结构

```
project-root/
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # 共享 fixtures
│   ├── test_items.py         # 数据模型测试
│   ├── test_message_queue.py # 消息队列测试
│   ├── test_settings.py      # 配置测试
│   ├── test_controllers.py   # API 控制器测试
│   ├── test_services.py      # 服务层测试
│   ├── test_repositories.py  # 仓储层测试
│   ├── test_middleware.py    # 中间件测试
│   └── test_integration.py   # 集成测试
├── test_message_queue.py     # 已有测试（消息队列）
├── test_settings.py          # 已有测试（配置）
└── pytest.ini                # pytest 配置
```

---

## 3. 测试框架与工具

### 3.1 测试框架

本项目使用 **pytest** 作为主要测试框架，利用其以下特性：

| 特性 | 用途 |
|------|------|
| `fixture` | 共享测试资源和上下文 |
| `parametrize` | 参数化测试用例 |
| `mark` | 标记和分类测试 |
| `conftest.py` | 全局 fixtures 配置 |
| `tmp_path` | 临时目录（文件队列测试） |
| `capsys` | 捕获标准输出 |
| `monkeypatch` | 动态修改对象 |

### 3.2 辅助工具

| 工具 | 用途 |
|------|------|
| `pytest-cov` | 代码覆盖率统计 |
| `pytest-mock` | Mock 对象管理 |
| `httpx` | FastAPI TestClient 异步支持 |
| `pytest-asyncio` | 异步测试支持 |

### 3.3 pytest 配置 (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (default)
    integration: Integration tests
    slow: Slow tests that may take longer
    redis: Tests requiring Redis connection
    file_queue: Tests for file queue
```

---

## 4. 测试策略

### 4.1 测试金字塔

```
        ╱╲
       ╱  ╲          E2E 测试 (5%)
      ╱    ╲
     ╱──────╲
    ╱        ╲      集成测试 (20%)
   ╱          ╲
  ╱────────────╲
 ╱              ╲   单元测试 (75%)
╱────────────────╲
```

### 4.2 测试分类

| 类型 | 占比 | 目标 | 运行频率 |
|------|------|------|----------|
| **单元测试** | 75% | 单个函数/类/模块 | 每次提交 |
| **集成测试** | 20% | 模块间交互 | 每次 PR |
| **端到端测试** | 5% | 完整业务流程 | 发布前 |

### 4.3 测试原则

1. **独立性**：每个测试用例独立运行，不依赖其他测试的执行顺序
2. **可重复性**：同一测试多次运行结果一致
3. **快速反馈**：单元测试应在毫秒级完成
4. **单一职责**：每个测试只验证一个行为
5. **可读性**：测试代码应清晰表达测试意图（Given-When-Then）

### 4.4 Mock 策略

| 场景 | Mock 方式 | 说明 |
|------|-----------|------|
| 外部服务 | `unittest.mock` / `pytest-mock` | 模拟 HTTP 请求、数据库等 |
| 时间依赖 | `freezegun` / `monkeypatch` | 固定时间戳 |
| 文件系统 | `tmp_path` fixture | 使用临时目录 |
| 随机数 | `monkeypatch` | 固定随机种子 |

---

## 5. 测试用例设计

### 5.1 消息队列测试 (`test_message_queue.py`)

#### 5.1.1 Message 数据类测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| MQ-001 | `test_message_creation` | 创建 Message 实例 | 所有字段正确初始化 |
| MQ-002 | `test_message_defaults` | 使用默认值创建 | 默认值正确填充 |
| MQ-003 | `test_message_to_dict` | 转换为字典 | 字典包含所有字段 |
| MQ-004 | `test_message_from_dict` | 从字典恢复 | 恢复后的对象与原对象一致 |
| MQ-005 | `test_message_is_expired` | 消息过期判断 | 无 TTL 永不过期，有 TTL 正确判断 |
| MQ-006 | `test_message_mark_processing` | 标记为处理中 | status 变为 'processing' |
| MQ-007 | `test_message_mark_done` | 标记为已完成 | status 变为 'done' |
| MQ-008 | `test_message_mark_failed` | 标记为失败 | status 变为 'failed'，error 字段设置 |
| MQ-009 | `test_message_increment_retry` | 重试计数递增 | retry_count 从 0 变为 1 |
| MQ-010 | `test_message_repr` | 字符串表示 | 包含 topic 和 message_id 前 8 位 |

#### 5.1.2 InMemoryQueue 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| IMQ-001 | `test_init_defaults` | 默认初始化 | maxsize=0, name='default' |
| IMQ-002 | `test_init_with_params` | 带参数初始化 | 参数正确设置 |
| IMQ-003 | `test_put_and_get` | 放入和取出消息 | 消息正确入队和出队 |
| IMQ-004 | `test_get_empty` | 从空队列获取 | 抛出 QueueEmptyError |
| IMQ-005 | `test_put_full` | 向满队列放入 | 抛出 QueueFullError |
| IMQ-006 | `test_priority_ordering` | 优先级排序 | 高优先级先出队 |
| IMQ-007 | `test_topic_filter` | 按主题过滤 | 只获取匹配主题的消息 |
| IMQ-008 | `test_put_batch` | 批量放入 | 所有消息入队，qsize 正确 |
| IMQ-009 | `test_get_batch` | 批量取出 | 取出指定数量消息 |
| IMQ-010 | `test_clear` | 清空队列 | qsize 变为 0 |
| IMQ-011 | `test_is_empty` | 判空 | 空返回 True，非空返回 False |
| IMQ-012 | `test_is_full` | 判满 | 满返回 True，未满返回 False |
| IMQ-013 | `test_get_all` | 获取所有消息 | 全部取出，队列为空 |
| IMQ-014 | `test_iteration` | 迭代器 | 可迭代所有消息 |
| IMQ-015 | `test_context_manager` | 上下文管理器 | 退出后队列清空 |
| IMQ-016 | `test_thread_safety` | 线程安全性 | 多线程并发操作无数据竞争 |
| IMQ-017 | `test_stats` | 统计信息 | 统计字段正确 |

#### 5.1.3 FileQueue 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| FQ-001 | `test_init_and_persistence` | 文件队列持久化 | 重新加载后数据保留 |
| FQ-002 | `test_file_queue_clear` | 清空文件队列 | 队列为空，文件被删除 |
| FQ-003 | `test_file_queue_empty` | 空文件队列 | 判空为 True，get 抛出异常 |

#### 5.1.4 Producer 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| PR-001 | `test_producer_send` | 发送消息 | 消息入队，qsize 增加 |
| PR-002 | `test_producer_send_batch` | 批量发送 | 所有消息入队 |
| PR-003 | `test_producer_with_source` | 带来源标识 | 消息 source 字段正确 |
| PR-004 | `test_producer_stats` | 生产者统计 | total_sent 正确 |

#### 5.1.5 Consumer 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| CO-001 | `test_consumer_consume` | 消费消息 | 消息状态变为 processing |
| CO-002 | `test_consumer_consume_with_topic` | 按主题消费 | 只消费匹配主题的消息 |
| CO-003 | `test_consumer_ack` | 确认消息 | 消息状态变为 done |
| CO-004 | `test_consumer_nack` | 拒绝消息 | 消息状态变为 failed |
| CO-005 | `test_consumer_process` | 处理函数 | handler 被调用，返回 True |
| CO-006 | `test_consumer_process_handler_failure` | 处理函数失败 | 返回 False，消息标记为失败 |
| CO-007 | `test_consumer_process_all` | 处理所有消息 | 所有消息被处理 |
| CO-008 | `test_consumer_stats` | 消费者统计 | 统计字段正确 |

#### 5.1.6 集成测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| INT-001 | `test_producer_consumer_workflow` | 生产者-消费者完整工作流 | 消息正确流转 |
| INT-002 | `test_multi_producer_multi_consumer` | 多生产者多消费者 | 并发操作正确 |
| INT-003 | `test_queue_stats_accuracy` | 队列统计准确性 | 统计数字与实际一致 |
| INT-004 | `test_file_queue_persistence_integration` | 文件队列持久化集成 | 跨进程数据持久化 |
| INT-005 | `test_priority_integration` | 优先级集成 | 高优先级先处理 |
| INT-006 | `test_topic_routing` | 主题路由 | 按主题正确路由 |

### 5.2 配置测试 (`test_settings.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| ST-001 | `test_log_level_exists` | LOG_LEVEL 存在 | settings 模块有 LOG_LEVEL 属性 |
| ST-002 | `test_log_level_default_value` | 默认日志级别 | LOG_LEVEL 是有效的日志级别 |
| ST-003 | `test_settings_importable` | 模块可导入 | 导入无异常，BOT_NAME 正确 |

### 5.3 数据模型测试 (`test_items.py`)

#### 5.3.1 TsItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| TI-001 | `test_ts_item_creation` | 创建 TsItem | 字段正确初始化 |
| TI-002 | `test_ts_item_defaults` | 默认值填充 | crawl_time, status, created_at, item_hash 自动填充 |
| TI-003 | `test_ts_item_to_dict` | 转换为字典 | 过滤掉 None 值 |
| TI-004 | `test_ts_item_to_dict_all` | 转换为字典（全部） | 保留所有字段 |
| TI-005 | `test_ts_item_validate_valid` | 有效数据验证 | 返回 True |
| TI-006 | `test_ts_item_validate_invalid` | 无效数据验证 | 返回 False |
| TI-007 | `test_ts_item_get_full_name` | 获取完整名称 | title - name 格式 |
| TI-008 | `test_ts_item_get_summary` | 获取摘要 | 包含关键信息 |
| TI-009 | `test_ts_item_hash_generation` | 哈希生成 | 相同内容生成相同哈希 |
| TI-010 | `test_ts_item_repr` | 字符串表示 | 包含 title 和 name |

#### 5.3.2 CourseItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| CI-001 | `test_course_item_creation` | 创建 CourseItem | 字段正确初始化 |
| CI-002 | `test_course_item_to_dict` | 转换为字典 | 过滤 None 值 |
| CI-003 | `test_course_item_validate` | 验证 | 有 course_name 返回 True |
| CI-004 | `test_course_item_is_full` | 判断课程已满 | enrolled >= capacity 返回 True |
| CI-005 | `test_course_item_get_occupancy_rate` | 获取占用率 | 返回 0.0 ~ 1.0 之间的值 |
| CI-006 | `test_course_item_get_occupancy_rate_zero_capacity` | 容量为 0 的占用率 | 返回 0.0 |

#### 5.3.3 ArticleItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AI-001 | `test_article_item_creation` | 创建 ArticleItem | 字段正确初始化 |
| AI-002 | `test_article_item_to_dict` | 转换为字典 | 过滤 None 值 |
| AI-003 | `test_article_item_validate` | 验证 | 有 title 返回 True |
| AI-004 | `test_article_item_get_tags_list` | 获取标签列表 | 支持字符串和列表格式 |
| AI-005 | `test_article_item_get_attachment_list` | 获取附件列表 | 支持多种格式 |
| AI-006 | `test_article_item_has_attachments` | 判断是否有附件 | 有附件返回 True |

#### 5.3.4 工具函数测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| UT-001 | `test_create_item` | 工厂函数创建 Item | 返回正确类型的 Item |
| UT-002 | `test_create_item_invalid_type` | 不支持的 Item 类型 | 抛出 ValueError |
| UT-003 | `test_merge_items` | 合并两个 Item | override 值覆盖 base 值 |
| UT-004 | `test_merge_items_type_mismatch` | 类型不匹配合并 | 抛出 TypeError |
| UT-005 | `test_batch_validate` | 批量验证 | 返回 valid 和 invalid 分组 |
| UT-006 | `test_items_to_dicts` | 批量转换为字典 | 返回字典列表 |
| UT-007 | `test_deduplicate_items` | 去重 | 重复项被移除 |
| UT-008 | `test_filter_items` | 过滤 | 只返回匹配条件的项 |
| UT-009 | `test_sort_items` | 排序 | 按指定字段排序 |
| UT-010 | `test_export_items_json` | 导出 JSON | 文件内容正确 |
| UT-011 | `test_export_items_csv` | 导出 CSV | 文件内容正确 |

### 5.4 API 控制器测试 (`test_controllers.py`)

#### 5.4.1 认证控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AC-001 | `test_login_success` | 登录成功 | 返回 200 和 token |
| AC-002 | `test_login_invalid_credentials` | 无效凭据 | 返回 401 |
| AC-003 | `test_login_missing_fields` | 缺少必填字段 | 返回 422 |

#### 5.4.2 用户控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| UC-001 | `test_get_user_success` | 获取用户成功 | 返回 200 和用户信息 |
| UC-002 | `test_get_user_not_found` | 用户不存在 | 返回 404 |
| UC-003 | `test_get_user_unauthorized` | 未认证 | 返回 401 |
| UC-004 | `test_create_user_success` | 创建用户成功 | 返回 201 |
| UC-005 | `test_create_user_duplicate` | 用户名重复 | 返回 409 |
| UC-006 | `test_create_user_missing_fields` | 缺少必填字段 | 返回 422 |

#### 5.4.3 队列控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| QC-001 | `test_send_message` | 发送消息 | 返回 200 和 message_id |
| QC-002 | `test_send_message_queue_full` | 队列已满 | 返回 400 |
| QC-003 | `test_send_batch` | 批量发送 | 返回成功/失败计数 |
| QC-004 | `test_receive_message` | 接收消息 | 返回消息内容 |
| QC-005 | `test_receive_message_empty` | 空队列接收 | 返回 null |
| QC-006 | `test_ack_message` | 确认消息 | 返回 acknowledged |
| QC-007 | `test_ack_message_not_found` | 确认不存在的消息 | 返回 404 |
| QC-008 | `test_nack_message` | 拒绝消息 | 返回 nacknowledged |
| QC-009 | `test_get_queue_stats` | 获取队列统计 | 返回统计信息 |
| QC-010 | `test_get_queue_config` | 获取队列配置 | 返回配置信息 |
| QC-011 | `test_update_queue_config` | 更新队列配置 | 返回 updated |
| QC-012 | `test_start_consumer` | 启动消费者 | 返回 started |
| QC-013 | `test_stop_consumer` | 停止消费者 | 返回 stopped |
| QC-014 | `test_list_messages` | 查看消息列表 | 返回分页消息 |
| QC-015 | `test_clear_queue` | 清空队列 | 返回 cleared |
| QC-016 | `test_queue_health` | 队列健康检查 | 返回健康状态 |

### 5.5 服务层测试 (`test_services.py`)

#### 5.5.1 AuthService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AS-001 | `test_authenticate_success` | 认证成功 | 返回 token 和 expires_in |
| AS-002 | `test_authenticate_user_not_found` | 用户不存在 | 抛出 AuthenticationError |
| AS-003 | `test_authenticate_wrong_password` | 密码错误 | 抛出 AuthenticationError |

#### 5.5.2 UserService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| US-001 | `test_get_user_by_id_found` | 用户存在 | 返回 User 对象 |
| US-002 | `test_get_user_by_id_not_found` | 用户不存在 | 返回 None |
| US-003 | `test_create_user_success` | 创建用户成功 | 返回新 User 对象 |
| US-004 | `test_create_user_duplicate` | 用户名重复 | 抛出 DomainException(409) |

#### 5.5.3 QueueService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| QS-001 | `test_init_memory_backend` | 初始化内存队列 | 队列后端为 InMemoryQueue |
| QS-002 | `test_init_file_backend` | 初始化文件队列 | 队列后端为 FileQueue |
| QS-003 | `test_send_message` | 发送消息 | 返回非空 message_id |
| QS-004 | `test_receive_message` | 接收消息 | 返回 MessageDTO |
| QS-005 | `test_acknowledge_message` | 确认消息 | 返回 True |
| QS-006 | `test_reject_message` | 拒绝消息 | 返回 True |
| QS-007 | `test_queue_size` | 队列大小 | 返回正确数量 |
| QS-008 | `test_clear_queue` | 清空队列 | 返回清空数量 |
| QS-009 | `test_send_batch` | 批量发送 | 返回 ID 列表 |
| QS-010 | `test_set_handler` | 设置处理器 | 处理器被调用 |

### 5.6 仓储层测试 (`test_repositories.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| RP-001 | `test_find_by_id_found` | 按 ID 查找存在 | 返回 User |
| RP-002 | `test_find_by_id_not_found` | 按 ID 查找不存在 | 返回 None |
| RP-003 | `test_find_by_username_found` | 按用户名查找存在 | 返回 User |
| RP-004 | `test_find_by_username_not_found` | 按用户名查找不存在 | 返回 None |
| RP-005 | `test_save` | 保存新用户 | 返回带 ID 的 User |
| RP-006 | `test_delete_found` | 删除存在用户 | 返回 True |
| RP-007 | `test_delete_not_found` | 删除不存在用户 | 返回 False |

### 5.7 中间件测试 (`test_middleware.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| MW-001 | `test_get_current_user_valid_token` | 有效 Token | 返回用户信息 |
| MW-002 | `test_get_current_user_invalid_token` | 无效 Token | 返回 401 |
| MW-003 | `test_get_current_user_missing_token` | 缺少 Token | 返回 401 |
| MW-004 | `test_domain_exception_handler` | 领域异常处理 | 返回正确状态码和错误信息 |
| MW-005 | `test_generic_exception_handler` | 通用异常处理 | 返回 500 |

### 5.8 集成测试 (`test_integration.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| IT-001 | `test_full_auth_flow` | 完整认证流程 | 登录 → 获取用户信息 |
| IT-002 | `test_queue_workflow` | 完整队列工作流 | 发送 → 接收 → 确认 |
| IT-003 | `test_error_handling` | 错误处理流程 | 无效请求返回正确错误 |
| IT-004 | `test_health_check` | 健康检查 | 返回 healthy |

---

## 6. 测试覆盖范围

### 6.1 覆盖率目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 行覆盖率 | ≥ 85% | 每行代码至少执行一次 |
| 分支覆盖率 | ≥ 75% | 每个条件分支至少执行一次 |
| 函数覆盖率 | ≥ 90% | 每个函数至少被一个测试覆盖 |
| 模块覆盖率 | 100% | 所有模块都有对应测试文件 |

### 6.2 覆盖率报告生成

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term-missing

# 查看 HTML 报告
open htmlcov/index.html
```

### 6.3 当前覆盖率统计

运行以下命令获取最新覆盖率：

```bash
pytest --cov=src --cov-report=term-missing
```

---

## 7. 运行测试

### 7.1 运行所有测试

```bash
# 运行所有测试
pytest

# 运行所有测试（含覆盖率）
pytest --cov=src --cov-report=term
```

### 7.2 运行特定测试文件

```bash
# 运行消息队列测试
pytest test_message_queue.py -v

# 运行配置测试
pytest test_settings.py -v

# 运行所有测试目录下的测试
pytest tests/ -v
```

### 7.3 运行特定测试类/方法

```bash
# 运行特定测试类
pytest test_message_queue.py::TestMessage -v

# 运行特定测试方法
pytest test_message_queue.py::TestMessage::test_message_creation -v
```

### 7.4 按标记运行

```bash
# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行慢测试
pytest -m slow

# 排除慢测试
pytest -m "not slow"
```

### 7.5 调试测试

```bash
# 显示 print 输出
pytest -s

# 详细输出
pytest -v

# 失败时立即停止
pytest -x

# 显示前 N 个失败详情
pytest --tb=long

# 失败时进入 PDB
pytest --pdb
```

### 7.6 并行测试

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 使用 4 个 CPU 核心并行运行
pytest -n 4
```

---

## 8. 持续集成

### 8.1 CI 配置 (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-mock httpx
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### 8.2 预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

---

## 9. 附录

### 9.1 测试命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 测试文件 | `test_<module_name>.py` | `test_items.py` |
| 测试类 | `Test<ClassName>` | `TestTsItem` |
| 测试方法 | `test_<method_name>_<scenario>` | `test_validate_invalid` |
| Fixture | `<descriptive_name>` | `sample_ts_item` |

### 9.2 测试代码模板

```python
"""Test for <module_name> module."""

import pytest
from <module> import <Class>


class Test<ClassName>:
    """<ClassName> 单元测试"""

    def test_<method>_<scenario>(self):
        """测试 <场景描述>"""
        # Arrange（准备）
        ...

        # Act（执行）
        result = ...

        # Assert（断言）
        assert result == expected
```

### 9.3 常用 Fixtures 模板

```python
# tests/conftest.py
import pytest
from datetime import datetime

from items import TsItem, CourseItem, ArticleItem
from message_queue import Message, InMemoryQueue


@pytest.fixture
def sample_ts_item():
    """创建一个示例 TsItem"""
    return TsItem(
        title="Dr.",
        name="张三",
        email="zhangsan@example.com",
        source_url="https://example.com/teacher/1",
        department="计算机学院",
    )


@pytest.fixture
def sample_message():
    """创建一个示例 Message"""
    return Message(
        topic="test_topic",
        data={"key": "value"},
        source="test_source",
    )


@pytest.fixture
def memory_queue():
    """创建一个内存队列实例"""
    return InMemoryQueue()


@pytest.fixture
def sample_user():
    """创建一个示例用户"""
    from src.models.user import User
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
    )
```

### 9.4 断言风格指南

```python
# ✅ 推荐：使用明确的断言
assert result == expected_value
assert result is None
assert len(items) == 3
assert "error" in response

# ✅ 使用 pytest 内置断言增强
with pytest.raises(ValueError, match="invalid"):
    func_that_raises()

# ❌ 避免：过于复杂的断言
assert not not result  # 应使用 assert result is not None
```

### 9.5 参考资料

| 资源 | 链接 |
|------|------|
| pytest 官方文档 | https://docs.pytest.org/ |
| pytest-cov 文档 | https://pytest-cov.readthedocs.io/ |
| pytest-mock 文档 | https://pytest-mock.readthedocs.io/ |
| FastAPI 测试指南 | https://fastapi.tiangolo.com/tutorial/testing/ |
| Mock 对象指南 | https://docs.python.org/3/library/unittest.mock.html |
# 单元测试文档

**版本**: 1.0.0
**更新日期**: 2024-06-15
**项目**: python-AI 爬虫系统

---

## 目录

1. [测试概述](#1-测试概述)
2. [测试环境](#2-测试环境)
3. [测试框架与工具](#3-测试框架与工具)
4. [测试策略](#4-测试策略)
5. [测试用例设计](#5-测试用例设计)
6. [测试覆盖范围](#6-测试覆盖范围)
7. [运行测试](#7-运行测试)
8. [持续集成](#8-持续集成)
9. [附录](#9-附录)

---

## 1. 测试概述

### 1.1 测试目标

本文档定义了 python-AI 项目的单元测试规范，确保：

- **功能正确性**：所有核心模块按预期工作
- **边界覆盖**：覆盖正常路径、异常路径和边界条件
- **回归防护**：代码变更不会破坏已有功能
- **可维护性**：测试代码清晰、可读、易于维护

### 1.2 测试范围

| 模块 | 测试文件 | 优先级 |
|------|----------|--------|
| 消息队列核心 | `test_message_queue.py` | 高 |
| 配置管理 | `test_settings.py` | 高 |
| 数据模型 (Items) | `test_items.py` | 高 |
| API 控制器 | `test_controllers.py` | 中 |
| 服务层 | `test_services.py` | 中 |
| 仓储层 | `test_repositories.py` | 中 |
| 中间件 | `test_middleware.py` | 低 |
| 集成测试 | `test_integration.py` | 中 |

---

## 2. 测试环境

### 2.1 环境要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.9+ |
| pytest | 7.0+ |
| pytest-cov | 4.0+ |
| pytest-mock | 3.10+ |
| httpx | 0.24+ (用于 FastAPI 测试) |

### 2.2 安装依赖

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-mock httpx

# 安装项目依赖
pip install -r requirements.txt
```

### 2.3 目录结构

```
project-root/
├── tests/                    # 测试目录
│   ├── __init__.py
│   ├── conftest.py           # 共享 fixtures
│   ├── test_items.py         # 数据模型测试
│   ├── test_message_queue.py # 消息队列测试
│   ├── test_settings.py      # 配置测试
│   ├── test_controllers.py   # API 控制器测试
│   ├── test_services.py      # 服务层测试
│   ├── test_repositories.py  # 仓储层测试
│   ├── test_middleware.py    # 中间件测试
│   └── test_integration.py   # 集成测试
├── test_message_queue.py     # 已有测试（消息队列）
├── test_settings.py          # 已有测试（配置）
└── pytest.ini                # pytest 配置
```

---

## 3. 测试框架与工具

### 3.1 测试框架

本项目使用 **pytest** 作为主要测试框架，利用其以下特性：

| 特性 | 用途 |
|------|------|
| `fixture` | 共享测试资源和上下文 |
| `parametrize` | 参数化测试用例 |
| `mark` | 标记和分类测试 |
| `conftest.py` | 全局 fixtures 配置 |
| `tmp_path` | 临时目录（文件队列测试） |
| `capsys` | 捕获标准输出 |
| `monkeypatch` | 动态修改对象 |

### 3.2 辅助工具

| 工具 | 用途 |
|------|------|
| `pytest-cov` | 代码覆盖率统计 |
| `pytest-mock` | Mock 对象管理 |
| `httpx` | FastAPI TestClient 异步支持 |
| `pytest-asyncio` | 异步测试支持 |

### 3.3 pytest 配置 (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests (default)
    integration: Integration tests
    slow: Slow tests that may take longer
    redis: Tests requiring Redis connection
    file_queue: Tests for file queue
```

---

## 4. 测试策略

### 4.1 测试金字塔

```
        ╱╲
       ╱  ╲          E2E 测试 (5%)
      ╱    ╲
     ╱──────╲
    ╱        ╲      集成测试 (20%)
   ╱          ╲
  ╱────────────╲
 ╱              ╲   单元测试 (75%)
╱────────────────╲
```

### 4.2 测试分类

| 类型 | 占比 | 目标 | 运行频率 |
|------|------|------|----------|
| **单元测试** | 75% | 单个函数/类/模块 | 每次提交 |
| **集成测试** | 20% | 模块间交互 | 每次 PR |
| **端到端测试** | 5% | 完整业务流程 | 发布前 |

### 4.3 测试原则

1. **独立性**：每个测试用例独立运行，不依赖其他测试的执行顺序
2. **可重复性**：同一测试多次运行结果一致
3. **快速反馈**：单元测试应在毫秒级完成
4. **单一职责**：每个测试只验证一个行为
5. **可读性**：测试代码应清晰表达测试意图（Given-When-Then）

### 4.4 Mock 策略

| 场景 | Mock 方式 | 说明 |
|------|-----------|------|
| 外部服务 | `unittest.mock` / `pytest-mock` | 模拟 HTTP 请求、数据库等 |
| 时间依赖 | `freezegun` / `monkeypatch` | 固定时间戳 |
| 文件系统 | `tmp_path` fixture | 使用临时目录 |
| 随机数 | `monkeypatch` | 固定随机种子 |

---

## 5. 测试用例设计

### 5.1 消息队列测试 (`test_message_queue.py`)

#### 5.1.1 Message 数据类测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| MQ-001 | `test_message_creation` | 创建 Message 实例 | 所有字段正确初始化 |
| MQ-002 | `test_message_defaults` | 使用默认值创建 | 默认值正确填充 |
| MQ-003 | `test_message_to_dict` | 转换为字典 | 字典包含所有字段 |
| MQ-004 | `test_message_from_dict` | 从字典恢复 | 恢复后的对象与原对象一致 |
| MQ-005 | `test_message_is_expired` | 消息过期判断 | 无 TTL 永不过期，有 TTL 正确判断 |
| MQ-006 | `test_message_mark_processing` | 标记为处理中 | status 变为 'processing' |
| MQ-007 | `test_message_mark_done` | 标记为已完成 | status 变为 'done' |
| MQ-008 | `test_message_mark_failed` | 标记为失败 | status 变为 'failed'，error 字段设置 |
| MQ-009 | `test_message_increment_retry` | 重试计数递增 | retry_count 从 0 变为 1 |
| MQ-010 | `test_message_repr` | 字符串表示 | 包含 topic 和 message_id 前 8 位 |

#### 5.1.2 InMemoryQueue 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| IMQ-001 | `test_init_defaults` | 默认初始化 | maxsize=0, name='default' |
| IMQ-002 | `test_init_with_params` | 带参数初始化 | 参数正确设置 |
| IMQ-003 | `test_put_and_get` | 放入和取出消息 | 消息正确入队和出队 |
| IMQ-004 | `test_get_empty` | 从空队列获取 | 抛出 QueueEmptyError |
| IMQ-005 | `test_put_full` | 向满队列放入 | 抛出 QueueFullError |
| IMQ-006 | `test_priority_ordering` | 优先级排序 | 高优先级先出队 |
| IMQ-007 | `test_topic_filter` | 按主题过滤 | 只获取匹配主题的消息 |
| IMQ-008 | `test_put_batch` | 批量放入 | 所有消息入队，qsize 正确 |
| IMQ-009 | `test_get_batch` | 批量取出 | 取出指定数量消息 |
| IMQ-010 | `test_clear` | 清空队列 | qsize 变为 0 |
| IMQ-011 | `test_is_empty` | 判空 | 空返回 True，非空返回 False |
| IMQ-012 | `test_is_full` | 判满 | 满返回 True，未满返回 False |
| IMQ-013 | `test_get_all` | 获取所有消息 | 全部取出，队列为空 |
| IMQ-014 | `test_iteration` | 迭代器 | 可迭代所有消息 |
| IMQ-015 | `test_context_manager` | 上下文管理器 | 退出后队列清空 |
| IMQ-016 | `test_thread_safety` | 线程安全性 | 多线程并发操作无数据竞争 |
| IMQ-017 | `test_stats` | 统计信息 | 统计字段正确 |

#### 5.1.3 FileQueue 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| FQ-001 | `test_init_and_persistence` | 文件队列持久化 | 重新加载后数据保留 |
| FQ-002 | `test_file_queue_clear` | 清空文件队列 | 队列为空，文件被删除 |
| FQ-003 | `test_file_queue_empty` | 空文件队列 | 判空为 True，get 抛出异常 |

#### 5.1.4 Producer 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| PR-001 | `test_producer_send` | 发送消息 | 消息入队，qsize 增加 |
| PR-002 | `test_producer_send_batch` | 批量发送 | 所有消息入队 |
| PR-003 | `test_producer_with_source` | 带来源标识 | 消息 source 字段正确 |
| PR-004 | `test_producer_stats` | 生产者统计 | total_sent 正确 |

#### 5.1.5 Consumer 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| CO-001 | `test_consumer_consume` | 消费消息 | 消息状态变为 processing |
| CO-002 | `test_consumer_consume_with_topic` | 按主题消费 | 只消费匹配主题的消息 |
| CO-003 | `test_consumer_ack` | 确认消息 | 消息状态变为 done |
| CO-004 | `test_consumer_nack` | 拒绝消息 | 消息状态变为 failed |
| CO-005 | `test_consumer_process` | 处理函数 | handler 被调用，返回 True |
| CO-006 | `test_consumer_process_handler_failure` | 处理函数失败 | 返回 False，消息标记为失败 |
| CO-007 | `test_consumer_process_all` | 处理所有消息 | 所有消息被处理 |
| CO-008 | `test_consumer_stats` | 消费者统计 | 统计字段正确 |

#### 5.1.6 集成测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| INT-001 | `test_producer_consumer_workflow` | 生产者-消费者完整工作流 | 消息正确流转 |
| INT-002 | `test_multi_producer_multi_consumer` | 多生产者多消费者 | 并发操作正确 |
| INT-003 | `test_queue_stats_accuracy` | 队列统计准确性 | 统计数字与实际一致 |
| INT-004 | `test_file_queue_persistence_integration` | 文件队列持久化集成 | 跨进程数据持久化 |
| INT-005 | `test_priority_integration` | 优先级集成 | 高优先级先处理 |
| INT-006 | `test_topic_routing` | 主题路由 | 按主题正确路由 |

### 5.2 配置测试 (`test_settings.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| ST-001 | `test_log_level_exists` | LOG_LEVEL 存在 | settings 模块有 LOG_LEVEL 属性 |
| ST-002 | `test_log_level_default_value` | 默认日志级别 | LOG_LEVEL 是有效的日志级别 |
| ST-003 | `test_settings_importable` | 模块可导入 | 导入无异常，BOT_NAME 正确 |

### 5.3 数据模型测试 (`test_items.py`)

#### 5.3.1 TsItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| TI-001 | `test_ts_item_creation` | 创建 TsItem | 字段正确初始化 |
| TI-002 | `test_ts_item_defaults` | 默认值填充 | crawl_time, status, created_at, item_hash 自动填充 |
| TI-003 | `test_ts_item_to_dict` | 转换为字典 | 过滤掉 None 值 |
| TI-004 | `test_ts_item_to_dict_all` | 转换为字典（全部） | 保留所有字段 |
| TI-005 | `test_ts_item_validate_valid` | 有效数据验证 | 返回 True |
| TI-006 | `test_ts_item_validate_invalid` | 无效数据验证 | 返回 False |
| TI-007 | `test_ts_item_get_full_name` | 获取完整名称 | title - name 格式 |
| TI-008 | `test_ts_item_get_summary` | 获取摘要 | 包含关键信息 |
| TI-009 | `test_ts_item_hash_generation` | 哈希生成 | 相同内容生成相同哈希 |
| TI-010 | `test_ts_item_repr` | 字符串表示 | 包含 title 和 name |

#### 5.3.2 CourseItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| CI-001 | `test_course_item_creation` | 创建 CourseItem | 字段正确初始化 |
| CI-002 | `test_course_item_to_dict` | 转换为字典 | 过滤 None 值 |
| CI-003 | `test_course_item_validate` | 验证 | 有 course_name 返回 True |
| CI-004 | `test_course_item_is_full` | 判断课程已满 | enrolled >= capacity 返回 True |
| CI-005 | `test_course_item_get_occupancy_rate` | 获取占用率 | 返回 0.0 ~ 1.0 之间的值 |
| CI-006 | `test_course_item_get_occupancy_rate_zero_capacity` | 容量为 0 的占用率 | 返回 0.0 |

#### 5.3.3 ArticleItem 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AI-001 | `test_article_item_creation` | 创建 ArticleItem | 字段正确初始化 |
| AI-002 | `test_article_item_to_dict` | 转换为字典 | 过滤 None 值 |
| AI-003 | `test_article_item_validate` | 验证 | 有 title 返回 True |
| AI-004 | `test_article_item_get_tags_list` | 获取标签列表 | 支持字符串和列表格式 |
| AI-005 | `test_article_item_get_attachment_list` | 获取附件列表 | 支持多种格式 |
| AI-006 | `test_article_item_has_attachments` | 判断是否有附件 | 有附件返回 True |

#### 5.3.4 工具函数测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| UT-001 | `test_create_item` | 工厂函数创建 Item | 返回正确类型的 Item |
| UT-002 | `test_create_item_invalid_type` | 不支持的 Item 类型 | 抛出 ValueError |
| UT-003 | `test_merge_items` | 合并两个 Item | override 值覆盖 base 值 |
| UT-004 | `test_merge_items_type_mismatch` | 类型不匹配合并 | 抛出 TypeError |
| UT-005 | `test_batch_validate` | 批量验证 | 返回 valid 和 invalid 分组 |
| UT-006 | `test_items_to_dicts` | 批量转换为字典 | 返回字典列表 |
| UT-007 | `test_deduplicate_items` | 去重 | 重复项被移除 |
| UT-008 | `test_filter_items` | 过滤 | 只返回匹配条件的项 |
| UT-009 | `test_sort_items` | 排序 | 按指定字段排序 |
| UT-010 | `test_export_items_json` | 导出 JSON | 文件内容正确 |
| UT-011 | `test_export_items_csv` | 导出 CSV | 文件内容正确 |

### 5.4 API 控制器测试 (`test_controllers.py`)

#### 5.4.1 认证控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AC-001 | `test_login_success` | 登录成功 | 返回 200 和 token |
| AC-002 | `test_login_invalid_credentials` | 无效凭据 | 返回 401 |
| AC-003 | `test_login_missing_fields` | 缺少必填字段 | 返回 422 |

#### 5.4.2 用户控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| UC-001 | `test_get_user_success` | 获取用户成功 | 返回 200 和用户信息 |
| UC-002 | `test_get_user_not_found` | 用户不存在 | 返回 404 |
| UC-003 | `test_get_user_unauthorized` | 未认证 | 返回 401 |
| UC-004 | `test_create_user_success` | 创建用户成功 | 返回 201 |
| UC-005 | `test_create_user_duplicate` | 用户名重复 | 返回 409 |
| UC-006 | `test_create_user_missing_fields` | 缺少必填字段 | 返回 422 |

#### 5.4.3 队列控制器测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| QC-001 | `test_send_message` | 发送消息 | 返回 200 和 message_id |
| QC-002 | `test_send_message_queue_full` | 队列已满 | 返回 400 |
| QC-003 | `test_send_batch` | 批量发送 | 返回成功/失败计数 |
| QC-004 | `test_receive_message` | 接收消息 | 返回消息内容 |
| QC-005 | `test_receive_message_empty` | 空队列接收 | 返回 null |
| QC-006 | `test_ack_message` | 确认消息 | 返回 acknowledged |
| QC-007 | `test_ack_message_not_found` | 确认不存在的消息 | 返回 404 |
| QC-008 | `test_nack_message` | 拒绝消息 | 返回 nacknowledged |
| QC-009 | `test_get_queue_stats` | 获取队列统计 | 返回统计信息 |
| QC-010 | `test_get_queue_config` | 获取队列配置 | 返回配置信息 |
| QC-011 | `test_update_queue_config` | 更新队列配置 | 返回 updated |
| QC-012 | `test_start_consumer` | 启动消费者 | 返回 started |
| QC-013 | `test_stop_consumer` | 停止消费者 | 返回 stopped |
| QC-014 | `test_list_messages` | 查看消息列表 | 返回分页消息 |
| QC-015 | `test_clear_queue` | 清空队列 | 返回 cleared |
| QC-016 | `test_queue_health` | 队列健康检查 | 返回健康状态 |

### 5.5 服务层测试 (`test_services.py`)

#### 5.5.1 AuthService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| AS-001 | `test_authenticate_success` | 认证成功 | 返回 token 和 expires_in |
| AS-002 | `test_authenticate_user_not_found` | 用户不存在 | 抛出 AuthenticationError |
| AS-003 | `test_authenticate_wrong_password` | 密码错误 | 抛出 AuthenticationError |

#### 5.5.2 UserService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| US-001 | `test_get_user_by_id_found` | 用户存在 | 返回 User 对象 |
| US-002 | `test_get_user_by_id_not_found` | 用户不存在 | 返回 None |
| US-003 | `test_create_user_success` | 创建用户成功 | 返回新 User 对象 |
| US-004 | `test_create_user_duplicate` | 用户名重复 | 抛出 DomainException(409) |

#### 5.5.3 QueueService 测试

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| QS-001 | `test_init_memory_backend` | 初始化内存队列 | 队列后端为 InMemoryQueue |
| QS-002 | `test_init_file_backend` | 初始化文件队列 | 队列后端为 FileQueue |
| QS-003 | `test_send_message` | 发送消息 | 返回非空 message_id |
| QS-004 | `test_receive_message` | 接收消息 | 返回 MessageDTO |
| QS-005 | `test_acknowledge_message` | 确认消息 | 返回 True |
| QS-006 | `test_reject_message` | 拒绝消息 | 返回 True |
| QS-007 | `test_queue_size` | 队列大小 | 返回正确数量 |
| QS-008 | `test_clear_queue` | 清空队列 | 返回清空数量 |
| QS-009 | `test_send_batch` | 批量发送 | 返回 ID 列表 |
| QS-010 | `test_set_handler` | 设置处理器 | 处理器被调用 |

### 5.6 仓储层测试 (`test_repositories.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| RP-001 | `test_find_by_id_found` | 按 ID 查找存在 | 返回 User |
| RP-002 | `test_find_by_id_not_found` | 按 ID 查找不存在 | 返回 None |
| RP-003 | `test_find_by_username_found` | 按用户名查找存在 | 返回 User |
| RP-004 | `test_find_by_username_not_found` | 按用户名查找不存在 | 返回 None |
| RP-005 | `test_save` | 保存新用户 | 返回带 ID 的 User |
| RP-006 | `test_delete_found` | 删除存在用户 | 返回 True |
| RP-007 | `test_delete_not_found` | 删除不存在用户 | 返回 False |

### 5.7 中间件测试 (`test_middleware.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| MW-001 | `test_get_current_user_valid_token` | 有效 Token | 返回用户信息 |
| MW-002 | `test_get_current_user_invalid_token` | 无效 Token | 返回 401 |
| MW-003 | `test_get_current_user_missing_token` | 缺少 Token | 返回 401 |
| MW-004 | `test_domain_exception_handler` | 领域异常处理 | 返回正确状态码和错误信息 |
| MW-005 | `test_generic_exception_handler` | 通用异常处理 | 返回 500 |

### 5.8 集成测试 (`test_integration.py`)

| 测试编号 | 测试名称 | 测试场景 | 预期结果 |
|----------|----------|----------|----------|
| IT-001 | `test_full_auth_flow` | 完整认证流程 | 登录 → 获取用户信息 |
| IT-002 | `test_queue_workflow` | 完整队列工作流 | 发送 → 接收 → 确认 |
| IT-003 | `test_error_handling` | 错误处理流程 | 无效请求返回正确错误 |
| IT-004 | `test_health_check` | 健康检查 | 返回 healthy |

---

## 6. 测试覆盖范围

### 6.1 覆盖率目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 行覆盖率 | ≥ 85% | 每行代码至少执行一次 |
| 分支覆盖率 | ≥ 75% | 每个条件分支至少执行一次 |
| 函数覆盖率 | ≥ 90% | 每个函数至少被一个测试覆盖 |
| 模块覆盖率 | 100% | 所有模块都有对应测试文件 |

### 6.2 覆盖率报告生成

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term-missing

# 查看 HTML 报告
open htmlcov/index.html
```

### 6.3 当前覆盖率统计

运行以下命令获取最新覆盖率：

```bash
pytest --cov=src --cov-report=term-missing
```

---

## 7. 运行测试

### 7.1 运行所有测试

```bash
# 运行所有测试
pytest

# 运行所有测试（含覆盖率）
pytest --cov=src --cov-report=term
```

### 7.2 运行特定测试文件

```bash
# 运行消息队列测试
pytest test_message_queue.py -v

# 运行配置测试
pytest test_settings.py -v

# 运行所有测试目录下的测试
pytest tests/ -v
```

### 7.3 运行特定测试类/方法

```bash
# 运行特定测试类
pytest test_message_queue.py::TestMessage -v

# 运行特定测试方法
pytest test_message_queue.py::TestMessage::test_message_creation -v
```

### 7.4 按标记运行

```bash
# 运行单元测试
pytest -m unit

# 运行集成测试
pytest -m integration

# 运行慢测试
pytest -m slow

# 排除慢测试
pytest -m "not slow"
```

### 7.5 调试测试

```bash
# 显示 print 输出
pytest -s

# 详细输出
pytest -v

# 失败时立即停止
pytest -x

# 显示前 N 个失败详情
pytest --tb=long

# 失败时进入 PDB
pytest --pdb
```

### 7.6 并行测试

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 使用 4 个 CPU 核心并行运行
pytest -n 4
```

---

## 8. 持续集成

### 8.1 CI 配置 (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-mock httpx
          pip install -r requirements.txt
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

### 8.2 预提交钩子

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

---

## 9. 附录

### 9.1 测试命名规范

| 元素 | 规范 | 示例 |
|------|------|------|
| 测试文件 | `test_<module_name>.py` | `test_items.py` |
| 测试类 | `Test<ClassName>` | `TestTsItem` |
| 测试方法 | `test_<method_name>_<scenario>` | `test_validate_invalid` |
| Fixture | `<descriptive_name>` | `sample_ts_item` |

### 9.2 测试代码模板

```python
"""Test for <module_name> module."""

import pytest
from <module> import <Class>


class Test<ClassName>:
    """<ClassName> 单元测试"""

    def test_<method>_<scenario>(self):
        """测试 <场景描述>"""
        # Arrange（准备）
        ...

        # Act（执行）
        result = ...

        # Assert（断言）
        assert result == expected
```

### 9.3 常用 Fixtures 模板

```python
# tests/conftest.py
import pytest
from datetime import datetime

from items import TsItem, CourseItem, ArticleItem
from message_queue import Message, InMemoryQueue


@pytest.fixture
def sample_ts_item():
    """创建一个示例 TsItem"""
    return TsItem(
        title="Dr.",
        name="张三",
        email="zhangsan@example.com",
        source_url="https://example.com/teacher/1",
        department="计算机学院",
    )


@pytest.fixture
def sample_message():
    """创建一个示例 Message"""
    return Message(
        topic="test_topic",
        data={"key": "value"},
        source="test_source",
    )


@pytest.fixture
def memory_queue():
    """创建一个内存队列实例"""
    return InMemoryQueue()


@pytest.fixture
def sample_user():
    """创建一个示例用户"""
    from src.models.user import User
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
    )
```

### 9.4 断言风格指南

```python
# ✅ 推荐：使用明确的断言
assert result == expected_value
assert result is None
assert len(items) == 3
assert "error" in response

# ✅ 使用 pytest 内置断言增强
with pytest.raises(ValueError, match="invalid"):
    func_that_raises()

# ❌ 避免：过于复杂的断言
assert not not result  # 应使用 assert result is not None
```

### 9.5 参考资料

| 资源 | 链接 |
|------|------|
| pytest 官方文档 | https://docs.pytest.org/ |
| pytest-cov 文档 | https://pytest-cov.readthedocs.io/ |
| pytest-mock 文档 | https://pytest-mock.readthedocs.io/ |
| FastAPI 测试指南 | https://fastapi.tiangolo.com/tutorial/testing/ |
| Mock 对象指南 | https://docs.python.org/3/library/unittest.mock.html |
