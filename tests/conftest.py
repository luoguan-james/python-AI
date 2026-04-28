# -*- coding: utf-8 -*-
"""
conftest.py — 共享 Fixtures

提供所有测试模块通用的 Fixture 定义，包括：
- 数据模型 Fixtures（TsItem, CourseItem, ArticleItem）
- 消息队列 Fixtures（Message, InMemoryQueue, FileQueue）
- 服务层 Fixtures（UserService, AuthService, QueueService）
- 仓储层 Fixtures（UserRepository）
- API 测试 Fixtures（TestClient）
"""

import pytest
import tempfile
import os
from datetime import datetime
from typing import Dict, Any

from items import TsItem, CourseItem, ArticleItem
from message_queue import Message, InMemoryQueue, FileQueue, Producer, Consumer
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.exceptions import DomainException, AuthenticationError


# =============================================================================
# 数据模型 Fixtures
# =============================================================================

@pytest.fixture
def sample_ts_item() -> TsItem:
    """创建一个完整的 TsItem 示例"""
    return TsItem(
        title="Dr.",
        name="张三",
        gender="男",
        age=35,
        email="zhangsan@example.com",
        phone="13800138000",
        department="计算机学院",
        major="计算机科学与技术",
        grade="教授",
        avatar_url="https://example.com/avatar/1.jpg",
        profile_url="https://example.com/teacher/1",
        source_url="https://example.com/teacher/1",
        source_site="example.edu",
        status="active",
    )


@pytest.fixture
def minimal_ts_item() -> TsItem:
    """创建一个最小字段的 TsItem（仅必填字段）"""
    return TsItem(
        title="学生",
        name="李四",
    )


@pytest.fixture
def sample_course_item() -> CourseItem:
    """创建一个完整的 CourseItem 示例"""
    return CourseItem(
        course_id="CS101",
        course_name="数据结构与算法",
        teacher_name="张三",
        teacher_id="T001",
        department="计算机学院",
        semester="2024-2025-1",
        credits=4,
        hours=64,
        schedule="周一 1-2 节",
        location="教学楼 A101",
        capacity=120,
        enrolled=100,
        description="本课程介绍基本数据结构和算法设计方法",
        syllabus_url="https://example.com/syllabus/CS101.pdf",
        source_url="https://example.com/course/CS101",
    )


@pytest.fixture
def sample_article_item() -> ArticleItem:
    """创建一个完整的 ArticleItem 示例"""
    return ArticleItem(
        article_id="ART001",
        title="关于2024年秋季学期选课的通知",
        author="教务处",
        publish_date="2024-06-01",
        content="<p>各位同学：2024年秋季学期选课即将开始...</p>",
        summary="2024年秋季学期选课通知",
        tags="选课,教务,通知",
        category="教务公告",
        view_count=1500,
        attachment_urls='["https://example.com/attach/schedule.pdf"]',
        cover_image_url="https://example.com/cover/news.jpg",
        source_url="https://example.com/article/ART001",
        source_site="example.edu",
    )


# =============================================================================
# 消息队列 Fixtures
# =============================================================================

@pytest.fixture
def sample_message() -> Message:
    """创建一个示例 Message"""
    return Message(
        body={"name": "张三", "age": 25, "department": "计算机学院"},
        priority=5,
    )


@pytest.fixture
def memory_queue() -> InMemoryQueue:
    """创建一个无限制的内存队列"""
    return InMemoryQueue(maxsize=0)


@pytest.fixture
def bounded_queue() -> InMemoryQueue:
    """创建一个有容量限制的内存队列（容量=5）"""
    return InMemoryQueue(maxsize=5)


@pytest.fixture
def file_queue() -> FileQueue:
    """创建一个临时文件队列（自动清理）"""
    tmpdir = tempfile.mkdtemp()
    q = FileQueue(data_dir=tmpdir)
    yield q
    # 清理临时目录
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def producer(memory_queue: InMemoryQueue) -> Producer:
    """创建一个生产者（绑定到内存队列）"""
    return Producer(memory_queue, name="test_producer")


@pytest.fixture
def consumer(memory_queue: InMemoryQueue) -> Consumer:
    """创建一个消费者（绑定到内存队列）"""
    return Consumer(memory_queue, name="test_consumer")


# =============================================================================
# 仓储层 Fixtures
# =============================================================================

@pytest.fixture
def user_repository() -> UserRepository:
    """创建一个空的 UserRepository"""
    return UserRepository()


@pytest.fixture
def user_repository_with_data(user_repository: UserRepository) -> UserRepository:
    """创建一个包含预置数据的 UserRepository"""
    user = User(username="existing_user", email="existing@example.com", password_hash="hash123")
    user_repository.save(user)
    return user_repository


@pytest.fixture
def sample_user() -> User:
    """创建一个示例 User 对象"""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password_123",
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )


# =============================================================================
# 服务层 Fixtures
# =============================================================================

@pytest.fixture
def user_service(user_repository_with_data: UserRepository) -> UserService:
    """创建一个 UserService 实例（带预置数据）"""
    service = UserService()
    service.user_repo = user_repository_with_data
    return service


@pytest.fixture
def auth_service(user_repository_with_data: UserRepository) -> AuthService:
    """创建一个 AuthService 实例（带预置数据）"""
    service = AuthService()
    service.user_repo = user_repository_with_data
    return service


# =============================================================================
# API 测试 Fixtures
# =============================================================================

@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """返回有效的认证请求头"""
    return {"Authorization": "Bearer valid-token"}


@pytest.fixture
def invalid_auth_headers() -> Dict[str, str]:
    """返回无效的认证请求头"""
    return {"Authorization": "Bearer invalid-token"}


# =============================================================================
# 辅助 Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """创建一个临时目录（自动清理）"""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)
