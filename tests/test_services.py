# -*- coding: utf-8 -*-
"""
Test for services module — 服务层单元测试

覆盖范围：
- AuthService（认证逻辑）
- UserService（用户业务逻辑）
- QueueService（队列服务逻辑）
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.exceptions import DomainException, AuthenticationError
from src.api.services.queue_service import QueueService
from src.api.interfaces.queue_interface import QueueConfig, QueueMessageDTO
from message_queue import InMemoryQueue, FileQueue, Message


# =============================================================================
# AuthService 测试
# =============================================================================

class TestAuthService:
    """AuthService 单元测试"""

    def test_authenticate_success(self, auth_service):
        """测试认证成功"""
        result = auth_service.authenticate("existing_user", "password")
        assert result is not None
        assert "token" in result
        assert result["token"] == "valid-token"
        assert result["expires_in"] == 3600

    def test_authenticate_user_not_found(self, auth_service):
        """测试用户不存在"""
        with pytest.raises(AuthenticationError, match="User not found"):
            auth_service.authenticate("nonexistent_user", "password")

    def test_authenticate_wrong_password(self, auth_service):
        """测试密码错误"""
        with pytest.raises(AuthenticationError, match="Invalid password"):
            auth_service.authenticate("existing_user", "wrong_password")

    def test_authenticate_empty_username(self, auth_service):
        """测试空用户名"""
        with pytest.raises(AuthenticationError, match="User not found"):
            auth_service.authenticate("", "password")

    def test_authenticate_empty_password(self, auth_service):
        """测试空密码"""
        with pytest.raises(AuthenticationError, match="Invalid password"):
            auth_service.authenticate("existing_user", "")

    def test_authenticate_returns_dict(self, auth_service):
        """测试返回值类型"""
        result = auth_service.authenticate("existing_user", "password")
        assert isinstance(result, dict)
        assert "token" in result
        assert "expires_in" in result

    def test_authenticate_with_empty_repository(self):
        """测试空仓库时认证"""
        service = AuthService()
        with pytest.raises(AuthenticationError, match="User not found"):
            service.authenticate("any_user", "password")


# =============================================================================
# UserService 测试
# =============================================================================

class TestUserService:
    """UserService 单元测试"""

    def test_get_user_by_id_found(self, user_service):
        """测试获取存在的用户"""
        user = user_service.get_user_by_id(1)
        assert user is not None
        assert user.username == "existing_user"
        assert user.email == "existing@example.com"

    def test_get_user_by_id_not_found(self, user_service):
        """测试获取不存在的用户"""
        user = user_service.get_user_by_id(999)
        assert user is None

    def test_get_user_by_id_zero(self, user_service):
        """测试获取 ID=0 的用户"""
        user = user_service.get_user_by_id(0)
        assert user is None

    def test_create_user_success(self, user_service):
        """测试创建用户成功"""
        user = user_service.create_user(
            username="new_user",
            email="new@example.com",
            password="secure_password",
        )
        assert user is not None
        assert user.id > 0
        assert user.username == "new_user"
        assert user.email == "new@example.com"
        # 密码应被存储（当前实现是明文占位）
        assert user.password_hash == "secure_password"

    def test_create_user_duplicate_username(self, user_service):
        """测试创建重复用户名"""
        with pytest.raises(DomainException) as exc_info:
            user_service.create_user(
                username="existing_user",
                email="another@example.com",
                password="password123",
            )
        assert exc_info.value.status_code == 409
        assert exc_info.value.error_code == "USERNAME_CONFLICT"
        assert "Username already exists" in str(exc_info.value.message)

    def test_create_user_empty_username(self, user_service):
        """测试创建空用户名（不触发重复检查）"""
        user = user_service.create_user(
            username="",
            email="empty@example.com",
            password="pwd",
        )
        assert user is not None
        assert user.username == ""

    def test_create_user_empty_email(self, user_service):
        """测试创建空邮箱"""
        user = user_service.create_user(
            username="no_email_user",
            email="",
            password="pwd",
        )
        assert user is not None

    def test_create_user_increments_id(self, user_service):
        """测试创建用户 ID 递增"""
        u1 = user_service.create_user("u1", "u1@e.com", "p1")
        u2 = user_service.create_user("u2", "u2@e.com", "p2")
        assert u2.id == u1.id + 1

    def test_get_user_after_create(self, user_service):
        """测试创建后能获取到"""
        created = user_service.create_user("brand_new", "new@e.com", "pwd")
        found = user_service.get_user_by_id(created.id)
        assert found is not None
        assert found.username == "brand_new"


# =============================================================================
# QueueService 测试
# =============================================================================

class TestQueueService:
    """QueueService 单元测试"""

    def test_init_default_config(self):
        """测试默认配置初始化"""
        service = QueueService()
        assert service._config.backend == "memory"
        assert service._config.maxsize == 0
        assert service._config.max_retries == 3
        assert service._queue is not None
        assert isinstance(service._queue, InMemoryQueue)

    def test_init_memory_backend(self):
        """测试内存队列后端"""
        config = QueueConfig(backend="memory", maxsize=100)
        service = QueueService(config)
        assert isinstance(service._queue, InMemoryQueue)

    def test_init_file_backend(self, temp_dir):
        """测试文件队列后端"""
        config = QueueConfig(backend="file", data_dir=temp_dir)
        service = QueueService(config)
        assert isinstance(service._queue, FileQueue)

    def test_send_message(self):
        """测试发送消息"""
        service = QueueService()
        msg_id = service.send_message(body={"key": "value"}, priority=5)
        assert msg_id is not None
        assert isinstance(msg_id, str)
        assert len(msg_id) > 0

    def test_send_message_with_topic(self):
        """测试发送带主题的消息"""
        service = QueueService()
        msg_id = service.send_message(body="test", topic="test_topic")
        assert msg_id is not None

    def test_send_message_with_max_retries(self):
        """测试发送带最大重试次数的消息"""
        service = QueueService()
        msg_id = service.send_message(body="test", max_retries=5)
        assert msg_id is not None

    def test_receive_message(self):
        """测试接收消息"""
        service = QueueService()
        service.send_message(body="hello")
        msg = service.receive_message()
        assert msg is not None
        assert msg.body == "hello"
        assert msg.status == "processing"

    def test_receive_message_empty(self):
        """测试空队列接收"""
        service = QueueService()
        msg = service.receive_message()
        assert msg is None

    def test_receive_message_with_timeout(self):
        """测试带超时的接收"""
        service = QueueService()
        msg = service.receive_message(timeout=0.1)
        assert msg is None

    def test_acknowledge_message(self):
        """测试确认消息"""
        service = QueueService()
        msg_id = service.send_message(body="test")
        msg = service.receive_message()
        assert msg is not None
        result = service.acknowledge_message(msg_id)
        assert result is True

    def test_acknowledge_message_not_found(self):
        """测试确认不存在的消息"""
        service = QueueService()
        result = service.acknowledge_message("nonexistent_id")
        assert result is False

    def test_reject_message(self):
        """测试拒绝消息"""
        service = QueueService()
        msg_id = service.send_message(body="test")
        msg = service.receive_message()
        assert msg is not None
        result = service.reject_message(msg_id, requeue=False)
        assert result is True

    def test_reject_message_not_found(self):
        """测试拒绝不存在的消息"""
        service = QueueService()
        result = service.reject_message("nonexistent_id")
        assert result is False

    def test_reject_message_with_requeue(self):
        """测试拒绝并重新入队"""
        service = QueueService()
        msg_id = service.send_message(body="test", max_retries=3)
        msg = service.receive_message()
        assert msg is not None
        result = service.reject_message(msg_id, requeue=True)
        assert result is True
        # 消息应重新入队
        assert service.queue_size() == 1

    def test_queue_size(self):
        """测试队列大小"""
        service = QueueService()
        assert service.queue_size() == 0
        service.send_message(body="msg1")
        service.send_message(body="msg2")
        assert service.queue_size() == 2

    def test_queue_size_after_receive(self):
        """测试接收后队列大小变化"""
        service = QueueService()
        service.send_message(body="test")
        assert service.queue_size() == 1
        service.receive_message()
        assert service.queue_size() == 0

    def test_clear_queue(self):
        """测试清空队列"""
        service = QueueService()
        service.send_message(body="msg1")
        service.send_message(body="msg2")
        count = service.clear_queue()
        assert count == 2
        assert service.queue_size() == 0

    def test_clear_empty_queue(self):
        """测试清空空队列"""
        service = QueueService()
        count = service.clear_queue()
        assert count == 0

    def test_send_batch(self):
        """测试批量发送"""
        service = QueueService()
        items = ["item1", "item2", "item3"]
        msg_ids = service.send_batch(items)
        assert len(msg_ids) == 3
        assert service.queue_size() == 3

    def test_send_batch_empty(self):
        """测试空批量发送"""
        service = QueueService()
        msg_ids = service.send_batch([])
        assert msg_ids == []

    def test_set_handler(self):
        """测试设置处理器"""
        service = QueueService()
        handler_called = []

        def custom_handler(body):
            handler_called.append(body)
            return True

        service.set_handler(custom_handler)
        service.send_message(body="test_data")
        msg = service.receive_message()
        assert msg is not None
        # 处理消息
        result = service.process_message(msg.msg_id)
        assert result is True
        assert len(handler_called) == 1
        assert handler_called[0] == "test_data"

    def test_handler_failure(self):
        """测试处理器失败"""
        service = QueueService()

        def failing_handler(body):
            raise ValueError("处理失败")

        service.set_handler(failing_handler)
        service.send_message(body="test")
        msg = service.receive_message()
        assert msg is not None
        result = service.process_message(msg.msg_id)
        assert result is False

    def test_is_running_initially_false(self):
        """测试初始运行状态"""
        service = QueueService()
        assert service.is_running is False

    def test_close(self):
        """测试关闭服务"""
        service = QueueService()
        service.send_message(body="test")
        service.close()
        assert service.is_running is False

    def test_priority_ordering(self):
        """测试优先级排序"""
        service = QueueService()
        service.send_message(body="low", priority=1)
        service.send_message(body="high", priority=10)
        service.send_message(body="medium", priority=5)

        msg1 = service.receive_message()
        msg2 = service.receive_message()
        msg3 = service.receive_message()

        assert msg1.body == "high"
        assert msg2.body == "medium"
        assert msg3.body == "low"

    def test_receive_batch(self):
        """测试批量接收"""
        service = QueueService()
        for i in range(5):
            service.send_message(body=f"msg_{i}")

        # 批量接收 3 条
        messages = service.receive_batch(max_count=3)
        assert len(messages) == 3

    def test_get_config(self):
        """测试获取配置"""
        config = QueueConfig(backend="memory", maxsize=50, max_retries=5)
        service = QueueService(config)
        assert service._config.backend == "memory"
        assert service._config.maxsize == 50
        assert service._config.max_retries == 5

    def test_update_config(self):
        """测试更新配置"""
        service = QueueService()
        new_config = QueueConfig(backend="memory", maxsize=200)
        service.update_config(new_config)
        assert service._config.maxsize == 200
