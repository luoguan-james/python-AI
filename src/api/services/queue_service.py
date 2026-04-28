"""队列服务实现

提供消息队列的业务逻辑封装，支持多种后端（内存、文件、Redis），
包含消息生产、消费、重试、监控等功能。
"""

import json
import logging
from typing import Any, Callable, Optional, List, Dict
from datetime import datetime

from src.api.interfaces.queue_interface import (
    QueueServiceInterface,
    QueueMessageDTO,
    QueueStats,
    QueueConfig,
    QueueMonitorInterface,
)
from message_queue import (
    BaseQueue,
    BaseQueue,
    BaseQueue,
    BaseQueue,
    BaseQueue,
    InMemoryQueue,
    FileQueue,
    RedisQueue,
    Producer,
    Consumer,
    Message,
    MessageStatus,
    create_queue,
    QueueFullError,
    QueueEmptyError,
)

logger = logging.getLogger(__name__)


class QueueService(QueueServiceInterface):
    """队列服务实现

    封装消息队列的核心操作，提供生产、消费、确认、拒绝等能力。
    支持运行时切换后端，便于开发/测试/生产环境使用不同实现。
    """

    def __init__(self, config: Optional[QueueConfig] = None):
        """初始化队列服务

        Args:
            config: 队列配置，为 None 时使用默认配置（内存队列）
        """
        self._config = config or QueueConfig()
        self._queue: Optional[BaseQueue] = None
        self._producer: Optional[Producer] = None
        self._consumer: Optional[Consumer] = None
        self._running = False
        self._init_queue()

    def _init_queue(self):
        """根据配置初始化队列后端"""
        backend = self._config.backend
        kwargs = {}

        if backend == "memory":
            kwargs["maxsize"] = self._config.maxsize
            self._queue = InMemoryQueue(**kwargs)
        elif backend == "file":
            kwargs["data_dir"] = self._config.data_dir or "/tmp/message_queue"
            self._queue = FileQueue(**kwargs)
        elif backend == "redis":
            kwargs["name"] = self._config.queue_name or "default_queue"
            kwargs["host"] = self._config.redis_host or "localhost"
            kwargs["port"] = self._config.redis_port or 6379
            kwargs["db"] = self._config.redis_db or 0
            kwargs["password"] = self._config.redis_password
            self._queue = RedisQueue(**kwargs)
        else:
            logger.warning(f"未知队列后端 '{backend}'，使用内存队列")
            self._queue = InMemoryQueue(maxsize=self._config.maxsize)

        self._producer = Producer(self._queue)
        self._consumer = Consumer(
            self._queue,
            handler=self._default_handler,
            max_retries=self._config.max_retries,
        )
        logger.info(f"队列服务初始化完成: backend={backend}, maxsize={self._config.maxsize}")

    def _default_handler(self, message: Message) -> bool:
        """默认消息处理器

        Args:
            message: 待处理的消息

        Returns:
            True 表示处理成功，False 表示处理失败
        """
        logger.info(f"默认处理器收到消息: {message}")
        return True

    # ---- 生产者方法 ----

    def send_message(
        self,
        body: Any,
        priority: int = 0,
        topic: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> str:
        """发送消息到队列

        Args:
            body: 消息内容（任意可序列化对象）
            priority: 优先级（数值越大优先级越高）
            topic: 消息主题标签，用于消费者过滤
            max_retries: 最大重试次数，None 使用配置默认值

        Returns:
            消息唯一 ID

        Raises:
            QueueFullError: 队列已满时抛出
        """
        if self._producer is None:
            raise RuntimeError("队列服务未初始化")

        try:
            msg_id = self._producer.send(
                body=body,
                priority=priority,
                topic=topic,
                max_retries=max_retries,
            )
            logger.debug(f"消息发送成功: id={msg_id}, topic={topic}, priority={priority}")
            return msg_id
        except QueueFullError:
            logger.error(f"队列已满，消息发送失败: maxsize={self._config.maxsize}")
            raise
        except Exception as e:
            logger.error(f"消息发送异常: {e}")
            raise

    def send_batch(
        self,
        items: List[Any],
        priority: int = 0,
        topic: Optional[str] = None,
    ) -> List[str]:
        """批量发送消息

        Args:
            items: 消息内容列表
            priority: 优先级
            topic: 消息主题

        Returns:
            消息 ID 列表
        """
        if self._producer is None:
            raise RuntimeError("队列服务未初始化")

        msg_ids = []
        for item in items:
            try:
                msg_id = self.send_message(
                    body=item,
                    priority=priority,
                    topic=topic,
                )
                msg_ids.append(msg_id)
            except QueueFullError:
                logger.warning(f"批量发送中断，已发送 {len(msg_ids)}/{len(items)} 条")
                break
        return msg_ids

    # ---- 消费者方法 ----

    def receive_message(self, timeout: float = 0) -> Optional[MessageDTO]:
        """接收一条消息

        Args:
            timeout: 等待超时秒数（0 表示立即返回）

        Returns:
            消息 DTO，队列为空时返回 None
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._consumer.receive(timeout=timeout)
        if msg is None:
        self,
        max_count: Optional[int] = None,
        timeout: float = 0,
    ) -> List[QueueMessageDTO]:  # type: ignore[override]
        """批量接收消息

        Args:
        Args:
        Args:
        Args:
        Args:
            max_count: 最大接收数量
            timeout: 等待超时

        Returns:
            消息 DTO 列表
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        messages = self._consumer.receive_batch(max_count=max_count, timeout=timeout)
        return [self._message_to_dto(msg) for msg in messages]

    def acknowledge_message(self, msg_id: str) -> bool:
        """确认消息处理完成

        Args:
            msg_id: 消息 ID

        Returns:
            是否确认成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        # 从处理中队列查找消息
        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.ack(msg)

    def reject_message(self, msg_id: str, requeue: bool = False) -> bool:
        """拒绝消息

        Args:
            msg_id: 消息 ID
            requeue: 是否重新入队（用于重试）

        Returns:
            是否拒绝成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.nack(msg, requeue=requeue)

    def process_message(self, msg_id: str) -> bool:
        """处理单条消息（调用注册的处理器）

        Args:
            msg_id: 消息 ID

        Returns:
            处理是否成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.process(msg)

    def set_handler(self, handler: Callable[[Any], bool]):
        """设置消息处理器

        Args:
            handler: 处理函数，接收消息 body，返回 bool 表示成功/失败
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        def wrapped_handler(msg: Message) -> bool:
            try:
                return handler(msg.body)
            except Exception as e:
                logger.error(f"消息处理器异常: {e}")
                return False

        self._consumer._handler = wrapped_handler
        logger.info("消息处理器已更新")

    # ---- 队列管理 ----

    def start_consuming(self, interval: float = 0.1):
        """启动消费循环

        Args:
            interval: 轮询间隔秒数
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        self._running = True
        self._consumer.start(interval=interval)
        logger.info("消费循环已启动")

    def stop_consuming(self, wait: bool = True):
        """停止消费循环

        Args:
            wait: 是否等待当前消息处理完成
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        self._running = False
        self._consumer.stop(wait=wait)
        logger.info("消费循环已停止")

    @property
    def is_running(self) -> bool:
        """消费循环是否正在运行"""
        return self._running

    def queue_size(self) -> int:
        """获取待处理消息数量"""
        if self._queue is None:
            return 0
        return self._queue.size()

    def clear_queue(self) -> int:
        """清空队列

        Returns:
            清空的消息数
        """
        if self._queue is None:
            return 0
        count = self._queue.clear()
        logger.info(f"队列已清空，移除 {count} 条消息")
        return count

    def close(self):
        """关闭队列服务，释放资源"""
        if self._running:
            self.stop_consuming()
        if self._queue is not None:
            self._queue.close()
        logger.info("队列服务已关闭")

    # ---- 内部辅助方法 ----

    def _find_processing_message(self, msg_id: str) -> Optional[Message]:
        """在处理中队列查找消息

        Args:
            msg_id: 消息 ID

        Returns:
            消息对象，未找到返回 None
        """
        if not isinstance(self._queue, InMemoryQueue):
            return self._queue._processing.get(msg_id)

    @staticmethod
    def _message_to_dto(msg: Message) -> QueueMessageDTO:
        """将 Message 对象转换为 MessageDTO

        Args:
        Args:
        Args:
        Returns:
            消息 DTO
        """
        return QueueMessageDTO(
            msg_id=msg.msg_id,
            body=msg.body,
            status=msg.status.value,
            status=msg.status.value,
            status=msg.status.value,
            status=msg.status.value,
            status=msg.status.value,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            retry_count=msg.retry_count,
            max_retries=msg.max_retries,
            error=msg.error,
            priority=msg.priority,
        )


class QueueMonitor(QueueMonitorInterface):
    """队列监控服务

    提供队列运行状态、统计信息、健康检查等监控能力。
    """

    def __init__(self, queue_service: QueueService):
        """初始化监控服务

        Args:
            queue_service: 队列服务实例
        """
        self._service = queue_service
        self._start_time = datetime.now()

    def get_stats(self) -> QueueStats:
        """获取队列统计信息"""
        queue = self._service._queue
        pending = queue.size() if queue else 0
        processing = 0
        completed = 0
        failed = 0

        if isinstance(queue, InMemoryQueue):
            processing = queue.processing_count
            completed = queue.history_count
            # 从历史中统计失败数
            failed = sum(
                1 for m in queue._history
                if m.status == MessageStatus.FAILED
            )

        uptime = (datetime.now() - self._start_time).total_seconds()

        return QueueStats(
            pending_count=pending,
            processing_count=processing,
            completed_count=completed,
            failed_count=failed,
            is_running=self._service.is_running,
            backend=self._service._config.backend,
            uptime_seconds=uptime,
        )

    def health_check(self) -> Dict[str, Any]:
        """健康检查

        Returns:
            健康状态字典
        """
        stats = self.get_stats()
        is_healthy = True
        issues = []

        # 检查队列是否可用
        if self._service._queue is None:
            is_healthy = False
            issues.append("队列未初始化")

        # 检查待处理消息积压
        if stats.pending_count > 1000:
            issues.append(f"消息积压: {stats.pending_count} 条待处理")

        # 检查失败率
        total = stats.completed_count + stats.failed_count
        if total > 0:
            fail_rate = stats.failed_count / total
            if fail_rate > 0.1:
                issues.append(f"失败率过高: {fail_rate:.1%}")

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": stats.uptime_seconds,
            "issues": issues,
            "stats": {
                "pending": stats.pending_count,
                "processing": stats.processing_count,
                "completed": stats.completed_count,
                "failed": stats.failed_count,
                "is_running": stats.is_running,
                "backend": stats.backend,
            },
        }


# 全局单例
_default_queue_service: Optional[QueueService] = None


def get_queue_service(config: Optional[QueueConfig] = None) -> QueueService:
    """获取全局队列服务实例（单例模式）

    Args:
        config: 队列配置，仅在首次初始化时生效

    Returns:
        队列服务实例
    """
    global _default_queue_service
    if _default_queue_service is None:
        _default_queue_service = QueueService(config)
    return _default_queue_service


def get_queue_monitor() -> QueueMonitor:
    """获取全局队列监控实例

    Returns:
        队列监控实例
    """
    service = get_queue_service()
    return QueueMonitor(service)
"""队列服务实现

提供消息队列的业务逻辑封装，支持多种后端（内存、文件、Redis），
包含消息生产、消费、重试、监控等功能。
"""

import json
import logging
from typing import Any, Callable, Optional, List, Dict
from datetime import datetime

from src.api.interfaces.queue_interface import (
    QueueServiceInterface,
    QueueMonitorInterface,
    MessageDTO,
    QueueStats,
    QueueConfig,
)
from message_queue import (
    BaseQueue,
    InMemoryQueue,
    FileQueue,
    RedisQueue,
    Producer,
    Consumer,
    Message,
    MessageStatus,
    create_queue,
    QueueFullError,
    QueueEmptyError,
)

logger = logging.getLogger(__name__)


class QueueService(QueueServiceInterface):
    """队列服务实现

    封装消息队列的核心操作，提供生产、消费、确认、拒绝等能力。
    支持运行时切换后端，便于开发/测试/生产环境使用不同实现。
    """

    def __init__(self, config: Optional[QueueConfig] = None):
        """初始化队列服务

        Args:
            config: 队列配置，为 None 时使用默认配置（内存队列）
        """
        self._config = config or QueueConfig()
        self._queue: Optional[BaseQueue] = None
        self._producer: Optional[Producer] = None
        self._consumer: Optional[Consumer] = None
        self._running = False
        self._init_queue()

    def _init_queue(self):
        """根据配置初始化队列后端"""
        backend = self._config.backend
        kwargs = {}

        if backend == "memory":
            kwargs["maxsize"] = self._config.maxsize
            self._queue = InMemoryQueue(**kwargs)
        elif backend == "file":
            kwargs["data_dir"] = self._config.data_dir or "/tmp/message_queue"
            self._queue = FileQueue(**kwargs)
        elif backend == "redis":
            kwargs["name"] = self._config.queue_name or "default_queue"
            kwargs["host"] = self._config.redis_host or "localhost"
            kwargs["port"] = self._config.redis_port or 6379
            kwargs["db"] = self._config.redis_db or 0
            kwargs["password"] = self._config.redis_password
            self._queue = RedisQueue(**kwargs)
        else:
            logger.warning(f"未知队列后端 '{backend}'，使用内存队列")
            self._queue = InMemoryQueue(maxsize=self._config.maxsize)

        self._producer = Producer(self._queue)
        self._consumer = Consumer(
            self._queue,
            handler=self._default_handler,
            max_retries=self._config.max_retries,
        )
        logger.info(f"队列服务初始化完成: backend={backend}, maxsize={self._config.maxsize}")

    def _default_handler(self, message: Message) -> bool:
        """默认消息处理器

        Args:
            message: 待处理的消息

        Returns:
            True 表示处理成功，False 表示处理失败
        """
        logger.info(f"默认处理器收到消息: {message}")
        return True

    # ---- 生产者方法 ----

    def send_message(
        self,
        body: Any,
        priority: int = 0,
        topic: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> str:
        """发送消息到队列

        Args:
            body: 消息内容（任意可序列化对象）
            priority: 优先级（数值越大优先级越高）
            topic: 消息主题标签，用于消费者过滤
            max_retries: 最大重试次数，None 使用配置默认值

        Returns:
            消息唯一 ID

        Raises:
            QueueFullError: 队列已满时抛出
        """
        if self._producer is None:
            raise RuntimeError("队列服务未初始化")

        try:
            msg_id = self._producer.send(
                body=body,
                priority=priority,
                topic=topic,
                max_retries=max_retries,
            )
            logger.debug(f"消息发送成功: id={msg_id}, topic={topic}, priority={priority}")
            return msg_id
        except QueueFullError:
            logger.error(f"队列已满，消息发送失败: maxsize={self._config.maxsize}")
            raise
        except Exception as e:
            logger.error(f"消息发送异常: {e}")
            raise

    def send_batch(
        self,
        items: List[Any],
        priority: int = 0,
        topic: Optional[str] = None,
    ) -> List[str]:
        """批量发送消息

        Args:
            items: 消息内容列表
            priority: 优先级
            topic: 消息主题

        Returns:
            消息 ID 列表
        """
        if self._producer is None:
            raise RuntimeError("队列服务未初始化")

        msg_ids = []
        for item in items:
            try:
                msg_id = self.send_message(
                    body=item,
                    priority=priority,
                    topic=topic,
                )
                msg_ids.append(msg_id)
            except QueueFullError:
                logger.warning(f"批量发送中断，已发送 {len(msg_ids)}/{len(items)} 条")
                break
        return msg_ids

    # ---- 消费者方法 ----

    def receive_message(self, timeout: float = 0) -> Optional[MessageDTO]:
        """接收一条消息

        Args:
            timeout: 等待超时秒数（0 表示立即返回）

        Returns:
            消息 DTO，队列为空时返回 None
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._consumer.receive(timeout=timeout)
        if msg is None:
            return None
        return self._message_to_dto(msg)

    def receive_batch(
        self,
        max_count: Optional[int] = None,
        timeout: float = 0,
    ) -> List[MessageDTO]:
        """批量接收消息

        Args:
            max_count: 最大接收数量
            timeout: 等待超时

        Returns:
            消息 DTO 列表
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        messages = self._consumer.receive_batch(max_count=max_count, timeout=timeout)
        return [self._message_to_dto(msg) for msg in messages]

    def acknowledge_message(self, msg_id: str) -> bool:
        """确认消息处理完成

        Args:
            msg_id: 消息 ID

        Returns:
            是否确认成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        # 从处理中队列查找消息
        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.ack(msg)

    def reject_message(self, msg_id: str, requeue: bool = False) -> bool:
        """拒绝消息

        Args:
            msg_id: 消息 ID
            requeue: 是否重新入队（用于重试）

        Returns:
            是否拒绝成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.nack(msg, requeue=requeue)

    def process_message(self, msg_id: str) -> bool:
        """处理单条消息（调用注册的处理器）

        Args:
            msg_id: 消息 ID

        Returns:
            处理是否成功
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        msg = self._find_processing_message(msg_id)
        if msg is None:
            logger.warning(f"未找到处理中的消息: {msg_id}")
            return False
        return self._consumer.process(msg)

    def set_handler(self, handler: Callable[[Any], bool]):
        """设置消息处理器

        Args:
            handler: 处理函数，接收消息 body，返回 bool 表示成功/失败
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        def wrapped_handler(msg: Message) -> bool:
            try:
                return handler(msg.body)
            except Exception as e:
                logger.error(f"消息处理器异常: {e}")
                return False

        self._consumer._handler = wrapped_handler
        logger.info("消息处理器已更新")

    # ---- 队列管理 ----

    def start_consuming(self, interval: float = 0.1):
        """启动消费循环

        Args:
            interval: 轮询间隔秒数
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        self._running = True
        self._consumer.start(interval=interval)
        logger.info("消费循环已启动")

    def stop_consuming(self, wait: bool = True):
        """停止消费循环

        Args:
            wait: 是否等待当前消息处理完成
        """
        if self._consumer is None:
            raise RuntimeError("队列服务未初始化")

        self._running = False
        self._consumer.stop(wait=wait)
        logger.info("消费循环已停止")

    @property
    def is_running(self) -> bool:
        """消费循环是否正在运行"""
        return self._running

    def queue_size(self) -> int:
        """获取待处理消息数量"""
        if self._queue is None:
            return 0
        return self._queue.size()

    def clear_queue(self) -> int:
        """清空队列

        Returns:
            清空的消息数
        """
        if self._queue is None:
            return 0
        count = self._queue.clear()
        logger.info(f"队列已清空，移除 {count} 条消息")
        return count

    def close(self):
        """关闭队列服务，释放资源"""
        if self._running:
            self.stop_consuming()
        if self._queue is not None:
            self._queue.close()
        logger.info("队列服务已关闭")

    # ---- 内部辅助方法 ----

    def _find_processing_message(self, msg_id: str) -> Optional[Message]:
        """在处理中队列查找消息

        Args:
            msg_id: 消息 ID

        Returns:
            消息对象，未找到返回 None
        """
        if not isinstance(self._queue, InMemoryQueue):
            logger.warning(f"当前队列后端不支持按 ID 查找处理中消息")
            return None

        with self._queue._lock:
            return self._queue._processing.get(msg_id)

    @staticmethod
    def _message_to_dto(msg: Message) -> MessageDTO:
        """将 Message 对象转换为 MessageDTO

        Args:
            msg: 消息对象

        Returns:
            消息 DTO
        """
        return MessageDTO(
            msg_id=msg.msg_id,
            body=msg.body,
            status=msg.status.value,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            retry_count=msg.retry_count,
            max_retries=msg.max_retries,
            error=msg.error,
            priority=msg.priority,
        )


class QueueMonitor(QueueMonitorInterface):
    """队列监控服务

    提供队列运行状态、统计信息、健康检查等监控能力。
    """

    def __init__(self, queue_service: QueueService):
        """初始化监控服务

        Args:
            queue_service: 队列服务实例
        """
        self._service = queue_service
        self._start_time = datetime.now()

    def get_stats(self) -> QueueStats:
        """获取队列统计信息"""
        queue = self._service._queue
        pending = queue.size() if queue else 0
        processing = 0
        completed = 0
        failed = 0

        if isinstance(queue, InMemoryQueue):
            processing = queue.processing_count
            completed = queue.history_count
            # 从历史中统计失败数
            failed = sum(
                1 for m in queue._history
                if m.status == MessageStatus.FAILED
            )

        uptime = (datetime.now() - self._start_time).total_seconds()

        return QueueStats(
            pending_count=pending,
            processing_count=processing,
            completed_count=completed,
            failed_count=failed,
            is_running=self._service.is_running,
            backend=self._service._config.backend,
            uptime_seconds=uptime,
        )

    def health_check(self) -> Dict[str, Any]:
        """健康检查

        Returns:
            健康状态字典
        """
        stats = self.get_stats()
        is_healthy = True
        issues = []

        # 检查队列是否可用
        if self._service._queue is None:
            is_healthy = False
            issues.append("队列未初始化")

        # 检查待处理消息积压
        if stats.pending_count > 1000:
            issues.append(f"消息积压: {stats.pending_count} 条待处理")

        # 检查失败率
        total = stats.completed_count + stats.failed_count
        if total > 0:
            fail_rate = stats.failed_count / total
            if fail_rate > 0.1:
                issues.append(f"失败率过高: {fail_rate:.1%}")

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": stats.uptime_seconds,
            "issues": issues,
            "stats": {
                "pending": stats.pending_count,
                "processing": stats.processing_count,
                "completed": stats.completed_count,
                "failed": stats.failed_count,
                "is_running": stats.is_running,
                "backend": stats.backend,
            },
        }


# 全局单例
_default_queue_service: Optional[QueueService] = None


def get_queue_service(config: Optional[QueueConfig] = None) -> QueueService:
    """获取全局队列服务实例（单例模式）

    Args:
        config: 队列配置，仅在首次初始化时生效

    Returns:
        队列服务实例
    """
    global _default_queue_service
    if _default_queue_service is None:
        _default_queue_service = QueueService(config)
    return _default_queue_service


def get_queue_monitor() -> QueueMonitor:
    """获取全局队列监控实例

    Returns:
        队列监控实例
    """
    service = get_queue_service()
    return QueueMonitor(service)
