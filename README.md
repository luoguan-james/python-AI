# python-AI — 高性能爬虫系统

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
