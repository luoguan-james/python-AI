# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
# test
# 123
# 456

import scrapy
from scrapy import Field, Item
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import hashlib
import json


class TsItem(scrapy.Item):
    """
    TS (Teacher/Student) 爬虫数据模型

    用于存储从目标网站爬取的教师/学生相关信息。
    每个字段对应一个爬取的数据维度。
    """

    # ========== 基本信息 ==========
    title = scrapy.Field()          # 标题/名称
    stu = scrapy.Field()            # 学生/教师标识

    # ========== 扩展信息 ==========
    name = scrapy.Field()           # 姓名
    gender = scrapy.Field()         # 性别
    age = scrapy.Field()            # 年龄
    email = scrapy.Field()          # 邮箱地址
    phone = scrapy.Field()          # 联系电话
    department = scrapy.Field()     # 院系/部门
    major = scrapy.Field()          # 专业
    grade = scrapy.Field()          # 年级/职称
    avatar_url = scrapy.Field()     # 头像URL
    profile_url = scrapy.Field()    # 个人主页URL

    # ========== 时间信息 ==========
    created_at = scrapy.Field()     # 数据创建时间（自动填充当前时间）
    updated_at = scrapy.Field()     # 数据更新时间
    crawl_time = scrapy.Field()     # 爬取时间戳

    # ========== 元数据 ==========
    source_url = scrapy.Field()     # 来源页面URL
    source_site = scrapy.Field()    # 来源站点名称
    item_hash = scrapy.Field()      # 数据唯一哈希（用于去重）
    status = scrapy.Field()         # 数据状态: active/inactive/archived

    def __init__(self, *args, **kwargs):
        """初始化 Item，自动填充爬取时间和状态"""
        super().__init__(*args, **kwargs)
        if 'crawl_time' not in self or self['crawl_time'] is None:
            self['crawl_time'] = datetime.now().isoformat()
        if 'status' not in self or self['status'] is None:
            self['status'] = 'active'
        if 'created_at' not in self or self['created_at'] is None:
            self['created_at'] = datetime.now().isoformat()
        # 自动生成 item_hash（如果未提供）
        if 'item_hash' not in self or self['item_hash'] is None:
            self['item_hash'] = self._generate_hash()

    def _generate_hash(self) -> str:
        """基于关键字段生成唯一哈希值，用于去重"""
        raw = f"{self.get('title', '')}|{self.get('name', '')}|{self.get('email', '')}|{self.get('source_url', '')}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def get_full_name(self) -> str:
        """获取完整名称（title + name 的组合）"""
        title = self.get('title', '')
        name = self.get('name', '')
        if title and name:
            return f"{title} - {name}"
        return title or name or ''

    def to_dict(self) -> dict:
        """将 Item 转换为普通字典，过滤掉 None 值"""
        return {key: value for key, value in self.items() if value is not None}

    def to_dict_all(self) -> dict:
        """将 Item 转换为普通字典，保留所有字段（包括 None）"""
        return dict(self)

    def validate(self) -> bool:
        """
        验证 Item 数据完整性

        Returns:
            bool: 数据是否有效（至少包含 title 或 name 之一）
        """
        return bool(self.get('title') or self.get('name'))

    def get_required_fields(self) -> List[str]:
        """获取必填字段列表"""
        return ['title', 'name']

    def get_summary(self) -> str:
        """获取简短摘要信息"""
        parts = []
        if self.get('name'):
            parts.append(self['name'])
        if self.get('department'):
            parts.append(self['department'])
        if self.get('email'):
            parts.append(self['email'])
        return ' | '.join(parts) if parts else self.get('title', 'N/A')

    def __repr__(self):
        """友好的字符串表示"""
        return f"<TsItem(title={self.get('title', '')!r}, name={self.get('name', '')!r})>"


class CourseItem(scrapy.Item):
    """
    课程信息数据模型

    用于存储爬取的课程相关信息。
    """

    course_id = scrapy.Field()          # 课程ID
    course_name = scrapy.Field()        # 课程名称
    teacher_name = scrapy.Field()       # 授课教师
    teacher_id = scrapy.Field()         # 教师ID
    department = scrapy.Field()         # 开课院系
    semester = scrapy.Field()           # 学期
    credits = scrapy.Field()            # 学分
    hours = scrapy.Field()              # 学时
    schedule = scrapy.Field()           # 上课时间/课表
    location = scrapy.Field()           # 上课地点
    capacity = scrapy.Field()           # 容量
    enrolled = scrapy.Field()           # 已选人数
    description = scrapy.Field()        # 课程描述
    syllabus_url = scrapy.Field()       # 教学大纲URL
    source_url = scrapy.Field()         # 来源页面URL
    crawl_time = scrapy.Field()         # 爬取时间戳

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'crawl_time' not in self or self['crawl_time'] is None:
            self['crawl_time'] = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """将 Item 转换为普通字典，过滤掉 None 值"""
        return {key: value for key, value in self.items() if value is not None}

    def to_dict_all(self) -> dict:
        """将 Item 转换为普通字典，保留所有字段（包括 None）"""
        return dict(self)

    def validate(self) -> bool:
        """
        验证 Item 数据完整性

        Returns:
            bool: 数据是否有效（至少包含 course_name）
        """
        return bool(self.get('course_name'))

    def get_required_fields(self) -> List[str]:
        """获取必填字段列表"""
        return ['course_name', 'teacher_name']

    def get_summary(self) -> str:
        """获取简短摘要信息"""
        parts = []
        if self.get('course_name'):
            parts.append(self['course_name'])
        if self.get('teacher_name'):
            parts.append(f"教师: {self['teacher_name']}")
        if self.get('semester'):
            parts.append(self['semester'])
        return ' | '.join(parts) if parts else 'N/A'

    def is_full(self) -> bool:
        """判断课程是否已满"""
        cap = self.get('capacity')
        enr = self.get('enrolled')
        if cap is not None and enr is not None:
            try:
                return int(enr) >= int(cap)
            except (ValueError, TypeError):
                return False
        return False

    def get_occupancy_rate(self) -> Optional[float]:
        """获取课程占用率（0.0 ~ 1.0）"""
        cap = self.get('capacity')
        enr = self.get('enrolled')
        if cap is not None and enr is not None:
            try:
                cap_int = int(cap)
                if cap_int == 0:
                    return 0.0
                return min(1.0, int(enr) / cap_int)
            except (ValueError, TypeError):
                return None
        return None

    def __repr__(self):
        return f"<CourseItem(course_name={self.get('course_name', '')!r}, teacher={self.get('teacher_name', '')!r})>"


class ArticleItem(scrapy.Item):
    """
    文章/公告信息数据模型

    用于存储爬取的文章、公告、新闻等内容。
    """

    article_id = scrapy.Field()         # 文章ID
    title = scrapy.Field()              # 文章标题
    author = scrapy.Field()             # 作者
    publish_date = scrapy.Field()       # 发布日期
    content = scrapy.Field()            # 文章内容（HTML或纯文本）
    summary = scrapy.Field()            # 文章摘要
    tags = scrapy.Field()               # 标签列表（逗号分隔或JSON）
    category = scrapy.Field()           # 分类
    view_count = scrapy.Field()         # 浏览次数
    attachment_urls = scrapy.Field()    # 附件URL列表（JSON格式）
    cover_image_url = scrapy.Field()    # 封面图片URL
    source_url = scrapy.Field()         # 来源页面URL
    source_site = scrapy.Field()        # 来源站点名称
    crawl_time = scrapy.Field()         # 爬取时间戳

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'crawl_time' not in self or self['crawl_time'] is None:
            self['crawl_time'] = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """将 Item 转换为普通字典，过滤掉 None 值"""
        return {key: value for key, value in self.items() if value is not None}

    def to_dict_all(self) -> dict:
        """将 Item 转换为普通字典，保留所有字段（包括 None）"""
        return dict(self)

    def validate(self) -> bool:
        """
        验证 Item 数据完整性

        Returns:
            bool: 数据是否有效（至少包含 title）
        """
        return bool(self.get('title'))

    def get_required_fields(self) -> List[str]:
        """获取必填字段列表"""
        return ['title', 'author']

    def get_summary(self) -> str:
        """获取简短摘要信息"""
        parts = []
        if self.get('title'):
            parts.append(self['title'])
        if self.get('author'):
            parts.append(f"作者: {self['author']}")
        if self.get('publish_date'):
            parts.append(self['publish_date'])
        return ' | '.join(parts) if parts else 'N/A'

    def get_tags_list(self) -> List[str]:
        """获取标签列表"""
        tags = self.get('tags')
        if tags is None:
            return []
        if isinstance(tags, list):
            return tags
        if isinstance(tags, str):
            # 尝试解析 JSON 数组
            try:
                parsed = json.loads(tags)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            # 按逗号分隔
            return [t.strip() for t in tags.split(',') if t.strip()]
        return []

    def get_attachment_list(self) -> List[str]:
        """获取附件URL列表"""
        urls = self.get('attachment_urls')
        if urls is None:
            return []
        if isinstance(urls, list):
            return urls
        if isinstance(urls, str):
            try:
                parsed = json.loads(urls)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass
            # 按逗号分隔
            return [u.strip() for u in urls.split(',') if u.strip()]
        return []

    def has_attachments(self) -> bool:
        """是否有附件"""
        return len(self.get_attachment_list()) > 0

    def __repr__(self):
        return f"<ArticleItem(title={self.get('title', '')!r}, author={self.get('author', '')!r})>"


# ========== 辅助函数 ==========

def create_item(item_type: str, **kwargs) -> scrapy.Item:
    """
    工厂函数：根据类型创建对应的 Item 实例

    Args:
        item_type: Item 类型名称 ('ts', 'course', 'article')
        **kwargs: 字段键值对

    Returns:
        scrapy.Item: 对应的 Item 实例

    Raises:
        ValueError: 当 item_type 不支持时抛出
    """
    item_map = {
        'ts': TsItem,
        'course': CourseItem,
        'article': ArticleItem,
    }
    cls = item_map.get(item_type.lower())
    if cls is None:
        raise ValueError(
            f"Unsupported item type: {item_type}. "
            f"Supported types: {list(item_map.keys())}"
        )
    return cls(**kwargs)


def merge_items(base_item: scrapy.Item, override_item: scrapy.Item) -> scrapy.Item:
    """
    合并两个 Item，override_item 中的非 None 值会覆盖 base_item 中的值

    Args:
        base_item: 基础 Item
        override_item: 覆盖 Item

    Returns:
        scrapy.Item: 合并后的 Item（类型与 base_item 相同）

    Raises:
        TypeError: 当两个 Item 类型不一致时抛出
    """
    if type(base_item) is not type(override_item):
        raise TypeError(
            f"Cannot merge items of different types: "
            f"{type(base_item).__name__} vs {type(override_item).__name__}"
        )
    merged = base_item.__class__(base_item)
    for key in override_item.fields:
        value = override_item.get(key)
        if value is not None:
            merged[key] = value
    return merged


def batch_validate(items: List[scrapy.Item]) -> Dict[str, List[scrapy.Item]]:
    """
    批量验证 Item 列表，返回有效和无效的 Item 分组

    Args:
        items: Item 列表

    Returns:
        dict: {'valid': [...], 'invalid': [...]}
    """
    result = {'valid': [], 'invalid': []}
    for item in items:
        if hasattr(item, 'validate') and callable(item.validate):
            if item.validate():
                result['valid'].append(item)
            else:
                result['invalid'].append(item)
        else:
            # 如果没有 validate 方法，默认视为有效
            result['valid'].append(item)
    return result


def items_to_dicts(items: List[scrapy.Item], exclude_none: bool = True) -> List[dict]:
    """
    将 Item 列表批量转换为字典列表

    Args:
        items: Item 列表
        exclude_none: 是否过滤掉 None 值

    Returns:
        List[dict]: 字典列表
    """
    result = []
    for item in items:
        if hasattr(item, 'to_dict') and callable(item.to_dict):
            if exclude_none:
                result.append(item.to_dict())
            else:
                result.append(item.to_dict_all())
        else:
            result.append(dict(item))
    return result


def deduplicate_items(items: List[scrapy.Item], key_field: str = 'item_hash') -> List[scrapy.Item]:
    """
    对 Item 列表进行去重

    Args:
        items: Item 列表
        key_field: 用于去重的字段名，默认 'item_hash'

    Returns:
        List[scrapy.Item]: 去重后的 Item 列表
    """
    seen: set = set()
    result: List[scrapy.Item] = []
    for item in items:
        key = item.get(key_field)
        if key is None:
            # 如果没有指定字段，使用 repr 作为 key
            key = repr(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def filter_items(items: List[scrapy.Item], **conditions) -> List[scrapy.Item]:
    """
    根据条件过滤 Item 列表

    Args:
        items: Item 列表
        **conditions: 过滤条件，如 status='active', department='CS'

    Returns:
        List[scrapy.Item]: 过滤后的 Item 列表
    """
    result = []
    for item in items:
        match = True
        for key, expected_value in conditions.items():
            actual_value = item.get(key)
            if actual_value != expected_value:
                match = False
                break
        if match:
            result.append(item)
    return result


def sort_items(items: List[scrapy.Item], key_field: str, reverse: bool = False) -> List[scrapy.Item]:
    """
    对 Item 列表按指定字段排序

    Args:
        items: Item 列表
        key_field: 排序字段名
        reverse: 是否降序

    Returns:
        List[scrapy.Item]: 排序后的 Item 列表
    """
    return sorted(
        items,
        key=lambda item: (item.get(key_field) or ''),
        reverse=reverse
    )


def export_items_json(items: List[scrapy.Item], filepath: str, ensure_ascii: bool = False, indent: int = 2) -> None:
    """
    将 Item 列表导出为 JSON 文件

    Args:
        items: Item 列表
        filepath: 输出文件路径
        ensure_ascii: 是否确保 ASCII 编码
        indent: JSON 缩进空格数
    """
    data = items_to_dicts(items, exclude_none=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)


def export_items_csv(items: List[scrapy.Item], filepath: str, fields: Optional[List[str]] = None) -> None:
    """
    将 Item 列表导出为 CSV 文件

    Args:
        items: Item 列表
        filepath: 输出文件路径
        fields: 要导出的字段列表，默认使用第一个 Item 的所有字段
    """
    import csv

    if not items:
        # 写入空文件
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            pass
        return

    # 确定字段列表
    if fields is None:
        fields = list(items[0].fields.keys())

    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in items:
            row = {field: item.get(field, '') for field in fields}
            writer.writerow(row)
