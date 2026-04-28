# 🕷️ python-AI — 高性能爬虫系统

> 基于 **FastAPI** + **Scrapy** 构建的高性能爬虫系统，提供 RESTful API 接口进行数据采集、消息队列管理和任务调度。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| ⚡ **高性能** | 异步架构 + 消息队列驱动，支持高并发爬取 |
| 🎯 **RESTful API** | 完整的 API 接口，方便集成与二次开发 |
| 📦 **内置消息队列** | 支持内存队列和 Redis 队列两种模式 |
| 🔧 **模块化设计** | API 层、服务层、数据层清晰分离，易于扩展 |
| 🧪 **高测试覆盖率** | 单元测试 + 集成测试，保障代码质量 |

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd python-AI

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python src/main.py
```

> 📖 详细使用说明请参阅 **[docs/USAGE.md](docs/USAGE.md)**

---

## 📚 文档索引

| 文档 | 说明 | 推荐指数 |
|------|------|:--------:|
| [docs/USAGE.md](docs/USAGE.md) | **使用文档** — 安装、配置、运行、API 调用 | ⭐⭐⭐ |
| [docs/API.md](docs/API.md) | **接口文档** — 所有 API 端点详细说明 | ⭐⭐⭐ |
| [docs/TESTING.md](docs/TESTING.md) | **测试文档** — 测试用例与运行指南 | ⭐⭐ |
| [docs/architecture.md](docs/architecture.md) | **架构说明** — 系统架构与设计思路 | ⭐⭐ |
| [docs/interfaces.md](docs/interfaces.md) | **接口规范** — 接口定义与协议 | ⭐⭐ |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | **需求规格** — 功能与非功能需求 | ⭐ |
| [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) | **技术设计** — 详细技术方案 | ⭐ |

---

## 📁 项目结构

```
python-AI/
├── docs/                          # 📄 文档目录
│   ├── USAGE.md                   #   使用文档
│   ├── API.md                     #   接口文档
│   ├── TESTING.md                 #   测试文档
│   ├── architecture.md            #   架构说明
│   ├── interfaces.md              #   接口规范
│   ├── REQUIREMENTS.md            #   需求规格
│   └── TECHNICAL_DESIGN.md        #   技术设计
│
├── src/                           # 💻 源代码
│   ├── main.py                    #   应用入口
│   ├── api/                       #   API 层
│   │   ├── controllers/           #     控制器
│   │   ├── interfaces/            #     接口定义
│   │   ├── middleware/            #     中间件
│   │   └── services/              #     服务层
│   ├── models/                    #   数据模型
│   ├── repositories/              #   数据仓库
│   └── services/                  #   业务服务
│
├── message_queue.py               # 📨 消息队列核心
├── items.py                       # 📦 爬虫数据模型
├── settings.py                    # ⚙️ 配置文件
│
├── tests/                         # 🧪 测试目录
│   ├── conftest.py                #   测试配置
│   ├── test_controllers.py        #   控制器测试
│   ├── test_integration.py        #   集成测试
│   ├── test_items.py              #   数据模型测试
│   ├── test_middleware.py         #   中间件测试
│   ├── test_repositories.py       #   仓库测试
│   └── test_services.py           #   服务测试
│
├── test_message_queue.py          # 📨 消息队列测试
└── test_settings.py               # ⚙️ 配置测试
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_services.py

# 查看测试覆盖率
pytest --cov=src tests/
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **FastAPI** | Web 框架 |
| **Scrapy** | 爬虫引擎 |
| **Pydantic** | 数据验证 |
| **pytest** | 测试框架 |
| **Redis** | 消息队列（可选） |

---

## 📄 许可证

MIT License © 2024

基于 FastAPI 和 Scrapy 的爬虫系统，提供 RESTful API 接口进行数据管理和消息队列操作。

## 快速开始

详细使用说明请参阅 [docs/USAGE.md](docs/USAGE.md)。

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/USAGE.md](docs/USAGE.md) | **使用文档（推荐）** — 安装、配置、运行、API 调用 |
| [docs/API.md](docs/API.md) | 接口 API 详细文档 |
| [docs/architecture.md](docs/architecture.md) | 系统架构说明 |
| [docs/interfaces.md](docs/interfaces.md) | 接口规范定义 |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | 需求规格说明书 |
| [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) | 技术架构设计 |
| [docs/TESTING.md](docs/TESTING.md) | 测试文档 |

## 项目结构

```
python-AI/
├── docs/                          # 文档目录
├── src/                           # 源代码
│   ├── main.py                    # 应用入口
│   ├── api/                       # API 层
│   │   ├── controllers/           # 控制器
│   │   ├── interfaces/            # 接口定义
│   │   ├── middleware/            # 中间件
│   │   └── services/              # 服务层
│   ├── models/                    # 数据模型
│   ├── repositories/              # 数据仓库
│   └── services/                  # 业务服务
├── message_queue.py               # 消息队列核心
├── items.py                       # 爬虫数据模型
├── settings.py                    # 配置文件
├── test_message_queue.py          # 消息队列测试
└── test_settings.py               # 配置测试
```

基于 FastAPI 和 Scrapy 的爬虫系统，提供 RESTful API 接口进行数据管理和消息队列操作。

## 快速开始

详细使用说明请参阅 [docs/USAGE.md](docs/USAGE.md)。

## 文档索引

| 文档 | 说明 |
|------|------|
| [docs/USAGE.md](docs/USAGE.md) | **使用文档（推荐）** — 安装、配置、运行、API 调用 |
| [docs/API.md](docs/API.md) | 接口 API 详细文档 |
| [docs/architecture.md](docs/architecture.md) | 系统架构说明 |
| [docs/interfaces.md](docs/interfaces.md) | 接口规范定义 |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | 需求规格说明书 |
| [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) | 技术架构设计 |
| [docs/TESTING.md](docs/TESTING.md) | 测试文档 |

## 项目结构

```
python-AI/
├── docs/                          # 文档目录
├── src/                           # 源代码
│   ├── main.py                    # 应用入口
│   ├── api/                       # API 层
│   │   ├── controllers/           # 控制器
│   │   ├── interfaces/            # 接口定义
│   │   ├── middleware/            # 中间件
│   │   └── services/              # 服务层
│   ├── models/                    # 数据模型
│   ├── repositories/              # 数据仓库
│   └── services/                  # 业务服务
├── message_queue.py               # 消息队列核心
├── items.py                       # 爬虫数据模型
├── settings.py                    # 配置文件
├── test_message_queue.py          # 消息队列测试
└── test_settings.py               # 配置测试
```
