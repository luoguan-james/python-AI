# -*- coding: utf-8 -*-
"""
Test for repositories module — 仓储层单元测试

覆盖范围：
- UserRepository 的 CRUD 操作
- 查找（按 ID、按用户名）
- 保存、删除
- 边界条件（不存在、重复等）
"""

import pytest
from datetime import datetime

from src.models.user import User
from src.repositories.user_repository import UserRepository


class TestUserRepository:
    """UserRepository 单元测试"""

    # =========================================================================
    # find_by_id
    # =========================================================================

    def test_find_by_id_found(self, user_repository_with_data):
        """测试按 ID 查找存在的用户"""
        user = user_repository_with_data.find_by_id(1)
        assert user is not None
        assert user.username == 'existing_user'
        assert user.email == 'existing@example.com'

    def test_find_by_id_not_found(self, user_repository):
        """测试按 ID 查找不存在的用户"""
        user = user_repository.find_by_id(999)
        assert user is None

    def test_find_by_id_zero(self, user_repository):
        """测试按 ID=0 查找（不存在）"""
        user = user_repository.find_by_id(0)
        assert user is None

    def test_find_by_id_negative(self, user_repository):
        """测试按负数 ID 查找"""
        user = user_repository.find_by_id(-1)
        assert user is None

    def test_find_by_id_after_save(self, user_repository):
        """测试保存后能通过 ID 找到"""
        user = User(username="new_user", email="new@e.com", password_hash="hash")
        saved = user_repository.save(user)
        found = user_repository.find_by_id(saved.id)
        assert found is not None
        assert found.username == "new_user"

    def test_find_by_id_after_delete(self, user_repository_with_data):
        """测试删除后找不到"""
        user_repository_with_data.delete(1)
        found = user_repository_with_data.find_by_id(1)
        assert found is None

    # =========================================================================
    # find_by_username
    # =========================================================================

    def test_find_by_username_found(self, user_repository_with_data):
        """测试按用户名查找存在的用户"""
        user = user_repository_with_data.find_by_username('existing_user')
        assert user is not None
        assert user.id == 1
        assert user.email == 'existing@example.com'

    def test_find_by_username_not_found(self, user_repository):
        """测试按用户名查找不存在的用户"""
        user = user_repository.find_by_username('nonexistent')
        assert user is None

    def test_find_by_username_empty_string(self, user_repository):
        """测试按空字符串查找"""
        user = user_repository.find_by_username('')
        assert user is None

    def test_find_by_username_case_sensitive(self, user_repository_with_data):
        """测试用户名大小写敏感"""
        # 存储的是 'existing_user'，查找 'EXISTING_USER' 应找不到
        user = user_repository_with_data.find_by_username('EXISTING_USER')
        assert user is None

    def test_find_by_username_multiple_users(self, user_repository):
        """测试多个用户中查找"""
        user1 = User(username="user1", email="u1@e.com", password_hash="h1")
        user2 = User(username="user2", email="u2@e.com", password_hash="h2")
        user_repository.save(user1)
        user_repository.save(user2)

        found = user_repository.find_by_username("user2")
        assert found is not None
        assert found.email == "u2@e.com"

    # =========================================================================
    # save
    # =========================================================================

    def test_save_assigns_id(self, user_repository):
        """测试保存时自动分配 ID"""
        user = User(username="new_user", email="new@e.com", password_hash="hash")
        saved = user_repository.save(user)
        assert saved.id > 0
        assert saved.id == 1  # 第一个用户 ID 应为 1

    def test_save_increments_id(self, user_repository):
        """测试 ID 自增"""
        u1 = user_repository.save(User(username="u1", email="u1@e.com", password_hash="h1"))
        u2 = user_repository.save(User(username="u2", email="u2@e.com", password_hash="h2"))
        assert u2.id == u1.id + 1

    def test_save_returns_user_with_id(self, user_repository):
        """测试 save 返回带 ID 的 User"""
        user = User(username="test", email="t@e.com", password_hash="hash")
        saved = user_repository.save(user)
        assert isinstance(saved, User)
        assert saved.id is not None
        assert saved.username == "test"

    def test_save_persists_all_fields(self, user_repository):
        """测试保存后所有字段完整"""
        now = datetime(2024, 6, 15, 10, 0, 0)
        user = User(
            username="full_user",
            email="full@e.com",
            password_hash="hashed_pwd_123",
            created_at=now,
        )
        saved = user_repository.save(user)
        found = user_repository.find_by_id(saved.id)
        assert found.username == "full_user"
        assert found.email == "full@e.com"
        assert found.password_hash == "hashed_pwd_123"
        assert found.created_at == now

    def test_save_multiple_users(self, user_repository):
        """测试保存多个用户"""
        count = 10
        for i in range(count):
            user = User(username=f"user_{i}", email=f"u{i}@e.com", password_hash=f"h{i}")
            user_repository.save(user)

        # 验证所有用户都能找到
        for i in range(count):
            found = user_repository.find_by_username(f"user_{i}")
            assert found is not None

    # =========================================================================
    # delete
    # =========================================================================

    def test_delete_existing(self, user_repository_with_data):
        """测试删除存在的用户"""
        result = user_repository_with_data.delete(1)
        assert result is True

    def test_delete_not_found(self, user_repository):
        """测试删除不存在的用户"""
        result = user_repository.delete(999)
        assert result is False

    def test_delete_twice(self, user_repository_with_data):
        """测试重复删除"""
        assert user_repository_with_data.delete(1) is True
        assert user_repository_with_data.delete(1) is False  # 第二次删除失败

    def test_delete_zero_id(self, user_repository):
        """测试删除 ID=0 的用户"""
        result = user_repository.delete(0)
        assert result is False

    def test_delete_negative_id(self, user_repository):
        """测试删除负数 ID"""
        result = user_repository.delete(-1)
        assert result is False

    # =========================================================================
    # 边界条件
    # =========================================================================

    def test_empty_repository(self, user_repository):
        """测试空仓库"""
        assert user_repository.find_by_id(1) is None
        assert user_repository.find_by_username("any") is None
        assert user_repository.delete(1) is False

    def test_duplicate_username_allowed(self, user_repository):
        """测试允许相同用户名（仓储层不校验唯一性）"""
        user_repository.save(User(username="same", email="a@e.com", password_hash="h1"))
        user_repository.save(User(username="same", email="b@e.com", password_hash="h2"))
        # 查找时返回第一个匹配的
        found = user_repository.find_by_username("same")
        assert found is not None
        assert found.email == "a@e.com"

    def test_storage_isolation(self, user_repository):
        """测试不同仓库实例隔离"""
        repo1 = UserRepository()
        repo2 = UserRepository()

        repo1.save(User(username="u1", email="u1@e.com", password_hash="h1"))
        # repo2 不应看到 repo1 的数据
        assert repo2.find_by_username("u1") is None
