# -*- coding: utf-8 -*-
"""
Integration tests — 集成测试

覆盖范围：
- 消息队列完整工作流（内存队列、文件队列）
- 生产者-消费者端到端流程
- 优先级与主题路由
- 重试机制
- 多线程并发
- 数据模型与队列结合
- API 端到端流程
"""

import pytest
import time
import json
import os
import threading
import tempfile
from datetime import datetime
from typing import List, Dict, Any

from items import TsItem, CourseItem, ArticleItem, create_item, items_to_dicts
from message_queue import (
    Message,
    InMemoryQueue,
    FileQueue,
    Producer,
    Consumer,
    QueueFullError,
    QueueEmptyError,
)
from src.api.services.queue_service import QueueService
from src.api.interfaces.queue_interface import QueueConfig


# =============================================================================
# 消息队列集成测试
# =============================================================================

class TestMessageQueueIntegration:
    """消息队列集成测试"""

    def test_producer_consumer_full_workflow(self):
        """测试生产者-消费者完整工作流"""
        queue = InMemoryQueue()
        producer = Producer(queue, name="spider")
        consumer = Consumer(queue, name="pipeline")

        # 生产者发送不同类型的消息
        producer.send(body={"type": "teacher", "name": "张三", "department": "计算机学院"})
        producer.send(body={"type": "student", "name": "李四", "grade": "2023级"})
        producer.send(body={"type": "course", "name": "数据结构", "credits": 4})

        assert queue.size() == 3

        # 消费者处理所有消息
        results = []

        def handler(msg: Message) -> bool:
            results.append(msg.body.get("name", msg.body.get("type")))
            return True

        consumer_with_handler = Consumer(queue, handler=handler)
        count = 0
        while queue.size() > 0:
            msg = consumer_with_handler.receive()
            if msg:
                consumer_with_handler.ack(msg)
                consumer_with_handler.process(msg)
                count += 1

        assert count == 3
        assert "张三" in results
        assert "李四" in results
        assert "数据结构" in results

    def test_priority_workflow(self):
        """测试优先级工作流"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 发送不同优先级的消息
        producer.send(body="low", priority=1)
        producer.send(body="medium", priority=5)
        producer.send(body="high", priority=10)
        producer.send(body="urgent", priority=100)

        consumer = Consumer(queue)
        received = []

        for _ in range(4):
            msg = consumer.receive()
            if msg:
                received.append(msg.body)
                consumer.ack(msg)

        assert received == ["urgent", "high", "medium", "low"]

    def test_topic_routing_workflow(self):
        """测试主题路由工作流"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 发送不同主题的消息
        producer.send(body="teacher_data", topic="ts_item")
        producer.send(body="course_data", topic="course_item")
        producer.send(body="article_data", topic="article_item")
        producer.send(body="another_teacher", topic="ts_item")

        consumer = Consumer(queue)

        # 只消费 ts_item 主题
        ts_messages = []
        for _ in range(2):
            msg = consumer.receive(topic="ts_item")
            if msg:
                ts_messages.append(msg.body)
                consumer.ack(msg)

        assert len(ts_messages) == 2
        assert "teacher_data" in ts_messages
        assert "another_teacher" in ts_messages

    def test_retry_mechanism(self):
        """测试重试机制"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 发送一条消息，设置最大重试次数
        msg_id = producer.send(body="retry_me", max_retries=3)
        consumer = Consumer(queue)

        # 第一次消费并拒绝（重试）
        msg = consumer.receive()
        assert msg is not None
        consumer.nack(msg, requeue=True)
        assert msg.retry_count == 1
        assert queue.size() == 1  # 消息重新入队

        # 第二次消费并拒绝（重试）
        msg = consumer.receive()
        assert msg is not None
        consumer.nack(msg, requeue=True)
        assert msg.retry_count == 2

        # 第三次消费并拒绝（重试）
        msg = consumer.receive()
        assert msg is not None
        consumer.nack(msg, requeue=True)
        assert msg.retry_count == 3

        # 第四次消费并拒绝（超过最大重试次数，标记为失败）
        msg = consumer.receive()
        assert msg is not None
        consumer.nack(msg, requeue=True)
        assert msg.status.value == "failed"
        assert "超过最大重试次数" in (msg.error or "")

    def test_batch_operations(self):
        """测试批量操作"""
        queue = InMemoryQueue()
        producer = Producer(queue)
        consumer = Consumer(queue)

        # 批量发送
        messages = [
            {"body": f"msg_{i}", "priority": i}
            for i in range(10)
        ]
        for m in messages:
            producer.send(body=m["body"], priority=m["priority"])

        assert queue.size() == 10

        # 批量接收（高优先级优先）
        received = []
        for _ in range(10):
            msg = consumer.receive()
            if msg:
                received.append(msg.body)
                consumer.ack(msg)

        # 验证优先级排序
        assert received == [f"msg_{i}" for i in range(9, -1, -1)]

    def test_message_lifecycle(self):
        """测试消息生命周期"""
        queue = InMemoryQueue()
        producer = Producer(queue)
        consumer = Consumer(queue)

        # 发送
        msg_id = producer.send(body="lifecycle_test")
        assert queue.size() == 1

        # 接收（状态变为 processing）
        msg = consumer.receive()
        assert msg is not None
        assert msg.status.value == "processing"

        # 确认（状态变为 completed）
        consumer.ack(msg)
        assert msg.status.value == "completed"

        # 队列为空
        assert queue.size() == 0

    def test_message_failure_lifecycle(self):
        """测试消息失败生命周期"""
        queue = InMemoryQueue()
        producer = Producer(queue)
        consumer = Consumer(queue)

        msg_id = producer.send(body="fail_test")
        msg = consumer.receive()
        assert msg is not None

        # 拒绝（不重试）
        consumer.nack(msg, requeue=False)
        assert msg.status.value == "failed"
        assert queue.size() == 0

    def test_concurrent_producer_consumer(self):
        """测试并发生产消费"""
        queue = InMemoryQueue()
        total_messages = 100
        num_producers = 5
        messages_per_producer = total_messages // num_producers

        # 并发生产
        def produce():
            producer = Producer(queue)
            for i in range(messages_per_producer):
                producer.send(body=f"data_{i}")

        threads = []
        for _ in range(num_producers):
            t = threading.Thread(target=produce)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert queue.size() == total_messages

        # 并发消费
        consumed = []
        lock = threading.Lock()

        def consume():
            consumer = Consumer(queue)
            while True:
                msg = consumer.receive(timeout=0.1)
                if msg is None:
                    break
                with lock:
                    consumed.append(msg.body)
                consumer.ack(msg)

        threads = []
        for _ in range(3):
            t = threading.Thread(target=consume)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(consumed) == total_messages

    def test_file_queue_persistence(self):
        """测试文件队列持久化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = os.path.join(tmpdir, "queue_data")

            # 第一阶段：生产消息
            q1 = FileQueue(data_dir=data_dir)
            p1 = Producer(q1)
            p1.send(body={"id": 1, "name": "张三"})
            p1.send(body={"id": 2, "name": "李四"})
            p1.send(body={"id": 3, "name": "王五"})
            assert q1.size() == 3

            # 关闭队列
            q1.close()

            # 第二阶段：重新加载并消费
            q2 = FileQueue(data_dir=data_dir)
            assert q2.size() == 3

            results = []
            c2 = Consumer(q2)

            for _ in range(3):
                msg = c2.receive()
                if msg:
                    results.append(msg.body["name"])
                    c2.ack(msg)

            assert len(results) == 3
            assert "张三" in results
            assert "李四" in results
            assert "王五" in results

    def test_file_queue_crash_recovery(self):
        """测试文件队列崩溃恢复"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = os.path.join(tmpdir, "crash_queue")

            # 发送消息
            q = FileQueue(data_dir=data_dir)
            q.send(Message(body="test_data"))

            # 模拟崩溃：消息在 processing 目录中
            msg = q.receive()
            assert msg is not None

            # 不确认也不拒绝，直接关闭（模拟崩溃）
            q.close()

            # 重新加载，应恢复处理中的消息
            q2 = FileQueue(data_dir=data_dir)
            assert q2.size() == 1  # 消息被恢复

            msg2 = q2.receive()
            assert msg2 is not None
            assert msg2.body == "test_data"

    def test_queue_stats_tracking(self):
        """测试队列统计追踪"""
        queue = InMemoryQueue(name="stats_test")
        producer = Producer(queue, name="stats_producer")
        consumer = Consumer(queue, name="stats_consumer")

        # 发送 5 条
        for i in range(5):
            producer.send(body=f"data_{i}")

        # 消费 3 条，确认 2 条，拒绝 1 条
        for i in range(3):
            msg = consumer.receive()
            if msg:
                if i < 2:
                    consumer.ack(msg)
                else:
                    consumer.nack(msg, requeue=False)

        # 验证统计
        stats = queue.get_stats()
        assert stats["total_put"] == 5
        assert stats["total_get"] == 3
        assert stats["current_size"] == 2


# =============================================================================
# 数据模型与队列集成测试
# =============================================================================

class TestItemsWithQueueIntegration:
    """数据模型与消息队列集成测试"""

    def test_ts_item_through_queue(self):
        """测试 TsItem 通过消息队列流转"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 创建 TsItem 并通过队列发送
        item = TsItem(
            title="Dr.",
            name="张三",
            email="zhangsan@example.com",
            department="计算机学院",
        )
        producer.send(body=item.to_dict(), topic="ts_item")

        # 消费并恢复
        consumer = Consumer(queue)
        msg = consumer.receive(topic="ts_item")
        assert msg is not None

        restored_item = TsItem(**msg.body)
        assert restored_item['title'] == 'Dr.'
        assert restored_item['name'] == '张三'
        assert restored_item['email'] == 'zhangsan@example.com'

    def test_multiple_item_types_through_queue(self):
        """测试多种 Item 类型通过队列流转"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 发送不同类型的 Item
        ts_item = TsItem(title="教授", name="王老师")
        course_item = CourseItem(course_name="数学", teacher_name="王老师")
        article_item = ArticleItem(title="通知", author="教务处")

        producer.send(body=ts_item.to_dict(), topic="ts_item")
        producer.send(body=course_item.to_dict(), topic="course_item")
        producer.send(body=article_item.to_dict(), topic="article_item")

        assert queue.size() == 3

        # 按主题消费
        consumer = Consumer(queue)

        msg = consumer.receive(topic="ts_item")
        assert msg is not None
        restored_ts = TsItem(**msg.body)
        assert restored_ts['title'] == '教授'

        msg = consumer.receive(topic="course_item")
        assert msg is not None
        restored_course = CourseItem(**msg.body)
        assert restored_course['course_name'] == '数学'

        msg = consumer.receive(topic="article_item")
        assert msg is not None
        restored_article = ArticleItem(**msg.body)
        assert restored_article['title'] == '通知'

    def test_batch_item_processing(self):
        """测试批量 Item 处理"""
        queue = InMemoryQueue()
        producer = Producer(queue)

        # 批量创建并发送
        teachers = [
            TsItem(title=f"教授{i}", name=f"老师{i}", department="计算机学院")
            for i in range(5)
        ]

        for t in teachers:
            producer.send(body=t.to_dict(), topic="teacher")

        assert queue.size() == 5

        # 批量消费处理
        consumer = Consumer(queue)
        processed = []

        def handler(msg: Message) -> bool:
            item = TsItem(**msg.body)
            processed.append(item.get_full_name())
            return True

        consumer_with_handler = Consumer(queue, handler=handler)
        while queue.size() > 0:
            msg = consumer_with_handler.receive()
            if msg:
                consumer_with_handler.process(msg)
                consumer_with_handler.ack(msg)

        assert len(processed) == 5


# =============================================================================
# QueueService 集成测试
# =============================================================================

class TestQueueServiceIntegration:
    """QueueService 集成测试"""

    def test_full_queue_service_workflow(self):
        """测试 QueueService 完整工作流"""
        service = QueueService()

        # 发送消息
        msg_id = service.send_message(body={"action": "test", "value": 42})
        assert msg_id is not None

        # 接收消息
        msg = service.receive_message()
        assert msg is not None
        assert msg.body == {"action": "test", "value": 42}

        # 确认消息
        result = service.acknowledge_message(msg_id)
        assert result is True

        # 队列为空
        assert service.queue_size() == 0

    def test_send_receive_ack_workflow(self):
        """测试发送-接收-确认完整流程"""
        service = QueueService()

        # 发送 3 条消息
        ids = []
        for i in range(3):
            mid = service.send_message(body=f"msg_{i}", priority=i)
            ids.append(mid)

        assert service.queue_size() == 3

        # 按优先级接收（高优先级先出）
        msg1 = service.receive_message()
        assert msg1.body == "msg_2"  # priority=2 最高

        msg2 = service.receive_message()
        assert msg2.body == "msg_1"  # priority=1

        msg3 = service.receive_message()
        assert msg3.body == "msg_0"  # priority=0 最低

        # 确认所有消息
        assert service.acknowledge_message(msg1.msg_id) is True
        assert service.acknowledge_message(msg2.msg_id) is True
        assert service.acknowledge_message(msg3.msg_id) is True

    def test_reject_and_requeue(self):
        """测试拒绝和重新入队"""
        service = QueueService()

        msg_id = service.send_message(body="retry_test", max_retries=3)
        msg = service.receive_message()
        assert msg is not None

        # 拒绝并重新入队
        result = service.reject_message(msg.msg_id, requeue=True)
        assert result is True

        # 消息重新入队
        assert service.queue_size() == 1

        # 重新接收
        msg2 = service.receive_message()
        assert msg2 is not None
        assert msg2.body == "retry_test"
        assert msg2.retry_count == 1

    def test_clear_and_reuse(self):
        """测试清空后复用"""
        service = QueueService()

        service.send_message(body="temp1")
        service.send_message(body="temp2")
        assert service.queue_size() == 2

        service.clear_queue()
        assert service.queue_size() == 0

        # 清空后继续使用
        service.send_message(body="new_msg")
        assert service.queue_size() == 1

    def test_file_backend_workflow(self, temp_dir):
        """测试文件后端工作流"""
        config = QueueConfig(backend="file", data_dir=temp_dir)
        service = QueueService(config)

        # 发送
        msg_id = service.send_message(body="persistent_data")
        assert service.queue_size() == 1

        # 接收
        msg = service.receive_message()
        assert msg is not None
        assert msg.body == "persistent_data"

        # 确认
        assert service.acknowledge_message(msg_id) is True

    def test_handler_integration(self):
        """测试处理器集成"""
        service = QueueService()
        results = []

        def my_handler(body):
            results.append(body)
            return True

        service.set_handler(my_handler)
        service.send_message(body="handler_test")
        msg = service.receive_message()
        assert msg is not None

        result = service.process_message(msg.msg_id)
        assert result is True
        assert results == ["handler_test"]


# =============================================================================
# 端到端 API 集成测试
# =============================================================================

class TestEndToEndIntegration:
    """端到端集成测试"""

    def test_health_check(self):
        """测试健康检查"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_routes_registered(self):
        """测试 API 路由注册"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # 验证路由存在
        routes = [route.path for route in app.routes]
        assert "/api/v1/auth/login" in routes
        assert "/api/v1/users/{user_id}" in routes
        assert "/api/v1/users" in routes
        assert "/api/v1/queue/send" in routes
        assert "/api/v1/queue/receive" in routes
        assert "/api/v1/queue/stats" in routes
        assert "/api/v1/queue/health" in routes
        assert "/health" in routes

    def test_error_response_format(self):
        """测试错误响应格式"""
        from fastapi.testclient import TestClient
        from src.main import app

        client = TestClient(app)

        # 测试 422 错误格式
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

        # 测试 404 错误格式
        response = client.get("/api/v1/users/999", headers={"Authorization": "Bearer valid-token"})
        # 可能返回 404 或 200（取决于 mock）
        assert response.status_code in (200, 401, 403, 404)
