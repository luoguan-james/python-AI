# -*- coding: utf-8 -*-
"""
Test for middleware module — 中间件单元测试

覆盖范围：
- 认证中间件（get_current_user）
- 错误处理中间件（domain_exception_handler, generic_exception_handler）
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.api.middleware.auth_middleware import get_current_user
from src.api.middleware.error_handler import (
    domain_exception_handler,
    generic_exception_handler,
)
from src.services.exceptions import DomainException, AuthenticationError


class TestAuthMiddleware:
    """认证中间件单元测试"""

    @pytest.mark.asyncio
    async def test_valid_token(self):
        """测试有效 Token"""
        # 模拟有效的认证凭据
        mock_credentials = Mock()
        mock_credentials.credentials = "valid-token"

        with patch('src.api.middleware.auth_middleware.HTTPBearer') as mock_bearer:
            mock_security = Mock()
            mock_security.return_value = mock_credentials
            mock_bearer.return_value = mock_security

            # 直接测试 get_current_user 逻辑
            # 由于 get_current_user 依赖 FastAPI 的 Depends，我们测试其核心逻辑
            result = await get_current_user(mock_credentials)
            assert result is not None
            assert "user_id" in result
            assert result["user_id"] == 1
            assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """测试无效 Token"""
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid-token"

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_empty_token(self):
        """测试空 Token"""
        mock_credentials = Mock()
        mock_credentials.credentials = ""

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_none_token(self):
        """测试 None Token"""
        mock_credentials = Mock()
        mock_credentials.credentials = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials)

        assert exc_info.value.status_code == 401


class TestErrorHandler:
    """错误处理中间件单元测试"""

    @pytest.mark.asyncio
    async def test_domain_exception_handler(self):
        """测试领域异常处理"""
        # 创建模拟 Request
        request = Mock(spec=Request)

        # 创建领域异常
        exc = DomainException(
            message="用户名已存在",
            status_code=409,
            error_code="USERNAME_CONFLICT",
        )

        response = await domain_exception_handler(request, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 409

        # 解析响应内容
        import json
        content = json.loads(response.body)
        assert content["error"] == "USERNAME_CONFLICT"
        assert content["message"] == "用户名已存在"
        assert content["status_code"] == 409

    @pytest.mark.asyncio
    async def test_domain_exception_authentication_error(self):
        """测试认证异常处理"""
        request = Mock(spec=Request)
        exc = AuthenticationError("认证失败")

        response = await domain_exception_handler(request, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401

        import json
        content = json.loads(response.body)
        assert content["error"] == "AUTHENTICATION_ERROR"
        assert content["message"] == "认证失败"

    @pytest.mark.asyncio
    async def test_domain_exception_default_values(self):
        """测试领域异常默认值"""
        request = Mock(spec=Request)
        exc = DomainException("默认错误")

        response = await domain_exception_handler(request, exc)
        assert response.status_code == 400

        import json
        content = json.loads(response.body)
        assert content["error"] == "DOMAIN_ERROR"
        assert content["message"] == "默认错误"

    @pytest.mark.asyncio
    async def test_generic_exception_handler(self):
        """测试通用异常处理"""
        request = Mock(spec=Request)
        exc = Exception("未知错误")

        response = await generic_exception_handler(request, exc)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        import json
        content = json.loads(response.body)
        assert content["error"] == "INTERNAL_ERROR"
        assert content["message"] == "An unexpected error occurred."

    @pytest.mark.asyncio
    async def test_generic_exception_with_different_messages(self):
        """测试通用异常不同消息"""
        request = Mock(spec=Request)

        # 无论原始异常消息是什么，通用处理器都应返回固定消息
        for msg in ["error1", "critical failure", ""]:
            exc = Exception(msg)
            response = await generic_exception_handler(request, exc)
            import json
            content = json.loads(response.body)
            assert content["message"] == "An unexpected error occurred."
