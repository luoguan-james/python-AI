# python-AI

## 项目概述

python-AI 是一个基于 Scrapy 框架的爬虫项目，用于爬取教师/学生（TS）信息、课程信息和文章信息。项目提供了完整的数据模型定义、数据库 ORM 模型以及配置管理。

## 项目结构

```
python-AI/
├── README.md           # 项目说明文档
├── items.py            # Scrapy 数据模型定义（TsItem, CourseItem, ArticleItem）
├── models.py           # SQLAlchemy ORM 数据库模型（TsModel, CourseModel, ArticleModel）
├── settings.py         # Scrapy 项目配置
└── test_settings.py    # 配置模块测试
```

## 核心模块

### 1. items.py - 数据模型

定义了三种 Scrapy Item 数据模型：

- **TsItem**: 教师/学生信息爬虫数据模型
  - 基本信息：title, stu
  - 扩展信息：name, gender, age, email, phone, department, major, grade, avatar_url, profile_url
  - 时间信息：created_at, updated_at, crawl_time
  - 元数据：source_url, source_site, item_hash, status
  - 自动填充：crawl_time, status, created_at, item_hash
  - 提供方法：get_full_name(), to_dict(), to_dict_all(), validate(), get_summary()

- **CourseItem**: 课程信息爬虫数据模型
  - 字段：course_id, course_name, teacher_name, teacher_id, department, semester, credits, hours, schedule, location, capacity, enrolled, description, syllabus_url, source_url, crawl_time
  - 自动填充：crawl_time

- **ArticleItem**: 文章信息爬虫数据模型
  - 字段：article_id, title, author, publish_date, content, summary, tags, category, url, source_url, crawl_time
  - 自动填充：crawl_time

### 2. models.py - 数据库模型

定义了三种 SQLAlchemy ORM 模型，对应 items.py 中的数据模型：

- **TsModel**: 对应 TsItem，存储教师/学生信息
  - 表名：ts_items
  - 包含完整字段映射，支持索引和唯一约束
  - 提供 to_dict() 方法

- **CourseModel**: 对应 CourseItem，存储课程信息
  - 表名：course_items
  - 包含完整字段映射，支持索引
  - 提供 to_dict() 方法

- **ArticleModel**: 对应 ArticleItem，存储文章信息
  - 表名：article_items
  - 包含完整字段映射，支持索引
  - 提供 to_dict() 方法

### 3. settings.py - 项目配置

Scrapy 项目配置文件，包含：
- BOT_NAME: TS
- SPIDER_MODULES / NEWSPIDER_MODULE: TS.spiders
- ROBOTSTXT_OBEY: True
- ITEM_PIPELINES: TS.pipelines.TsPipeline
- LOG_LEVEL: INFO

### 4. test_settings.py - 配置测试

使用 pytest 框架测试 settings 模块：
- test_log_level_exists: 验证 LOG_LEVEL 存在
- test_log_level_default_value: 验证 LOG_LEVEL 为有效值
- test_settings_importable: 验证模块可正常导入

## 数据流

1. Scrapy Spider 爬取网页数据
2. 数据填充到 Item 对象（TsItem / CourseItem / ArticleItem）
3. Item Pipeline 处理数据（清洗、验证、去重）
4. 数据持久化到数据库（通过 SQLAlchemy ORM 模型）

## 开发指南

### 环境要求

- Python 3.7+
- Scrapy
- SQLAlchemy
- pytest

### 运行测试

```bash
cd /root/workspace/test-projects/python-AI
python -m pytest test_settings.py -v
```

### 扩展数据模型

1. 在 items.py 中定义新的 Item 类
2. 在 models.py 中定义对应的 ORM 模型
3. 在 settings.py 中配置对应的 Pipeline
