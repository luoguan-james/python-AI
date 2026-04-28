"""队列服务接口定义。

定义消息队列的抽象接口，确保 API 层与消息队列实现之间的契约一致性。
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class QueueMessageDTO:
    """队列消息数据传输对象"""
    msg_id: str
    body: Any
    status: str
    created_at: str
    updated_at: str
    retry_count: int
    max_retries: int
    error: Optional[str]
    priority: int


class QueueServiceInterface(ABC):
    """消息队列服务接口"""

    @abstractmethod
    def send_message(self, body: Any, priority: int = 0,
                     topic: Optional[str] = None,
                     max_retries: int = 3) -> str:
        """发送消息到队列。

        Args:
            body: 消息内容（任意可序列化对象）
            priority: 优先级（数值越大优先级越高）
            topic: 消息主题标签，用于路由过滤
            max_retries: 最大重试次数

        Returns:
            消息唯一ID

        Raises:
            QueueFullError: 队列已满时抛出
        """
        ...

    @abstractmethod
    def receive_message(self, timeout: float = 0,
                        topic: Optional[str] = None) -> Optional[QueueMessageDTO]:
        """从队列接收一条消息。

        Args:
            timeout: 等待超时秒数（0表示立即返回）
            topic: 按主题过滤

        Returns:
            消息对象，队列为空时返回 None
        """
        ...

    @abstractmethod
    def acknowledge_message(self, msg_id: str) -> bool:
        """确认消息处理完成。

        Args:
            msg_id: 消息ID

        Returns:
            确认成功返回 True
        """
        ...

    @abstractmethod
    def reject_message(self, msg_id: str, requeue: bool = False,
                       error: Optional[str] = None) -> bool:
        """拒绝消息。

        Args:
            msg_id: 消息ID
            requeue: 是否重新入队（用于重试）
            error: 错误信息

        Returns:
            拒绝成功返回 True
        """
        ...

    @abstractmethod
    def queue_size(self) -> int:
        """返回队列中待处理消息数量。"""
        ...

    @abstractmethod
    def clear_queue(self) -> int:
        """清空队列，返回清空的消息数。"""
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """获取队列统计信息。

        Returns:
            包含 pending, processing, completed, failed 计数的字典
        """
        ...


class QueueConsumerInterface(ABC):
    """队列消费者接口"""

    @abstractmethod
    def start_consuming(self, handler: Callable[[QueueMessageDTO], bool],
                        interval: float = 0.1):
        """启动消费循环。

        Args:
            handler: 消息处理回调函数，接收消息返回是否成功
            interval: 轮询间隔（秒）
        """
        ...

    @abstractmethod
    def stop_consuming(self, wait: bool = True):
        """停止消费循环。

        Args:
            wait: 是否等待当前处理完成
        """
        ...

    @abstractmethod
    def is_running(self) -> bool:
        """消费者是否正在运行。"""
        ...
"""队列服务接口定义。

定义消息队列的抽象接口，确保 API 层与消息队列实现之间的契约一致性。
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class QueueMessageDTO:
    """队列消息数据传输对象"""
    msg_id: str
    body: Any
    status: str
    created_at: str
    updated_at: str
    retry_count: int
    max_retries: int
    error: Optional[str]
    priority: int


class QueueServiceInterface(ABC):
    """消息队列服务接口"""

    @abstractmethod
    def send_message(self, body: Any, priority: int = 0,
                     topic: Optional[str] = None,
                     max_retries: int = 3) -> str:
        """发送消息到队列。

        Args:
            body: 消息内容（任意可序列化对象）
            priority: 优先级（数值越大优先级越高）
            topic: 消息主题标签，用于路由过滤
            max_retries: 最大重试次数

        Returns:
    def is_running(self) -> bool:
        """消费者是否正在运行。"""
        ...


class QueueMonitorInterface(ABC):
    """队列监控接口

    提供队列运行状态、统计信息、健康检查等监控能力。
    """

    @abstractmethod
    def get_stats(self) -> QueueStats:
        """获取队列统计信息。

        Returns:
            QueueStats: 包含待处理、处理中、已完成、失败消息数量等信息
        """
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """健康检查。

        Returns:
            dict: 包含健康状态、运行时长、告警信息等
        """
        ...


class QueueMonitorInterface(ABC):
    """队列监控接口

    提供队列运行状态、统计信息、健康检查等监控能力。
    """

    @abstractmethod
    def get_stats(self) -> QueueStats:
        """获取队列统计信息。

        Returns:
            QueueStats: 包含待处理、处理中、已完成、失败消息数量等信息
        """
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """健康检查。

        Returns:
            dict: 包含健康状态、运行时长、告警信息等
        """
        ...


class QueueMonitorInterface(ABC):
    """队列监控接口

    提供队列运行状态、统计信息、健康检查等监控能力。
    """

    @abstractmethod
    def get_stats(self) -> QueueStats:
        """获取队列统计信息。

        Returns:
            QueueStats: 包含待处理、处理中、已完成、失败消息数量等信息
        """
        ...

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """健康检查。

        Returns:
            dict: 包含健康状态、运行时长、告警信息等
        """
        ...
            QueueFullError: 队列已满时抛出
        """
        ...

    @abstractmethod
    def receive_message(self, timeout: float = 0,
                        topic: Optional[str] = None) -> Optional[QueueMessageDTO]:
        """从队列接收一条消息。

        Args:
            timeout: 等待超时秒数（0表示立即返回）
            topic: 按主题过滤

        Returns:
            消息对象，队列为空时返回 None
        """
        ...

    @abstractmethod
    def acknowledge_message(self, msg_id: str) -> bool:
        """确认消息处理完成。

        Args:
            msg_id: 消息ID

        Returns:
            确认成功返回 True
        """
        ...

    @abstractmethod
    def reject_message(self, msg_id: str, requeue: bool = False,
                       error: Optional[str] = None) -> bool:
        """拒绝消息。

        Args:
            msg_id: 消息ID
            requeue: 是否重新入队（用于重试）
            error: 错误信息

        Returns:
            拒绝成功返回 True
        """
        ...

    @abstractmethod
    def queue_size(self) -> int:
        """返回队列中待处理消息数量。"""
        ...

    @abstractmethod
    def clear_queue(self) -> int:
        """清空队列，返回清空的消息数。"""
        ...

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        """获取队列统计信息。

        Returns:
            包含 pending, processing, completed, failed 计数的字典
        """
        ...


class QueueConsumerInterface(ABC):
    """队列消费者接口"""

    @abstractmethod
    def start_consuming(self, handler: Callable[[QueueMessageDTO], bool],
                        interval: float = 0.1):
        """启动消费循环。

        Args:
            handler: 消息处理回调函数，接收消息返回是否成功
            interval: 轮询间隔（秒）
        """
        ...

    @abstractmethod
    def stop_consuming(self, wait: bool = True):
        """停止消费循环。

        Args:
            wait: 是否等待当前处理完成
        """
        ...

    @abstractmethod
    def is_running(self) -> bool:
        """消费者是否正在运行。"""
        ...
