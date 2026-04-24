# -*- coding: utf-8 -*-
"""
Test for message_queue module - verify MessageQueue functionality.
"""

import pytest
import time
import json
import os
import tempfile
import threading
from datetime import datetime

from message_queue import (
    Message,
    MessageQueue,
    InMemoryQueue,
    FileQueue,
    Producer,
    Consumer,
    QueueError,
    QueueFullError,
    QueueEmptyError,
    QueueTimeoutError,
)


class TestMessage:
    """Message 单元测试"""

    def test_message_creation(self):
        """测试 Message 创建"""
        msg = Message(
            topic='test_topic',
            data={'key': 'value'},
            source='test_source'
        )
        assert msg.topic == 'test_topic'
        assert msg.data == {'key': 'value'}
        assert msg.source == 'test_source'
        assert msg.message_id is not None
        assert msg.timestamp is not None
        assert msg.status == 'pending'
        assert msg.retry_count == 0

    def test_message_defaults(self):
        """测试 Message 默认值"""
        msg = Message(topic='test', data='hello')
        assert msg.source == 'default'
        assert msg.priority == 0
        assert msg.ttl is None

    def test_message_to_dict(self):
        """测试 Message 转换为字典"""
        msg = Message(
            topic='test_topic',
            data={'key': 'value'},
            source='test_source',
            priority=5,
        )
        d = msg.to_dict()
        assert d['topic'] == 'test_topic'
        assert d['data'] == {'key': 'value'}
        assert d['source'] == 'test_source'
        assert d['priority'] == 5
        assert d['status'] == 'pending'
        assert 'message_id' in d
        assert 'timestamp' in d

    def test_message_from_dict(self):
        """测试从字典恢复 Message"""
        original = Message(
            topic='test_topic',
            data={'key': 'value'},
            source='test_source',
        )
        d = original.to_dict()
        restored = Message.from_dict(d)
        assert restored.topic == original.topic
        assert restored.data == original.data
        assert restored.source == original.source
        assert restored.message_id == original.message_id
        assert restored.timestamp == original.timestamp

    def test_message_is_expired(self):
        """测试消息过期判断"""
        # 无 TTL 永不过期
        msg = Message(topic='test', data='hello')
        assert msg.is_expired() is False

        # 有 TTL 但未过期
        msg = Message(topic='test', data='hello', ttl=60)
        assert msg.is_expired() is False

        # 已过期消息
        msg = Message(topic='test', data='hello', ttl=-1)
        # 手动设置一个过去的时间戳
        msg.timestamp = (datetime.now().timestamp() - 10)
        assert msg.is_expired() is True

    def test_message_mark_processing(self):
        """测试标记为处理中"""
        msg = Message(topic='test', data='hello')
        msg.mark_processing()
        assert msg.status == 'processing'

    def test_message_mark_done(self):
        """测试标记为已完成"""
        msg = Message(topic='test', data='hello')
        msg.mark_done()
        assert msg.status == 'done'

    def test_message_mark_failed(self):
        """测试标记为失败"""
        msg = Message(topic='test', data='hello')
        msg.mark_failed(error='test error')
        assert msg.status == 'failed'
        assert msg.error == 'test error'

    def test_message_increment_retry(self):
        """测试重试计数"""
        msg = Message(topic='test', data='hello')
        assert msg.retry_count == 0
        msg.increment_retry()
        assert msg.retry_count == 1
        msg.increment_retry()
        assert msg.retry_count == 2

    def test_message_repr(self):
        """测试字符串表示"""
        msg = Message(topic='test_topic', data={'key': 'value'})
        repr_str = repr(msg)
        assert 'test_topic' in repr_str
        assert msg.message_id[:8] in repr_str


class TestInMemoryQueue:
    """InMemoryQueue 单元测试"""

    def test_init_defaults(self):
        """测试默认初始化"""
        q = InMemoryQueue()
        assert q.maxsize == 0
        assert q.name == 'default'

    def test_init_with_params(self):
        """测试带参数初始化"""
        q = InMemoryQueue(maxsize=100, name='test_queue')
        assert q.maxsize == 100
        assert q.name == 'test_queue'

    def test_put_and_get(self):
        """测试放入和取出消息"""
        q = InMemoryQueue()
        msg = Message(topic='test', data='hello')
        q.put(msg)
        assert q.qsize() == 1

        retrieved = q.get()
        assert retrieved.topic == 'test'
        assert retrieved.data == 'hello'
        assert q.qsize() == 0

    def test_get_empty(self):
        """测试从空队列获取消息"""
        q = InMemoryQueue()
        with pytest.raises(QueueEmptyError):
            q.get(timeout=0.1)

    def test_put_full(self):
        """测试向满队列放入消息"""
        q = InMemoryQueue(maxsize=2)
        q.put(Message(topic='t1', data='d1'))
        q.put(Message(topic='t2', data='d2'))
        with pytest.raises(QueueFullError):
            q.put(Message(topic='t3', data='d3'), timeout=0.1)

    def test_priority_ordering(self):
        """测试优先级排序"""
        q = InMemoryQueue()
        q.put(Message(topic='low', data='low', priority=1))
        q.put(Message(topic='high', data='high', priority=10))
        q.put(Message(topic='mid', data='mid', priority=5))

        # 高优先级先出队
        assert q.get().topic == 'high'
        assert q.get().topic == 'mid'
        assert q.get().topic == 'low'

    def test_topic_filter(self):
        """测试按主题过滤"""
        q = InMemoryQueue()
        q.put(Message(topic='topic_a', data='a'))
        q.put(Message(topic='topic_b', data='b'))
        q.put(Message(topic='topic_a', data='a2'))

        # 只获取 topic_a 的消息
        msg = q.get(topic='topic_a')
        assert msg.topic == 'topic_a'
        assert msg.data == 'a'

        msg = q.get(topic='topic_a')
        assert msg.topic == 'topic_a'
        assert msg.data == 'a2'

    def test_put_batch(self):
        """测试批量放入"""
        q = InMemoryQueue()
        messages = [
            Message(topic='t1', data='d1'),
            Message(topic='t2', data='d2'),
            Message(topic='t3', data='d3'),
        ]
        count = q.put_batch(messages)
        assert count == 3
        assert q.qsize() == 3

    def test_get_batch(self):
        """测试批量取出"""
        q = InMemoryQueue()
        for i in range(5):
            q.put(Message(topic='test', data=f'data_{i}'))

        batch = q.get_batch(max_count=3)
        assert len(batch) == 3
        assert q.qsize() == 2

    def test_clear(self):
        """测试清空队列"""
        q = InMemoryQueue()
        q.put(Message(topic='t1', data='d1'))
        q.put(Message(topic='t2', data='d2'))
        assert q.qsize() == 2

        q.clear()
        assert q.qsize() == 0

    def test_is_empty(self):
        """测试判空"""
        q = InMemoryQueue()
        assert q.is_empty() is True
        q.put(Message(topic='test', data='hello'))
        assert q.is_empty() is False

    def test_is_full(self):
        """测试判满"""
        q = InMemoryQueue(maxsize=2)
        assert q.is_full() is False
        q.put(Message(topic='t1', data='d1'))
        assert q.is_full() is False
        q.put(Message(topic='t2', data='d2'))
        assert q.is_full() is True

    def test_get_all(self):
        """测试获取所有消息"""
        q = InMemoryQueue()
        q.put(Message(topic='t1', data='d1'))
        q.put(Message(topic='t2', data='d2'))
        all_msgs = q.get_all()
        assert len(all_msgs) == 2
        assert q.qsize() == 0

    def test_iteration(self):
        """测试迭代器"""
        q = InMemoryQueue()
        q.put(Message(topic='t1', data='d1'))
        q.put(Message(topic='t2', data='d2'))

        count = 0
        for msg in q:
            count += 1
            assert msg.topic in ('t1', 't2')
            if count >= 2:
                break

    def test_context_manager(self):
        """测试上下文管理器"""
        with InMemoryQueue() as q:
            q.put(Message(topic='test', data='hello'))
            assert q.qsize() == 1
        # 退出上下文后队列应清空
        assert q.qsize() == 0

    def test_thread_safety(self):
        """测试线程安全性"""
        q = InMemoryQueue()
        num_threads = 10
        msgs_per_thread = 100

        def producer():
            for i in range(msgs_per_thread):
                q.put(Message(topic='test', data=f'data_{i}'))

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=producer)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert q.qsize() == num_threads * msgs_per_thread

    def test_stats(self):
        """测试统计信息"""
        q = InMemoryQueue(name='stats_test')
        q.put(Message(topic='t1', data='d1'))
        q.put(Message(topic='t2', data='d2'))
        q.get()  # 取出一个

        stats = q.get_stats()
        assert stats['name'] == 'stats_test'
        assert stats['current_size'] == 1
        assert stats['total_put'] == 2
        assert stats['total_get'] == 1
        assert 'maxsize' in stats
        assert 'uptime' in stats


class TestFileQueue:
    """FileQueue 单元测试"""

    def test_init_and_persistence(self):
        """测试文件队列的持久化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test_queue.json')
            q = FileQueue(filepath=filepath, name='file_test')

            q.put(Message(topic='t1', data='d1'))
            q.put(Message(topic='t2', data='d2'))
            assert q.qsize() == 2

            # 重新加载，数据应持久化
            q2 = FileQueue(filepath=filepath, name='file_test')
            assert q2.qsize() == 2

            msg = q2.get()
            assert msg.topic == 't1'
            assert msg.data == 'd1'

    def test_file_queue_clear(self):
        """测试文件队列清空"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test_queue.json')
            q = FileQueue(filepath=filepath)
            q.put(Message(topic='t1', data='d1'))
            q.clear()
            assert q.qsize() == 0
            # 文件应被删除
            assert not os.path.exists(filepath)

    def test_file_queue_empty(self):
        """测试空文件队列"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'empty_queue.json')
            q = FileQueue(filepath=filepath)
            assert q.is_empty() is True
            with pytest.raises(QueueEmptyError):
                q.get(timeout=0.1)


class TestProducer:
    """Producer 单元测试"""

    def test_producer_send(self):
        """测试生产者发送消息"""
        q = InMemoryQueue()
        producer = Producer(q, name='test_producer')
        producer.send(topic='test_topic', data={'key': 'value'})
        assert q.qsize() == 1

        msg = q.get()
        assert msg.topic == 'test_topic'
        assert msg.data == {'key': 'value'}

    def test_producer_send_batch(self):
        """测试生产者批量发送"""
        q = InMemoryQueue()
        producer = Producer(q)
        messages = [
            {'topic': 't1', 'data': 'd1'},
            {'topic': 't2', 'data': 'd2'},
        ]
        count = producer.send_batch(messages)
        assert count == 2
        assert q.qsize() == 2

    def test_producer_with_source(self):
        """测试生产者带来源标识"""
        q = InMemoryQueue()
        producer = Producer(q, name='spider_1')
        producer.send(topic='data', data='hello')
        msg = q.get()
        assert msg.source == 'spider_1'

    def test_producer_stats(self):
        """测试生产者统计"""
        q = InMemoryQueue()
        producer = Producer(q, name='stats_producer')
        producer.send(topic='t1', data='d1')
        producer.send(topic='t2', data='d2')

        stats = producer.get_stats()
        assert stats['name'] == 'stats_producer'
        assert stats['total_sent'] == 2


class TestConsumer:
    """Consumer 单元测试"""

    def test_consumer_consume(self):
        """测试消费者消费消息"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))
        q.put(Message(topic='test', data='world'))

        consumer = Consumer(q, name='test_consumer')

        msg1 = consumer.consume()
        assert msg1.data == 'hello'
        assert msg1.status == 'processing'

        msg2 = consumer.consume()
        assert msg2.data == 'world'

    def test_consumer_consume_with_topic(self):
        """测试消费者按主题消费"""
        q = InMemoryQueue()
        q.put(Message(topic='a', data='1'))
        q.put(Message(topic='b', data='2'))
        q.put(Message(topic='a', data='3'))

        consumer = Consumer(q)

        msg = consumer.consume(topic='a')
        assert msg.data == '1'

        msg = consumer.consume(topic='a')
        assert msg.data == '3'

    def test_consumer_ack(self):
        """测试消费者确认消息"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))

        consumer = Consumer(q)
        msg = consumer.consume()
        assert msg.status == 'processing'

        consumer.ack(msg)
        assert msg.status == 'done'

    def test_consumer_nack(self):
        """测试消费者拒绝消息"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))

        consumer = Consumer(q)
        msg = consumer.consume()

        consumer.nack(msg, error='processing failed')
        assert msg.status == 'failed'
        assert msg.error == 'processing failed'

    def test_consumer_process(self):
        """测试消费者处理函数"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))

        results = []

        def handler(msg):
            results.append(msg.data)
            return True

        consumer = Consumer(q, handler=handler)
        result = consumer.process()
        assert result is True
        assert len(results) == 1
        assert results[0] == 'hello'

    def test_consumer_process_handler_failure(self):
        """测试消费者处理函数失败"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))

        def failing_handler(msg):
            raise ValueError('handler error')

        consumer = Consumer(q, handler=failing_handler)
        result = consumer.process()
        assert result is False

        # 消息应被标记为失败
        msg = q.get()
        assert msg.status == 'failed'
        assert 'handler error' in msg.error

    def test_consumer_process_all(self):
        """测试消费者处理所有消息"""
        q = InMemoryQueue()
        for i in range(3):
            q.put(Message(topic='test', data=f'data_{i}'))

        results = []

        def handler(msg):
            results.append(msg.data)
            return True

        consumer = Consumer(q, handler=handler)
        count = consumer.process_all()
        assert count == 3
        assert len(results) == 3
        assert q.is_empty()

    def test_consumer_stats(self):
        """测试消费者统计"""
        q = InMemoryQueue()
        q.put(Message(topic='test', data='hello'))

        consumer = Consumer(q, name='stats_consumer')
        msg = consumer.consume()
        consumer.ack(msg)

        stats = consumer.get_stats()
        assert stats['name'] == 'stats_consumer'
        assert stats['total_consumed'] == 1
        assert stats['total_acked'] == 1
        assert stats['total_nacked'] == 0


class TestIntegration:
    """集成测试"""

    def test_producer_consumer_workflow(self):
        """测试生产者-消费者完整工作流"""
        q = InMemoryQueue()
        producer = Producer(q, name='spider')
        consumer = Consumer(q, name='pipeline')

        # 生产者发送消息
        producer.send(topic='ts_item', data={'name': '张三', 'age': 25})
        producer.send(topic='ts_item', data={'name': '李四', 'age': 30})
        producer.send(topic='course_item', data={'course_name': '数学'})

        assert q.qsize() == 3

        # 消费者处理
        results = []

        def handler(msg):
            results.append(msg.data.get('name', msg.data.get('course_name')))
            return True

        consumer_with_handler = Consumer(q, handler=handler)
        count = consumer_with_handler.process_all()
        assert count == 3
        assert len(results) == 3
        assert '张三' in results
        assert '李四' in results
        assert '数学' in results

    def test_multi_producer_multi_consumer(self):
        """测试多生产者多消费者"""
        q = InMemoryQueue()

        # 多个生产者
        producers = [Producer(q, name=f'producer_{i}') for i in range(3)]
        for p in producers:
            p.send(topic='data', data=f'from_{p.name}')

        assert q.qsize() == 3

        # 多个消费者
        consumed = []

        def handler(msg):
            consumed.append(msg.data)
            return True

        consumers = [Consumer(q, handler=handler) for _ in range(3)]
        for c in consumers:
            c.process()

        assert len(consumed) == 3

    def test_queue_stats_accuracy(self):
        """测试队列统计准确性"""
        q = InMemoryQueue(name='stats_test')
        producer = Producer(q, name='producer')
        consumer = Consumer(q, name='consumer')

        # 发送 5 条，消费 3 条
        for i in range(5):
            producer.send(topic='test', data=f'data_{i}')

        for _ in range(3):
            msg = consumer.consume()
            consumer.ack(msg)

        stats = q.get_stats()
        assert stats['total_put'] == 5
        assert stats['total_get'] == 3
        assert stats['current_size'] == 2

    def test_file_queue_persistence_integration(self):
        """测试文件队列持久化集成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'integrate_queue.json')

            # 第一阶段：生产消息
            q1 = FileQueue(filepath=filepath)
            producer = Producer(q1, name='stage1')
            producer.send(topic='item', data={'id': 1})
            producer.send(topic='item', data={'id': 2})
            producer.send(topic='item', data={'id': 3})
            assert q1.qsize() == 3

            # 第二阶段：重新加载并消费
            q2 = FileQueue(filepath=filepath)
            assert q2.qsize() == 3

            results = []

            def handler(msg):
                results.append(msg.data['id'])
                return True

            consumer = Consumer(q2, handler=handler)
            consumer.process_all()
            assert len(results) == 3
            assert sorted(results) == [1, 2, 3]

    def test_priority_integration(self):
        """测试优先级集成"""
        q = InMemoryQueue()
        producer = Producer(q)

        # 发送不同优先级的消息
        producer.send(topic='test', data='low', priority=1)
        producer.send(topic='test', data='medium', priority=5)
        producer.send(topic='test', data='high', priority=10)

        # 按优先级消费
        consumer = Consumer(q)
        assert consumer.consume().data == 'high'
        assert consumer.consume().data == 'medium'
        assert consumer.consume().data == 'low'

    def test_topic_routing(self):
        """测试主题路由"""
        q = InMemoryQueue()
        producer = Producer(q)

        producer.send(topic='ts_item', data='teacher_data')
        producer.send(topic='course_item', data='course_data')
        producer.send(topic='article_item', data='article_data')

        # 按主题消费
        consumer = Consumer(q)

        msg = consumer.consume(topic=
