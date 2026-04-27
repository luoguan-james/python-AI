# -*- coding: utf-8 -*-

"""
队列控制器

提供消息队列的 RESTful API 端点，支持消息的发送、接收、确认、拒绝、
批量操作以及队列监控管理。
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.interfaces.queue_interface import (
    QueueServiceInterface,
    QueueStats,
    QueueMessage,
    QueueConfig,
)
from src.api.middleware.auth_middleware import get_current_user
from src.api.services.queue_service import QueueService

router = APIRouter(prefix="/api/v1/queue", tags=["消息队列"])


def get_queue_service() -> QueueServiceInterface:
    """获取队列服务实例（依赖注入）。

    Returns:
        QueueServiceInterface: 队列服务实例
    """
    return QueueService()


# ──────────────────────────────────────────────
# 请求/响应模型
# ──────────────────────────────────────────────


class SendMessageRequest(BaseModel):
    """发送消息请求体"""

    body: Any
    """消息体内容"""
    priority: int = 0
    """消息优先级（0=普通，数值越大优先级越高）"""
    topic: Optional[str] = None
    """消息主题标签，用于路由过滤"""
    message_id: Optional[str] = None
    """自定义消息ID（不指定则自动生成）"""
    ttl: Optional[int] = None
    """消息生存时间（秒），过期后自动丢弃"""


class SendMessageResponse(BaseModel):
    """发送消息响应体"""

    message_id: str
    """消息唯一标识"""
    status: str = "sent"
    """发送状态"""
    queue_size: int
    """当前队列大小"""


class ReceiveMessageResponse(BaseModel):
    """接收消息响应体"""

    message_id: str
    """消息唯一标识"""
    body: Any
    """消息体内容"""
    priority: int
    """消息优先级"""
    topic: Optional[str] = None
    """消息主题"""
    created_at: str
    """消息创建时间"""
    retry_count: int
    """已重试次数"""


class QueueStatsResponse(BaseModel):
    """队列统计信息响应体"""

    total_sent: int
    """总发送消息数"""
    total_received: int
    """总接收消息数"""
    total_acked: int
    """总确认消息数"""
    total_nacked: int
    """总拒绝消息数"""
    total_failed: int
    """总失败消息数"""
    pending_count: int
    """待处理消息数"""
    processing_count: int
    """处理中消息数"""
    avg_process_time: Optional[float] = None
    """平均处理时间（秒）"""
    error_rate: float
    """错误率（0.0 ~ 1.0）"""
    queue_size: int
    """当前队列大小"""
    is_running: bool
    """消费者是否正在运行"""


class QueueConfigResponse(BaseModel):
    """队列配置响应体"""

    backend: str
    """后端类型（memory/file/redis）"""
    maxsize: int
    """队列最大容量（0=无限制）"""
    max_retries: int
    """最大重试次数"""
    retry_delay: int
    """重试延迟（秒）"""
    batch_size: int
    """批量消费大小"""
    auto_start: bool
    """是否自动启动消费者"""


class BatchSendRequest(BaseModel):
    """批量发送消息请求体"""

    messages: List[SendMessageRequest]
    """消息列表"""


class BatchSendResponse(BaseModel):
    """批量发送消息响应体"""

    message_ids: List[str]
    """发送成功的消息ID列表"""
    success_count: int
    """成功数量"""
    failed_count: int
    """失败数量"""


# ──────────────────────────────────────────────
# 端点定义
# ──────────────────────────────────────────────


@router.post(
    "/send",
    response_model=SendMessageResponse,
    summary="发送消息",
    description="向消息队列发送一条消息，支持优先级和主题标签",
)
async def send_message(
    request: SendMessageRequest,
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """发送一条消息到队列。

    Args:
        request: 消息请求体，包含消息内容、优先级、主题等
        queue_service: 队列服务实例（依赖注入）
        current_user: 当前认证用户信息

    Returns:
        SendMessageResponse: 包含消息ID和发送状态

    Raises:
        HTTPException 400: 消息格式无效或队列已满
        HTTPException 401: 未认证
    """
    try:
        message_id = queue_service.send_message(
            body=request.body,
            priority=request.priority,
            topic=request.topic,
            message_id=request.message_id,
            ttl=request.ttl,
        )
        return SendMessageResponse(
            message_id=message_id,
            status="sent",
            queue_size=queue_service.get_stats().queue_size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post(
    "/send_batch",
    response_model=BatchSendResponse,
    summary="批量发送消息",
    description="批量发送多条消息到队列",
)
async def send_batch(
    request: BatchSendRequest,
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """批量发送多条消息。

    Args:
        request: 批量消息请求体
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        BatchSendResponse: 批量发送结果
    """
    message_ids = []
    failed_count = 0

    for msg in request.messages:
        try:
            mid = queue_service.send_message(
                body=msg.body,
                priority=msg.priority,
                topic=msg.topic,
                message_id=msg.message_id,
                ttl=msg.ttl,
            )
            message_ids.append(mid)
        except Exception:
            failed_count += 1

    return BatchSendResponse(
        message_ids=message_ids,
        success_count=len(message_ids),
        failed_count=failed_count,
    )


@router.get(
    "/receive",
    response_model=Optional[ReceiveMessageResponse],
    summary="接收消息",
    description="从队列接收一条消息（非阻塞），支持按主题过滤",
)
async def receive_message(
    topic: Optional[str] = Query(None, description="按主题过滤消息"),
    timeout: float = Query(0.0, description="等待超时时间（秒），0=不等待"),
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """从队列接收一条消息。

    Args:
        topic: 可选的主题过滤
        timeout: 等待超时时间
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        ReceiveMessageResponse 或 None（队列为空时）
    """
    message = queue_service.receive_message(topic=topic, timeout=timeout)
    if message is None:
        return None

    return ReceiveMessageResponse(
        message_id=message.message_id,
        body=message.body,
        priority=message.priority,
        topic=message.topic,
        created_at=message.created_at.isoformat() if hasattr(message.created_at, 'isoformat') else str(message.created_at),
        retry_count=message.retry_count,
    )


@router.post(
    "/ack/{message_id}",
    summary="确认消息",
    description="确认消息已成功处理，从队列中移除",
)
async def ack_message(
    message_id: str,
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """确认消息处理成功。

    Args:
        message_id: 消息ID
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 确认结果

    Raises:
        HTTPException 404: 消息不存在
    """
    success = queue_service.ack_message(message_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"消息 {message_id} 不存在或已被确认",
        )
    return {"status": "acknowledged", "message_id": message_id}


@router.post(
    "/nack/{message_id}",
    summary="拒绝消息",
    description="拒绝消息处理，可选择重新入队重试",
)
async def nack_message(
    message_id: str,
    requeue: bool = Query(True, description="是否重新入队重试"),
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """拒绝消息处理。

    Args:
        message_id: 消息ID
        requeue: 是否重新入队（用于重试）
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 拒绝结果
    """
    success = queue_service.nack_message(message_id, requeue=requeue)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"消息 {message_id} 不存在或已被处理",
        )
    return {
        "status": "nacknowledged",
        "message_id": message_id,
        "requeued": requeue,
    }


@router.get(
    "/stats",
    response_model=QueueStatsResponse,
    summary="队列统计",
    description="获取消息队列的详细统计信息",
)
async def get_queue_stats(
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """获取队列统计信息。

    Args:
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        QueueStatsResponse: 队列统计信息
    """
    stats = queue_service.get_stats()
    return QueueStatsResponse(
        total_sent=stats.total_sent,
        total_received=stats.total_received,
        total_acked=stats.total_acked,
        total_nacked=stats.total_nacked,
        total_failed=stats.total_failed,
        pending_count=stats.pending_count,
        processing_count=stats.processing_count,
        avg_process_time=stats.avg_process_time,
        error_rate=stats.error_rate,
        queue_size=stats.queue_size,
        is_running=stats.is_running,
    )


@router.get(
    "/config",
    response_model=QueueConfigResponse,
    summary="队列配置",
    description="获取当前队列的配置信息",
)
async def get_queue_config(
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """获取队列配置。

    Args:
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        QueueConfigResponse: 队列配置信息
    """
    config = queue_service.get_config()
    return QueueConfigResponse(
        backend=config.backend,
        maxsize=config.maxsize,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        batch_size=config.batch_size,
        auto_start=config.auto_start,
    )


@router.put(
    "/config",
    summary="更新队列配置",
    description="动态更新队列配置参数",
)
async def update_queue_config(
    config: QueueConfig,
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """更新队列配置。

    Args:
        config: 新的配置参数
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 更新结果
    """
    try:
        queue_service.update_config(config)
        return {"status": "updated", "config": config.dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/start",
    summary="启动消费者",
    description="启动队列消费者，开始处理消息",
)
async def start_consumer(
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """启动消费者。

    Args:
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 启动结果
    """
    queue_service.start_consumer()
    return {"status": "started"}


@router.post(
    "/stop",
    summary="停止消费者",
    description="停止队列消费者",
)
async def stop_consumer(
    wait: bool = Query(True, description="是否等待当前消息处理完成"),
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """停止消费者。

    Args:
        wait: 是否等待当前消息处理完成
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 停止结果
    """
    queue_service.stop_consumer(wait=wait)
    return {"status": "stopped"}


@router.get(
    "/messages",
    summary="查看队列消息",
    description="查看队列中待处理的消息列表（分页）",
)
async def list_messages(
    status: Optional[str] = Query(None, description="按状态过滤: pending/processing/done/failed"),
    topic: Optional[str] = Query(None, description="按主题过滤"),
    skip: int = Query(0, ge=0, description="跳过的消息数"),
    limit: int = Query(20, ge=1, le=100, description="返回的消息数"),
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """查看队列中的消息列表。

    Args:
        status: 消息状态过滤
        topic: 主题过滤
        skip: 分页偏移
        limit: 每页数量
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 消息列表和总数
    """
    messages, total = queue_service.list_messages(
        status=status,
        topic=topic,
        skip=skip,
        limit=limit,
    )
    return {
        "messages": [
            {
                "message_id": m.message_id,
                "body": m.body,
                "priority": m.priority,
                "topic": m.topic,
                "status": m.status,
                "created_at": m.created_at.isoformat() if hasattr(m.created_at, 'isoformat') else str(m.created_at),
                "retry_count": m.retry_count,
            }
            for m in messages
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.delete(
    "/clear",
    summary="清空队列",
    description="清空队列中所有待处理的消息",
)
async def clear_queue(
    queue_service: QueueServiceInterface = Depends(get_queue_service),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """清空队列。

    Args:
        queue_service: 队列服务实例
        current_user: 当前认证用户

    Returns:
        dict: 清空结果
    """
    cleared_count = queue_service.clear()
    return {"status": "cleared", "cleared_count": cleared_count}


@router.get(
    "/health",
    summary="队列健康检查",
    description="检查消息队列服务是否正常运行",
)
async def queue_health(
    queue_service: QueueServiceInterface = Depends(get_queue_service),
):
    """队列健康检查端点（无需认证）。

    Returns:
        dict: 健康状态信息
    """
    try:
        stats = queue_service.get_stats()
        return {
            "status": "healthy",
            "backend": queue_service.get_config().backend,
            "queue_size": stats.queue_size,
            "is_running": stats.is_running,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
