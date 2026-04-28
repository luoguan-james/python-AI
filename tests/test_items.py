# -*- coding: utf-8 -*-
"""
Test for items module — 爬虫数据模型单元测试

覆盖范围：
- TsItem 数据模型（创建、序列化、验证、哈希、工具方法）
- CourseItem 数据模型（创建、序列化、验证、业务方法）
- ArticleItem 数据模型（创建、序列化、验证、标签/附件处理）
- 工具函数（工厂函数、合并、批量验证、去重、过滤、排序、导出）
"""

import pytest
import json
import os
import tempfile
from datetime import datetime

from items import (
    TsItem,
    CourseItem,
    ArticleItem,
    create_item,
    merge_items,
    batch_validate,
    items_to_dicts,
    deduplicate_items,
    filter_items,
    sort_items,
    export_items_json,
    export_items_csv,
)


# =============================================================================
# TsItem 测试
# =============================================================================

class TestTsItem:
    """TsItem 数据模型单元测试"""

    def test_creation_with_all_fields(self, sample_ts_item):
        """测试创建完整字段的 TsItem"""
        item = sample_ts_item
        assert item['title'] == 'Dr.'
        assert item['name'] == '张三'
        assert item['gender'] == '男'
        assert item['age'] == 35
        assert item['email'] == 'zhangsan@example.com'
        assert item['phone'] == '13800138000'
        assert item['department'] == '计算机学院'
        assert item['major'] == '计算机科学与技术'
        assert item['grade'] == '教授'
        assert item['source_site'] == 'example.edu'
        assert item['status'] == 'active'

    def test_default_values(self, minimal_ts_item):
        """测试默认值自动填充"""
        item = minimal_ts_item
        # crawl_time 应自动填充
        assert item['crawl_time'] is not None
        # status 默认 active
        assert item['status'] == 'active'
        # created_at 应自动填充
        assert item['created_at'] is not None
        # item_hash 应自动生成
        assert item['item_hash'] is not None
        assert len(item['item_hash']) == 32  # MD5 哈希长度

    def test_to_dict_filters_none(self, sample_ts_item):
        """测试 to_dict 过滤 None 值"""
        d = sample_ts_item.to_dict()
        # 所有值都不应为 None
        for key, value in d.items():
            assert value is not None, f"字段 {key} 不应为 None"

    def test_to_dict_all_keeps_none(self):
        """测试 to_dict_all 保留所有字段"""
        item = TsItem(title="测试")
        d = item.to_dict_all()
        # 未设置的字段应为 None
        assert d.get('name') is None
        assert d.get('email') is None
        # 已设置的字段保留
        assert d['title'] == '测试'

    def test_validate_valid(self, sample_ts_item):
        """测试有效数据验证通过"""
        assert sample_ts_item.validate() is True

    def test_validate_valid_with_title_only(self):
        """测试只有 title 时验证通过"""
        item = TsItem(title="Dr.")
        assert item.validate() is True

    def test_validate_valid_with_name_only(self):
        """测试只有 name 时验证通过"""
        item = TsItem(name="张三")
        assert item.validate() is True

    def test_validate_invalid_empty(self):
        """测试空数据验证失败"""
        item = TsItem()
        assert item.validate() is False

    def test_get_full_name_with_both(self, sample_ts_item):
        """测试 title 和 name 都存在时返回组合"""
        assert sample_ts_item.get_full_name() == "Dr. - 张三"

    def test_get_full_name_title_only(self):
        """测试只有 title 时返回 title"""
        item = TsItem(title="Dr.")
        assert item.get_full_name() == "Dr."

    def test_get_full_name_name_only(self):
        """测试只有 name 时返回 name"""
        item = TsItem(name="张三")
        assert item.get_full_name() == "张三"

    def test_get_full_name_empty(self):
        """测试 title 和 name 都为空时返回空字符串"""
        item = TsItem()
        assert item.get_full_name() == ""

    def test_get_summary(self, sample_ts_item):
        """测试获取摘要"""
        summary = sample_ts_item.get_summary()
        assert '张三' in summary
        assert '计算机学院' in summary
        assert 'zhangsan@example.com' in summary

    def test_get_summary_minimal(self, minimal_ts_item):
        """测试最小字段的摘要"""
        summary = minimal_ts_item.get_summary()
        assert summary == '李四'

    def test_get_summary_empty(self):
        """测试空 Item 的摘要"""
        item = TsItem()
        assert item.get_summary() == 'N/A'

    def test_hash_consistency(self):
        """测试相同内容生成相同哈希"""
        item1 = TsItem(title="Dr.", name="张三", email="z@e.com", source_url="https://example.com")
        item2 = TsItem(title="Dr.", name="张三", email="z@e.com", source_url="https://example.com")
        assert item1['item_hash'] == item2['item_hash']

    def test_hash_different_content(self):
        """测试不同内容生成不同哈希"""
        item1 = TsItem(title="Dr.", name="张三", email="z@e.com")
        item2 = TsItem(title="Prof.", name="李四", email="l@e.com")
        assert item1['item_hash'] != item2['item_hash']

    def test_repr(self, sample_ts_item):
        """测试字符串表示"""
        repr_str = repr(sample_ts_item)
        assert 'TsItem' in repr_str
        assert 'Dr.' in repr_str
        assert '张三' in repr_str

    def test_get_required_fields(self):
        """测试获取必填字段列表"""
        item = TsItem()
        fields = item.get_required_fields()
        assert 'title' in fields
        assert 'name' in fields

    def test_crawl_time_auto_fill(self):
        """测试爬取时间自动填充"""
        item = TsItem(title="测试")
        assert item['crawl_time'] is not None
        # 验证是 ISO 格式的时间字符串
        datetime.fromisoformat(item['crawl_time'])

    def test_crawl_time_custom(self):
        """测试自定义爬取时间"""
        custom_time = "2024-01-01T00:00:00"
        item = TsItem(title="测试", crawl_time=custom_time)
        assert item['crawl_time'] == custom_time

    def test_item_hash_custom(self):
        """测试自定义哈希值"""
        custom_hash = "custom_hash_value"
        item = TsItem(title="测试", item_hash=custom_hash)
        assert item['item_hash'] == custom_hash

    def test_to_dict_roundtrip(self, sample_ts_item):
        """测试 to_dict 和从 dict 重建的一致性"""
        d = sample_ts_item.to_dict()
        # 验证所有字段都可 JSON 序列化
        json_str = json.dumps(d, ensure_ascii=False)
        restored = json.loads(json_str)
        assert restored['title'] == 'Dr.'
        assert restored['name'] == '张三'
        assert restored['email'] == 'zhangsan@example.com'


# =============================================================================
# CourseItem 测试
# =============================================================================

class TestCourseItem:
    """CourseItem 数据模型单元测试"""

    def test_creation_with_all_fields(self, sample_course_item):
        """测试创建完整字段的 CourseItem"""
        item = sample_course_item
        assert item['course_id'] == 'CS101'
        assert item['course_name'] == '数据结构与算法'
        assert item['teacher_name'] == '张三'
        assert item['department'] == '计算机学院'
        assert item['semester'] == '2024-2025-1'
        assert item['credits'] == 4
        assert item['capacity'] == 120
        assert item['enrolled'] == 100

    def test_default_crawl_time(self):
        """测试爬取时间自动填充"""
        item = CourseItem(course_name="测试课程")
        assert item['crawl_time'] is not None
        datetime.fromisoformat(item['crawl_time'])

    def test_to_dict_filters_none(self, sample_course_item):
        """测试 to_dict 过滤 None 值"""
        d = sample_course_item.to_dict()
        for key, value in d.items():
            assert value is not None, f"字段 {key} 不应为 None"

    def test_to_dict_all_keeps_none(self):
        """测试 to_dict_all 保留 None 字段"""
        item = CourseItem(course_name="测试")
        d = item.to_dict_all()
        assert d.get('teacher_name') is None
        assert d['course_name'] == '测试'

    def test_validate_valid(self, sample_course_item):
        """测试有效数据验证通过"""
        assert sample_course_item.validate() is True

    def test_validate_invalid_empty(self):
        """测试空数据验证失败"""
        item = CourseItem()
        assert item.validate() is False

    def test_is_full_true(self):
        """测试课程已满"""
        item = CourseItem(course_name="满课", capacity=100, enrolled=100)
        assert item.is_full() is True

    def test_is_full_false(self):
        """测试课程未满"""
        item = CourseItem(course_name="有余位", capacity=100, enrolled=80)
        assert item.is_full() is False

    def test_is_full_over_enrolled(self):
        """测试超选情况"""
        item = CourseItem(course_name="超选", capacity=100, enrolled=120)
        assert item.is_full() is True

    def test_is_full_no_capacity(self):
        """测试未设置容量"""
        item = CourseItem(course_name="无容量")
        assert item.is_full() is False

    def test_get_occupancy_rate(self):
        """测试获取占用率"""
        item = CourseItem(course_name="测试", capacity=100, enrolled=75)
        rate = item.get_occupancy_rate()
        assert rate == 0.75

    def test_get_occupancy_rate_full(self):
        """测试满课占用率"""
        item = CourseItem(course_name="满课", capacity=100, enrolled=100)
        assert item.get_occupancy_rate() == 1.0

    def test_get_occupancy_rate_zero_capacity(self):
        """测试容量为 0 时占用率"""
        item = CourseItem(course_name="零容量", capacity=0, enrolled=0)
        assert item.get_occupancy_rate() == 0.0

    def test_get_occupancy_rate_no_data(self):
        """测试未设置容量和人数"""
        item = CourseItem(course_name="无数据")
        assert item.get_occupancy_rate() is None

    def test_get_summary(self, sample_course_item):
        """测试获取摘要"""
        summary = sample_course_item.get_summary()
        assert '数据结构与算法' in summary
        assert '张三' in summary
        assert '2024-2025-1' in summary

    def test_get_summary_minimal(self):
        """测试最小字段摘要"""
        item = CourseItem(course_name="测试课程")
        assert item.get_summary() == '测试课程'

    def test_get_summary_empty(self):
        """测试空 Item 摘要"""
        item = CourseItem()
        assert item.get_summary() == 'N/A'

    def test_get_required_fields(self):
        """测试必填字段"""
        item = CourseItem()
        fields = item.get_required_fields()
        assert 'course_name' in fields
        assert 'teacher_name' in fields

    def test_repr(self, sample_course_item):
        """测试字符串表示"""
        repr_str = repr(sample_course_item)
        assert 'CourseItem' in repr_str
        assert '数据结构与算法' in repr_str
        assert '张三' in repr_str


# =============================================================================
# ArticleItem 测试
# =============================================================================

class TestArticleItem:
    """ArticleItem 数据模型单元测试"""

    def test_creation_with_all_fields(self, sample_article_item):
        """测试创建完整字段的 ArticleItem"""
        item = sample_article_item
        assert item['article_id'] == 'ART001'
        assert item['title'] == '关于2024年秋季学期选课的通知'
        assert item['author'] == '教务处'
        assert item['publish_date'] == '2024-06-01'
        assert item['category'] == '教务公告'
        assert item['view_count'] == 1500

    def test_default_crawl_time(self):
        """测试爬取时间自动填充"""
        item = ArticleItem(title="测试文章")
        assert item['crawl_time'] is not None
        datetime.fromisoformat(item['crawl_time'])

    def test_to_dict_filters_none(self, sample_article_item):
        """测试 to_dict 过滤 None 值"""
        d = sample_article_item.to_dict()
        for key, value in d.items():
            assert value is not None, f"字段 {key} 不应为 None"

    def test_validate_valid(self, sample_article_item):
        """测试有效数据验证通过"""
        assert sample_article_item.validate() is True

    def test_validate_invalid_empty(self):
        """测试空数据验证失败"""
        item = ArticleItem()
        assert item.validate() is False

    def test_get_tags_list_from_string(self, sample_article_item):
        """测试从逗号分隔字符串获取标签列表"""
        tags = sample_article_item.get_tags_list()
        assert '选课' in tags
        assert '教务' in tags
        assert '通知' in tags
        assert len(tags) == 3

    def test_get_tags_list_from_list(self):
        """测试从列表获取标签"""
        item = ArticleItem(title="测试", tags=["标签1", "标签2"])
        tags = item.get_tags_list()
        assert tags == ["标签1", "标签2"]

    def test_get_tags_list_from_json(self):
        """测试从 JSON 字符串获取标签"""
        item = ArticleItem(title="测试", tags='["tag1", "tag2"]')
        tags = item.get_tags_list()
        assert tags == ["tag1", "tag2"]

    def test_get_tags_list_none(self):
        """测试无标签时返回空列表"""
        item = ArticleItem(title="测试")
        assert item.get_tags_list() == []

    def test_get_tags_list_empty_string(self):
        """测试空字符串标签"""
        item = ArticleItem(title="测试", tags="")
        assert item.get_tags_list() == []

    def test_get_attachment_list_from_json(self, sample_article_item):
        """测试从 JSON 字符串获取附件列表"""
        urls = sample_article_item.get_attachment_list()
        assert 'https://example.com/attach/schedule.pdf' in urls
        assert len(urls) == 1

    def test_get_attachment_list_from_list(self):
        """测试从列表获取附件"""
        item = ArticleItem(title="测试", attachment_urls=["url1", "url2"])
        urls = item.get_attachment_list()
        assert urls == ["url1", "url2"]

    def test_get_attachment_list_none(self):
        """测试无附件时返回空列表"""
        item = ArticleItem(title="测试")
        assert item.get_attachment_list() == []

    def test_has_attachments_true(self, sample_article_item):
        """测试有附件"""
        assert sample_article_item.has_attachments() is True

    def test_has_attachments_false(self):
        """测试无附件"""
        item = ArticleItem(title="测试")
        assert item.has_attachments() is False

    def test_get_summary(self, sample_article_item):
        """测试获取摘要"""
        summary = sample_article_item.get_summary()
        assert '关于2024年秋季学期选课的通知' in summary
        assert '教务处' in summary
        assert '2024-06-01' in summary

    def test_get_summary_minimal(self):
        """测试最小字段摘要"""
        item = ArticleItem(title="通知")
        assert item.get_summary() == '通知'

    def test_get_summary_empty(self):
        """测试空 Item 摘要"""
        item = ArticleItem()
        assert item.get_summary() == 'N/A'

    def test_get_required_fields(self):
        """测试必填字段"""
        item = ArticleItem()
        fields = item.get_required_fields()
        assert 'title' in fields
        assert 'author' in fields

    def test_repr(self, sample_article_item):
        """测试字符串表示"""
        repr_str = repr(sample_article_item)
        assert 'ArticleItem' in repr_str
        assert '关于2024年秋季学期选课的通知' in repr_str
        assert '教务处' in repr_str


# =============================================================================
# 工具函数测试
# =============================================================================

class TestCreateItem:
    """工厂函数 create_item 测试"""

    def test_create_ts_item(self):
        """测试创建 TsItem"""
        item = create_item('ts', title="Dr.", name="张三")
        assert isinstance(item, TsItem)
        assert item['title'] == 'Dr.'
        assert item['name'] == '张三'

    def test_create_course_item(self):
        """测试创建 CourseItem"""
        item = create_item('course', course_name="数学", teacher_name="王老师")
        assert isinstance(item, CourseItem)
        assert item['course_name'] == '数学'

    def test_create_article_item(self):
        """测试创建 ArticleItem"""
        item = create_item('article', title="公告", author="admin")
        assert isinstance(item, ArticleItem)
        assert item['title'] == '公告'

    def test_create_invalid_type(self):
        """测试不支持的 Item 类型"""
        with pytest.raises(ValueError, match="Unsupported item type"):
            create_item('invalid_type')

    def test_create_case_insensitive(self):
        """测试类型名大小写不敏感"""
        item = create_item('TS', title="测试")
        assert isinstance(item, TsItem)


class TestMergeItems:
    """merge_items 函数测试"""

    def test_merge_ts_items(self):
        """测试合并两个 TsItem"""
        base = TsItem(title="Dr.", name="张三", email="old@e.com")
        override = TsItem(title="Prof.", email="new@e.com")
        merged = merge_items(base, override)
        assert merged['title'] == 'Prof.'  # 被覆盖
        assert merged['name'] == '张三'     # 保留
        assert merged['email'] == 'new@e.com'  # 被覆盖

    def test_merge_type_mismatch(self):
        """测试类型不匹配时抛出异常"""
        base = TsItem(title="测试")
        override = CourseItem(course_name="课程")
        with pytest.raises(TypeError, match="Cannot merge items of different types"):
            merge_items(base, override)

    def test_merge_preserves_type(self):
        """测试合并后类型与 base 一致"""
        base = TsItem(title="Dr.")
        override = TsItem(name="张三")
        merged = merge_items(base, override)
        assert type(merged) is TsItem

    def test_merge_override_none_does_not_clear(self):
        """测试 override 中的 None 不会覆盖 base 的值"""
        base = TsItem(title="Dr.", name="张三")
        override = TsItem(title=None, name=None)
        merged = merge_items(base, override)
        # None 值不应覆盖已有值
        assert merged['title'] == 'Dr.'
        assert merged['name'] == '张三'


class TestBatchValidate:
    """batch_validate 函数测试"""

    def test_all_valid(self, sample_ts_item):
        """测试全部有效"""
        items = [sample_ts_item, TsItem(title="测试")]
        result = batch_validate(items)
        assert len(result['valid']) == 2
        assert len(result['invalid']) == 0

    def test_some_invalid(self):
        """测试部分无效"""
        items = [TsItem(title="有效"), TsItem()]
        result = batch_validate(items)
        assert len(result['valid']) == 1
        assert len(result['invalid']) == 1

    def test_all_invalid(self):
        """测试全部无效"""
        items = [TsItem(), TsItem()]
        result = batch_validate(items)
        assert len(result['valid']) == 0
        assert len(result['invalid']) == 2

    def test_empty_list(self):
        """测试空列表"""
        result = batch_validate([])
        assert len(result['valid']) == 0
        assert len(result['invalid']) == 0

    def test_mixed_types(self):
        """测试混合类型"""
        items = [
            TsItem(title="教师"),
            CourseItem(course_name="课程"),
            ArticleItem(title="文章"),
        ]
        result = batch_validate(items)
        assert len(result['valid']) == 3


class TestItemsToDicts:
    """items_to_dicts 函数测试"""

    def test_exclude_none(self, sample_ts_item):
        """测试排除 None 值"""
        items = [sample_ts_item]
        dicts = items_to_dicts(items, exclude_none=True)
        assert len(dicts) == 1
        for d in dicts:
            for v in d.values():
                assert v is not None

    def test_keep_none(self):
        """测试保留 None 值"""
        item = TsItem(title="测试")
        dicts = items_to_dicts([item], exclude_none=False)
        assert len(dicts) == 1
        assert dicts[0].get('name') is None

    def test_empty_list(self):
        """测试空列表"""
        assert items_to_dicts([]) == []

    def test_multiple_items(self):
        """测试多个 Item"""
        items = [TsItem(title="A"), TsItem(title="B")]
        dicts = items_to_dicts(items)
        assert len(dicts) == 2


class TestDeduplicateItems:
    """deduplicate_items 函数测试"""

    def test_deduplicate_by_hash(self):
        """测试按 item_hash 去重"""
        items = [
            TsItem(title="A", name="张三", email="z@e.com"),
            TsItem(title="A", name="张三", email="z@e.com"),  # 重复
            TsItem(title="B", name="李四", email="l@e.com"),
        ]
        result = deduplicate_items(items)
        assert len(result) == 2

    def test_no_duplicates(self):
        """测试无重复"""
        items = [
            TsItem(title="A", name="张三"),
            TsItem(title="B", name="李四"),
        ]
        result = deduplicate_items(items)
        assert len(result) == 2

    def test_all_duplicates(self):
        """测试全部重复"""
        item = TsItem(title="A", name="张三")
        items = [item, TsItem(title="A", name="张三")]
        result = deduplicate_items(items)
        assert len(result) == 1

    def test_empty_list(self):
        """测试空列表"""
        assert deduplicate_items([]) == []


class TestFilterItems:
    """filter_items 函数测试"""

    def test_filter_by_status(self):
        """测试按状态过滤"""
        items = [
            TsItem(title="A", status="active"),
            TsItem(title="B", status="inactive"),
            TsItem(title="C", status="active"),
        ]
        result = filter_items(items, status="active")
        assert len(result) == 2
        assert all(item['status'] == 'active' for item in result)

    def test_filter_by_multiple_conditions(self):
        """测试多条件过滤"""
        items = [
            TsItem(title="A", status="active", department="CS"),
            TsItem(title="B", status="active", department="Math"),
            TsItem(title="C", status="inactive", department="CS"),
        ]
        result = filter_items(items, status="active", department="CS")
        assert len(result) == 1
        assert result[0]['title'] == 'A'

    def test_no_match(self):
        """测试无匹配"""
        items = [TsItem(title="A", status="active")]
        result = filter_items(items, status="inactive")
        assert len(result) == 0

    def test_empty_list(self):
        """测试空列表"""
        assert filter_items([]) == []


class TestSortItems:
    """sort_items 函数测试"""

    def test_sort_ascending(self):
        """测试升序排序"""
        items = [
            TsItem(title="B"),
            TsItem(title="A"),
            TsItem(title="C"),
        ]
        result = sort_items(items, key_field="title")
        assert [item['title'] for item in result] == ['A', 'B', 'C']

    def test_sort_descending(self):
        """测试降序排序"""
        items = [
            TsItem(title="A"),
            TsItem(title="C"),
            TsItem(title="B"),
        ]
        result = sort_items(items, key_field="title", reverse=True)
        assert [item['title'] for item in result] == ['C', 'B', 'A']

    def test_sort_with_none(self):
        """测试含 None 字段排序"""
        items = [
            TsItem(title="B"),
            TsItem(name="A"),  # title 为 None
            TsItem(title="C"),
        ]
        result = sort_items(items, key_field="title")
        # None 值排在最前
        assert result[0].get('title') is None or result[0].get('title') == ''

    def test_empty_list(self):
        """测试空列表"""
        assert sort_items([], key_field="title") == []


class TestExportItemsJson:
    """export_items_json 函数测试"""

    def test_export_json(self, sample_ts_item):
        """测试导出 JSON 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            export_items_json([sample_ts_item], filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]['title'] == 'Dr.'
            assert data[0]['name'] == '张三'
        finally:
            os.unlink(filepath)

    def test_export_json_empty(self):
        """测试导出空列表"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            export_items_json([], filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert data == []
        finally:
            os.unlink(filepath)

    def test_export_json_multiple(self):
        """测试导出多个 Item"""
        items = [
            TsItem(title="A", name="张三"),
            TsItem(title="B", name="李四"),
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            export_items_json(items, filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert len(data) == 2
        finally:
            os.unlink(filepath)


class TestExportItemsCsv:
    """export_items_csv 函数测试"""

    def test_export_csv(self, sample_ts_item):
        """测试导出 CSV 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            export_items_csv([sample_ts_item], filepath)
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            assert 'title' in content
            assert 'Dr.' in content
            assert '张三' in content
        finally:
            os.unlink(filepath)

    def test_export_csv_empty(self):
        """测试导出空列表"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            export_items_csv([], filepath)
            # 空文件也应成功创建
            assert os.path.exists(filepath)
        finally:
            os.unlink(filepath)

    def test_export_csv_with_specified_fields(self):
        """测试指定字段导出"""
        item = TsItem(title="Dr.", name="张三", email="z@e.com", phone="123456")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            filepath = f.name

        try:
            export_items_csv([item], filepath, fields=['title', 'name'])
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            assert 'title,name' in content
            assert 'Dr.,张三' in content
            # 不应包含未指定的字段
            assert 'email' not in content.split('\n')[0]
        finally:
            os.unlink(filepath)
