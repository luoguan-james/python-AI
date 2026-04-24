# -*- coding: utf-8 -*-

"""
消息队列模块

提供通用的消息队列抽象，支持多种后端实现（内存、Redis、文件），
用于解耦爬虫数据生产与消费，支持异步处理、批量消费、重试机制。

使用示例:
    # 内存队列（单进程）
    from message_queue import InMemoryQueue, Producer, Consumer

    queue = InMemoryQueue()
    producer = Producer(queue)
    consumer = Consumer(queue, handler=lambda msg: print(msg.body))

    producer.send({'name': '张三', 'department': '计算机学院'})
    msg = consumer.receive()
    consumer.ack(msg)

    # 文件队列（进程间/持久化）
    from message_queue import FileQueue
    queue = FileQueue('/tmp/mq_data')
"""

import json
import os
import time
import uuid
import threading
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# 消息状态枚举
# =============================================================================

class MessageStatus(str, Enum):
    """消息状态"""
    PENDING = 'pending'       # 待处理
    PROCESSING = 'processing' # 处理中
    COMPLETED = 'completed'   # 已完成
    FAILED = 'failed'         # 失败
    RETRY = 'retry'           # 待重试


# =============================================================================
# 消息数据类
# =============================================================================

@dataclass
class Message:
    """
    消息体

    Attributes:
        msg_id: 消息唯一ID（自动生成）
        body: 消息内容（可以是任意可序列化对象）
        status: 消息状态
        created_at: 创建时间戳
        updated_at: 最后更新时间戳
        retry_count: 已重试次数
        max_retries: 最大重试次数
        error: 错误信息
        priority: 优先级（数值越大优先级越高）
    """
    body: Any
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: MessageStatus = MessageStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    priority: int = 0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'msg_id': self.msg_id,
            'body': self.body,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error': self.error,
            'priority': self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """从字典恢复消息"""
        return cls(
            msg_id=data.get('msg_id', str(uuid.uuid4())),
            body=data.get('body'),
            status=MessageStatus(data.get('status', 'pending')),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat()),
            retry_count=data.get('retry_count', 0),
            max_retries=data.get('max_retries', 3),
            error=data.get('error'),
            priority=data.get('priority', 0),
        )

    def __repr__(self):
        return (f"<Message(id={self.msg_id[:8]}, status={self.status.value}, "
                f"retry={self.retry_count}/{self.max_retries})>")


# =============================================================================
# 队列抽象基类
# =============================================================================

class BaseQueue:
    """
    消息队列抽象基类

    所有队列后端实现必须继承此类并实现以下方法。
    """

    def send(self, message: Message) -> str:
        """发送消息到队列，返回消息ID"""
        raise NotImplementedError

    def receive(self, timeout: float = 0) -> Optional[Message]:
        """
        从队列接收一条消息（非阻塞）
        Args:
            timeout: 等待超时秒数（0表示立即返回）
        Returns:
            消息对象，队列为空时返回 None
        """
        raise NotImplementedError

    def ack(self, message: Message) -> bool:
        """确认消息处理完成"""
        raise NotImplementedError

    def nack(self, message: Message, requeue: bool = False) -> bool:
        """
        拒绝消息
        Args:
            message: 消息对象
            requeue: 是否重新入队（用于重试）
        """
        raise NotImplementedError

    def size(self) -> int:
        """返回队列中待处理消息数量"""
        raise NotImplementedError

    def clear(self) -> int:
        """清空队列，返回清空的消息数"""
        raise NotImplementedError

    def close(self):
        """关闭队列，释放资源"""
        raise NotImplementedError


# =============================================================================
# 内存队列实现（线程安全）
# =============================================================================

class InMemoryQueue(BaseQueue):
    """
    基于内存的队列实现

    使用优先级队列 + 条件变量实现线程安全的生产者-消费者模式。
    适用于单进程内的异步任务分发。

    特点:
        - 支持优先级
        - 线程安全
        - 支持重试
        - 不支持进程间通信
    """

    def __init__(self, maxsize: int = 0):
        """
        Args:
            maxsize: 队列最大容量（0表示无限制）
        """
        self._maxsize = maxsize
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._not_full = threading.Condition(self._lock)
        # 使用列表模拟优先级队列（按 priority 降序排列）
        self._queue: List[Message] = []
        # 处理中的消息（msg_id -> Message）
        self._processing: dict = {}
        # 已完成/失败的消息（保留最近 N 条用于审计）
        self._history: List[Message] = []
        self._max_history = 1000

    def send(self, message: Message) -> str:
        """发送消息"""
        with self._not_full:
            if self._maxsize > 0 and len(self._queue) >= self._maxsize:
                raise QueueFullError(f"队列已满 (maxsize={self._maxsize})")
            self._queue.append(message)
            # 按优先级降序排序
            self._queue.sort(key=lambda m: m.priority, reverse=True)
            self._not_empty.notify()
        logger.debug(f"消息已入队: {message}")
        return message.msg_id

    def receive(self, timeout: float = 0) -> Optional[Message]:
        """接收消息"""
        with self._not_empty:
            if not self._queue:
                if timeout <= 0:
                    return None
                self._not_empty.wait(timeout=timeout)
            if not self._queue:
                return None
            message = self._queue.pop(0)
            message.status = MessageStatus.PROCESSING
            message.updated_at = datetime.now().isoformat()
            self._processing[message.msg_id] = message
        logger.debug(f"消息已出队: {message}")
        return message

    def ack(self, message: Message) -> bool:
        """确认消息"""
        with self._lock:
            if message.msg_id not in self._processing:
                logger.warning(f"消息不在处理中状态，无法确认: {message}")
                return False
            msg = self._processing.pop(message.msg_id)
            msg.status = MessageStatus.COMPLETED
            msg.updated_at = datetime.now().isoformat()
            self._add_history(msg)
        logger.debug(f"消息已确认: {message}")
        return True

    def nack(self, message: Message, requeue: bool = False) -> bool:
        """拒绝消息"""
        with self._lock:
            if message.msg_id not in self._processing:
                logger.warning(f"消息不在处理中状态，无法拒绝: {message}")
                return False
            msg = self._processing.pop(message.msg_id)
            msg.updated_at = datetime.now().isoformat()

            if requeue and msg.retry_count < msg.max_retries:
                # 重试：重新入队
                msg.retry_count += 1
                msg.status = MessageStatus.RETRY
                msg.error = message.error
                self._queue.append(msg)
                self._queue.sort(key=lambda m: m.priority, reverse=True)
                self._not_empty.notify()
                logger.info(f"消息将重试 ({msg.retry_count}/{msg.max_retries}): {msg}")
            else:
                # 标记为失败
                msg.status = MessageStatus.FAILED
                msg.error = message.error or '超过最大重试次数'
                self._add_history(msg)
                logger.warning(f"消息处理失败: {msg}")
        return True

    def size(self) -> int:
        """返回待处理消息数量"""
        with self._lock:
            return len(self._queue)

    def clear(self) -> int:
        """清空队列"""
        with self._lock:
            count = len(self._queue)
            self._queue.clear()
            self._processing.clear()
        logger.info(f"队列已清空，移除 {count} 条消息")
        return count

    def close(self):
        """关闭队列"""
        self.clear()

    def _add_history(self, message: Message):
        """添加到历史记录（自动裁剪）"""
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    @property
    def pending_count(self) -> int:
        """待处理消息数"""
        return self.size()

    @property
    def processing_count(self) -> int:
        """处理中消息数"""
        with self._lock:
            return len(self._processing)

    @property
    def history_count(self) -> int:
        """历史消息数"""
        return len(self._history)


# =============================================================================
# 文件队列实现（进程间通信 / 持久化）
# =============================================================================

class FileQueue(BaseQueue):
    """
    基于文件的队列实现

    使用文件系统存储消息，支持进程间通信和持久化。
    每个消息存储为一个独立的 JSON 文件。

    特点:
        - 进程安全（文件锁）
        - 崩溃恢复
        - 支持大消息（不占用内存）
        - 适合开发/测试环境
    """

    def __init__(self, data_dir: str = '/tmp/message_queue'):
        """
        Args:
            data_dir: 数据存储目录
        """
        self._data_dir = data_dir
        self._pending_dir = os.path.join(data_dir, 'pending')
        self._processing_dir = os.path.join(data_dir, 'processing')
        self._completed_dir = os.path.join(data_dir, 'completed')
        self._failed_dir = os.path.join(data_dir, 'failed')

        # 创建目录结构
        for d in [self._pending_dir, self._processing_dir,
                  self._completed_dir, self._failed_dir]:
            os.makedirs(d, exist_ok=True)

        # 恢复崩溃时遗留的处理中消息
        self._recover_processing()

        logger.info(f"文件队列初始化完成: {data_dir}")

    def send(self, message: Message) -> str:
        """发送消息"""
        filepath = self._message_path(self._pending_dir, message.msg_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
        logger.debug(f"消息已写入文件: {filepath}")
        return message.msg_id

    def receive(self, timeout: float = 0) -> Optional[Message]:
        """接收消息"""
        # 获取待处理文件列表
        files = self._list_files(self._pending_dir)
        if not files:
            if timeout > 0:
                time.sleep(min(timeout, 0.5))
                files = self._list_files(self._pending_dir)
            if not files:
                return None

        # 取最早的文件（FIFO）
        filepath = files[0]
        try:
            msg = self._read_message(filepath)
            if msg is None:
                return None

            # 移动到处理中目录
            dest = self._message_path(self._processing_dir, msg.msg_id)
            os.rename(filepath, dest)
            msg.status = MessageStatus.PROCESSING
            msg.updated_at = datetime.now().isoformat()
            # 更新文件内容
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(msg.to_dict(), f, ensure_ascii=False, indent=2)
            return msg
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            return None

    def ack(self, message: Message) -> bool:
        """确认消息"""
        src = self._message_path(self._processing_dir, message.msg_id)
        if not os.path.exists(src):
            logger.warning(f"消息文件不存在: {src}")
            return False
        try:
            message.status = MessageStatus.COMPLETED
            message.updated_at = datetime.now().isoformat()
            dest = self._message_path(self._completed_dir, message.msg_id)
            with open(src, 'w', encoding='utf-8') as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
            os.rename(src, dest)
            return True
        except Exception as e:
            logger.error(f"确认消息失败: {e}")
            return False

    def nack(self, message: Message, requeue: bool = False) -> bool:
        """拒绝消息"""
        src = self._message_path(self._processing_dir, message.msg_id)
        if not os.path.exists(src):
            logger.warning(f"消息文件不存在: {src}")
            return False
        try:
            message.updated_at = datetime.now().isoformat()
            if requeue and message.retry_count < message.max_retries:
                message.retry_count += 1
                message.status = MessageStatus.RETRY
                message.error = message.error
                dest = self._message_path(self._pending_dir, message.msg_id)
            else:
                message.status = MessageStatus.FAILED
                message.error = message.error or '超过最大重试次数'
                dest = self._message_path(self._failed_dir, message.msg_id)

            with open(src, 'w', encoding='utf-8') as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
            os.rename(src, dest)
            return True
        except Exception as e:
            logger.error(f"拒绝消息失败: {e}")
            return False

    def size(self) -> int:
        """返回待处理消息数量"""
        return len(self._list_files(self._pending_dir))

    def clear(self) -> int:
        """清空队列"""
        count = 0
        for dir_path in [self._pending_dir, self._processing_dir]:
            for fname in os.listdir(dir_path):
                fpath = os.path.join(dir_path, fname)
                if fname.endswith('.json'):
                    os.remove(fpath)
                    count += 1
        logger.info(f"文件队列已清空，移除 {count} 条消息")
        return count

    def close(self):
        """关闭队列"""
        pass

    def _recover_processing(self):
        """恢复崩溃时遗留的处理中消息"""
        files = self._list_files(self._processing_dir)
        for fpath in files:
            try:
                msg = self._read_message(fpath)
                if msg and msg.retry_count < msg.max_retries:
                    # 重新放回待处理队列
                    dest = self._message_path(self._pending_dir, msg.msg_id)
                    os.rename(fpath, dest)
                    logger.info(f"恢复消息到待处理队列: {msg}")
                else:
                    # 标记为失败
                    msg.status = MessageStatus.FAILED
                    msg.error = '进程崩溃导致消息未完成'
                    dest = self._message_path(self._failed_dir, msg.msg_id)
                    with open(fpath, 'w', encoding='utf-8') as f:
                        json.dump(msg.to_dict(), f, ensure_ascii=False, indent=2)
                    os.rename(fpath, dest)
                    logger.warning(f"消息已移至失败队列: {msg}")
            except Exception as e:
                logger.error(f"恢复消息失败: {e}")

    @staticmethod
    def _message_path(directory: str, msg_id: str) -> str:
        """获取消息文件路径"""
        return os.path.join(directory, f"{msg_id}.json")

    @staticmethod
    def _list_files(directory: str) -> List[str]:
        """列出目录中的 JSON 文件（按修改时间排序）"""
        try:
            files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if f.endswith('.json')
            ]
            files.sort(key=lambda p: os.path.getmtime(p))
            return files
        except OSError:
            return []

    @staticmethod
    def _read_message(filepath: str) -> Optional[Message]:
        """从文件读取消息"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Message.from_dict(data)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"读取消息文件失败 {filepath}: {e}")
            return None


# =============================================================================
# Redis 队列实现（分布式）
# =============================================================================

class RedisQueue(BaseQueue):
    """
    基于 Redis 的队列实现

    使用 Redis List 作为底层存储，支持分布式部署。
    需要安装 redis-py: pip install redis

    特点:
        - 支持分布式
        - 高性能
        - 支持阻塞读取
        - 支持消息持久化（Redis 配置）
    """

    def __init__(self, name: str = 'default_queue',
                 host: str = 'localhost', port: int = 6379,
                 db: int = 0, password: str = None,
                 max_retries: int = 3):
        """
        Args:
            name: 队列名称
            host: Redis 主机地址
            port: Redis 端口
            db: Redis 数据库编号
            password: Redis 密码
            max_retries: 消息最大重试次数
        """
        self._name = name
        self._max_retries = max_retries
        self._processing_key = f"{name}:processing"
        self._retry_key = f"{name}:retry"

        try:
            import redis
            self._client = redis.Redis(
                host=host, port=port, db=db,
                password=password, decode_responses=True
            )
            self._client.ping()
            logger.info(f"Redis 队列连接成功: {host}:{port}/{db}")
        except ImportError:
            raise ImportError(
                "使用 RedisQueue 需要安装 redis-py: pip install redis"
            )
        except Exception as e:
            raise ConnectionError(f"Redis 连接失败: {e}")

    def send(self, message: Message) -> str:
        """发送消息"""
        data = json.dumps(message.to_dict(), ensure_ascii=False)
        self._client.lpush(self._name, data)
        logger.debug(f"消息已发送到 Redis: {message}")
        return message.msg_id

    def receive(self, timeout: float = 0) -> Optional[Message]:
        """接收消息"""
        try:
            if timeout > 0:
                result = self._client.brpop(self._name, timeout=int(timeout))
                if result is None:
                    return None
                _, data = result
            else:
                data = self._client.rpop(self._name)
                if data is None:
                    return None

            msg_dict = json.loads(data)
            message = Message.from_dict(msg_dict)
            message.status = MessageStatus.PROCESSING
            message.updated_at = datetime.now().isoformat()

            # 存入处理中集合
            self._client.hset(
                self._processing_key, message.msg_id,
                json.dumps(message.to_dict(), ensure_ascii=False)
            )
            return message
        except Exception as e:
            logger.error(f"从 Redis 接收消息失败: {e}")
            return None

    def ack(self, message: Message) -> bool:
        """确认消息"""
        try:
            self._client.hdel(self._processing_key, message.msg_id)
            logger.debug(f"Redis 消息已确认: {message}")
            return True
        except Exception as e:
            logger.error(f"确认 Redis 消息失败: {e}")
            return False

    def nack(self, message: Message, requeue: bool = False) -> bool:
        """拒绝消息"""
        try:
            self._client.hdel(self._processing_key, message.msg_id)
            if requeue and message.retry_count < message.max_retries:
                message.retry_count += 1
                message.status = MessageStatus.RETRY
                message.updated_at = datetime.now().isoformat()
                self.send(message)
                logger.info(f"Redis 消息将重试 ({message.retry_count}/{message.max_retries})")
            else:
                message.status = MessageStatus.FAILED
                message.error = message.error or '超过最大重试次数'
                message.updated_at = datetime.now().isoformat()
                self._client.hset(
                    f"{self._name}:failed", message.msg_id,
                    json.dumps(message.to_dict(), ensure_ascii=False)
                )
                logger.warning(f"Redis 消息处理失败: {message}")
            return True
        except Exception as e:
            logger.error(f"拒绝 Redis 消息失败: {e}")
            return False

    def size(self) -> int:
        """返回待处理消息数量"""
        try:
            return self._client.llen(self._name)
        except Exception:
            return 0

    def clear(self) -> int:
        """清空队列"""
        try:
            count = self._client.llen(self._name)
            self._client.delete(self._name)
            self._client.delete(self._processing_key)
            self._client.delete(f"{self._name}:failed")
            return count
        except Exception as e:
            logger.error(f"清空 Redis 队列失败: {e}")
            return 0

    def close(self):
        """关闭连接"""
        try:
            self._client.close()
        except Exception:
            pass


# =============================================================================
# 生产者
# =============================================================================

class Producer:
    """
    消息生产者

    封装消息创建和发送逻辑，提供便捷的发送方法。
    """

    def __init__(self, queue: BaseQueue):
        """
        Args:
            queue: 消息队列实例
        """
        self._queue = queue

    def send(self, body: Any, priority: int = 0,
             max_retries: int = 3, **kwargs) -> str:
        """
        发送消息

        Args:
            body: 消息内容
            priority: 优先级（数值越大优先级越高）
            max_retries: 最大重试次数
            **kwargs: 其他 Message 字段

        Returns:
            消息 ID
        """
        message = Message(
            body=body,
            priority=priority,
            max_retries=max_retries,
            **kwargs
        )
        return self._queue.send(message)

    def send_batch(self, items: List[Any], priority: int = 0) -> List[str]:
        """
        批量发送消息

        Args:
            items: 消息内容列表
            priority: 优先级

        Returns:
            消息 ID 列表
        """
        msg_ids = []
        for item in items:
            msg_id = self.send(item, priority=priority)
            msg_ids.append(msg_id)
        return msg_ids

    @property
    def queue(self) -> BaseQueue:
        """获取底层队列"""
        return self._queue


# =============================================================================
# 消费者
# =============================================================================

class Consumer:
    """
    消息消费者

    提供消息接收、处理和确认的完整生命周期管理。
    支持自动确认、批量消费、错误重试。
    """

    def __init__(self, queue: BaseQueue,
                 handler: Optional[Callable[[Message], bool]] = None,
                 auto_ack: bool = True,
                 batch_size: int = 1):
        """
        Args:
            queue: 消息队列实例
            handler: 消息处理函数（接收 Message 参数，返回 bool 表示成功/失败）
            auto_ack: 是否自动确认（handler 返回 True 时自动 ack）
            batch_size: 批量消费数量
        """
        self._queue = queue
        self._handler = handler
        self._auto_ack = auto_ack
        self._batch_size = batch_size
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def receive(self, timeout: float = 0) -> Optional[Message]:
        """
        接收一条消息

        Args:
            timeout: 超时秒数

        Returns:
            消息对象，队列为空时返回 None
        """
        return self._queue.receive(timeout=timeout)

    def receive_batch(self, max_count: Optional[int] = None,
                      timeout: float = 0) -> List[Message]:
        """
        批量接收消息

        Args:
            max_count: 最大接收数量（默认使用 batch_size）
            timeout: 超时秒数

        Returns:
            消息列表
        """
        count = max_count or self._batch_size
        messages = []
        for _ in range(count):
            msg = self._queue.receive(timeout=timeout)
            if msg is None:
                break
            messages.append(msg)
        return messages

    def ack(self, message: Message) -> bool:
        """确认消息"""
        return self._queue.ack(message)

    def nack(self, message: Message, requeue: bool = False) -> bool:
        """拒绝消息"""
        return self._queue.nack(message, requeue=requeue)

    def process(self, message: Message) -> bool:
        """
        处理单条消息

        如果设置了 handler，调用 handler 处理。
        如果 auto_ack 为 True，处理成功后自动确认。

        Args:
            message: 消息对象

        Returns:
            处理是否成功
        """
        if self._handler is None:
            raise ValueError("未设置消息处理函数 (handler)")

        try:
            success = self._handler(message)
            if success and self._auto_ack:
                self.ack(message)
            elif not success:
                self.nack(message, requeue=True)
            return success
        except Exception as e:
            logger.exception(f"消息处理异常: {e}")
            message.error = str(e)
            self.nack(message, requeue=True)
            return False

    def start(self, interval: float = 0.1):
        """
        启动后台消费循环（在独立线程中运行）

        Args:
            interval: 轮询间隔（秒）
        """
        if self._running:
            logger.warning("消费者已在运行中")
            return

        if self._handler is None:
            raise ValueError("后台消费需要设置 handler")

        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(interval,),
            daemon=True,
            name='ConsumerThread'
        )
        self._thread.start()
        logger.info("消费者后台线程已启动")

    def stop(self, wait: bool = True):
        """
        停止后台消费循环

        Args:
            wait: 是否等待线程结束
        """
        self._running = False
        if self._thread and wait:
            self._thread.join(timeout=5)
        logger.info("消费者已停止")

    def _run_loop(self, interval: float):
        """后台消费循环"""
        while self._running:
            try:
                message = self._queue.receive(timeout=interval)
                if message is None:
                    continue
                self.process(message)
            except Exception as e:
                logger.error(f"消费循环异常: {e}")
                time.sleep(interval)

    @property
    def is_running(self) -> bool:
        """消费者是否在运行"""
        return self._running

    @property
    def queue(self) -> BaseQueue:
        """获取底层队列"""
        return self._queue


# =============================================================================
# 异常定义
# =============================================================================

class QueueFullError(Exception):
    """队列已满异常"""
    pass


class QueueEmptyError(Exception):
    """队列为空异常"""
    pass


class QueueConnectionError(Exception):
    """队列连接异常"""
    pass


# =============================================================================
# 便捷工厂函数
# =============================================================================

def create_queue(backend: str = 'memory', **kwargs) -> BaseQueue:
    """
    创建消息队列实例

    Args:
        backend: 队列后端类型 ('memory', 'file', 'redis')
        **kwargs: 传递给队列构造函数的参数

    Returns:
        队列实例

    Examples:
        >>> queue = create_queue('memory')
        >>> queue = create_queue('file', data_dir='/tmp/my_queue')
        >>> queue = create_queue('redis', name='my_queue', host='localhost')
    """
    backend = backend.lower()
    if backend == 'memory':
        return InMemoryQueue(**kwargs)
    elif backend == 'file':
        return FileQueue(**kwargs)
    elif backend == 'redis':
        return RedisQueue(**kwargs)
    else:
        raise ValueError(f"不支持的队列后端: {backend!r}，可选: memory, file, redis")


def create_producer_consumer(backend: str = 'memory',
                              handler: Optional[Callable] = None,
                              **kwargs) -> tuple:
    """
    便捷创建生产者和消费者对

    Args:
        backend: 队列后端类型
        handler: 消息处理函数
        **kwargs: 传递给队列和消费者的参数

    Returns:
        (producer, consumer) 元组
    """
    queue = create_queue(backend, **kwargs)
    producer = Producer(queue)
    consumer = Consumer(queue, handler=handler)
    return producer, consumer
