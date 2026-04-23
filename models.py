# -*- coding: utf-8 -*-

"""
数据库模型定义

定义 SQLAlchemy ORM 模型，用于将爬取的数据持久化到数据库中。
支持 TsItem, CourseItem, ArticleItem 三种数据模型的存储。
"""

from datetime import datetime
from typing import Optional, List
import hashlib
import json

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean,
    create_engine, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()


class TsModel(Base):
    """
    TS (Teacher/Student) 数据库模型

    对应 TsItem，存储教师/学生相关信息。
    """
    __tablename__ = 'ts_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True, comment='标题/名称')
    stu = Column(String(50), nullable=True, comment='学生/教师标识')
    name = Column(String(255), nullable=True, comment='姓名')
    gender = Column(String(10), nullable=True, comment='性别')
    age = Column(Integer, nullable=True, comment='年龄')
    email = Column(String(255), nullable=True, comment='邮箱地址')
    phone = Column(String(50), nullable=True, comment='联系电话')
    department = Column(String(255), nullable=True, comment='院系/部门')
    major = Column(String(255), nullable=True, comment='专业')
    grade = Column(String(100), nullable=True, comment='年级/职称')
    avatar_url = Column(String(1024), nullable=True, comment='头像URL')
    profile_url = Column(String(1024), nullable=True, comment='个人主页URL')
    created_at = Column(DateTime, default=datetime.now, comment='数据创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='数据更新时间')
    crawl_time = Column(DateTime, default=datetime.now, comment='爬取时间戳')
    source_url = Column(String(1024), nullable=True, comment='来源页面URL')
    source_site = Column(String(255), nullable=True, comment='来源站点名称')
    item_hash = Column(String(64), unique=True, nullable=False, comment='数据唯一哈希（用于去重）')
    status = Column(String(20), default='active', comment='数据状态: active/inactive/archived')

    __table_args__ = (
        Index('idx_ts_name', 'name'),
        Index('idx_ts_email', 'email'),
        Index('idx_ts_department', 'department'),
        Index('idx_ts_status', 'status'),
        Index('idx_ts_crawl_time', 'crawl_time'),
        UniqueConstraint('item_hash', name='uq_ts_item_hash'),
    )

    def __repr__(self):
        return f"<TsModel(id={self.id}, name={self.name!r}, title={self.title!r})>"

    def to_dict(self) -> dict:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'stu': self.stu,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'major': self.major,
            'grade': self.grade,
            'avatar_url': self.avatar_url,
            'profile_url': self.profile_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'crawl_time': self.crawl_time.isoformat() if self.crawl_time else None,
            'source_url': self.source_url,
            'source_site': self.source_site,
            'item_hash': self.item_hash,
            'status': self.status,
        }


class CourseModel(Base):
    """
    课程信息数据库模型

    对应 CourseItem，存储课程相关信息。
    """
    __tablename__ = 'course_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(100), nullable=True, comment='课程ID')
    course_name = Column(String(255), nullable=False, comment='课程名称')
    teacher_name = Column(String(255), nullable=True, comment='授课教师')
    teacher_id = Column(String(100), nullable=True, comment='教师ID')
    department = Column(String(255), nullable=True, comment='开课院系')
    semester = Column(String(100), nullable=True, comment='学期')
    credits = Column(Float, nullable=True, comment='学分')
    hours = Column(Integer, nullable=True, comment='学时')
    schedule = Column(Text, nullable=True, comment='上课时间/课表')
    location = Column(String(255), nullable=True, comment='上课地点')
    capacity = Column(Integer, nullable=True, comment='容量')
    enrolled = Column(Integer, nullable=True, comment='已选人数')
    description = Column(Text, nullable=True, comment='课程描述')
    syllabus_url = Column(String(1024), nullable=True, comment='教学大纲URL')
    source_url = Column(String(1024), nullable=True, comment='来源页面URL')
    crawl_time = Column(DateTime, default=datetime.now, comment='爬取时间戳')

    __table_args__ = (
        Index('idx_course_name', 'course_name'),
        Index('idx_course_teacher', 'teacher_name'),
        Index('idx_course_semester', 'semester'),
        Index('idx_course_department', 'department'),
        Index('idx_course_crawl_time', 'crawl_time'),
    )

    def __repr__(self):
        return f"<CourseModel(id={self.id}, course_name={self.course_name!r}, teacher={self.teacher_name!r})>"

    def to_dict(self) -> dict:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'course_name': self.course_name,
            'teacher_name': self.teacher_name,
            'teacher_id': self.teacher_id,
            'department': self.department,
            'semester': self.semester,
            'credits': self.credits,
            'hours': self.hours,
            'schedule': self.schedule,
            'location': self.location,
            'capacity': self.capacity,
            'enrolled': self.enrolled,
            'description': self.description,
            'syllabus_url': self.syllabus_url,
            'source_url': self.source_url,
            'crawl_time': self.crawl_time.isoformat() if self.crawl_time else None,
        }

    def is_full(self) -> bool:
        """判断课程是否已满"""
        if self.capacity is not None and self.enrolled is not None:
            return self.enrolled >= self.capacity
        return False

    def get_occupancy_rate(self) -> Optional[float]:
        """获取课程占用率（0.0 ~ 1.0）"""
        if self.capacity is not None and self.enrolled is not None:
            if self.capacity == 0:
                return 0.0
            return min(1.0, self.enrolled / self.capacity)
        return None


class ArticleModel(Base):
    """
    文章/公告信息数据库模型

    对应 ArticleItem，存储文章、公告、新闻等内容。
    """
    __tablename__ = 'article_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(100), nullable=True, comment='文章ID')
    title = Column(String(255), nullable=False, comment='文章标题')
    author = Column(String(255), nullable=True, comment='作者')
    publish_date = Column(DateTime, nullable=True, comment='发布日期')
    content = Column(Text, nullable=True, comment='文章内容（HTML或纯文本）')
    summary = Column(Text, nullable=True, comment='文章摘要')
    tags = Column(Text, nullable=True, comment='标签列表（逗号分隔或JSON）')
    category = Column(String(100), nullable=True, comment='分类')
    view_count = Column(Integer, nullable=True, comment='浏览次数')
    attachment_urls = Column(Text, nullable=True, comment='附件URL列表（JSON格式）')
    cover_image_url = Column(String(1024), nullable=True, comment='封面图片URL')
    source_url = Column(String(1024), nullable=True, comment='来源页面URL')
    source_site = Column(String(255), nullable=True, comment='来源站点名称')
    crawl_time = Column(DateTime, default=datetime.now, comment='爬取时间戳')

    __table_args__ = (
        Index('idx_article_title', 'title'),
        Index('idx_article_author', 'author'),
        Index('idx_article_category', 'category'),
        Index('idx_article_publish_date', 'publish_date'),
        Index('idx_article_crawl_time', 'crawl_time'),
    )

    def __repr__(self):
        return f"<ArticleModel(id={self.id}, title={self.title!r}, author={self.author!r})>"

    def to_dict(self) -> dict:
        """将模型转换为字典"""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'title': self.title,
            'author': self.author,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'content': self.content,
            'summary': self.summary,
            'tags': self.tags,
            'category': self.category,
            'view_count': self.view_count,
            'attachment_urls': self.attachment_urls,
            'cover_image_url': self.cover_image_url,
            'source_url': self.source_url,
            'source_site': self.source_site,
            'crawl_time': self.crawl_time.isoformat() if self.crawl_time else None,
        }

    def get_tags_list(self) -> List[str]:
        """获取标签列表"""
        if not self.tags:
            return []
        try:
            parsed = json.loads(self.tags)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_attachment_list(self) -> List[str]:
        """获取附件URL列表"""
        if not self.attachment_urls:
            return []
        try:
            parsed = json.loads(self.attachment_urls)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
        return [u.strip() for u in self.attachment_urls.split(',') if u.strip()]

    def has_attachments(self) -> bool:
        """是否有附件"""
        return len(self.get_attachment_list()) > 0


# ========== 数据库连接和会话管理 ==========

def get_engine(db_url: str = 'sqlite:///ts_data.db', echo: bool = False):
    """
    创建数据库引擎

    Args:
        db_url: 数据库连接URL，默认使用 SQLite
        echo: 是否打印SQL语句

    Returns:
        Engine: SQLAlchemy 引擎实例
    """
    return create_engine(db_url, echo=echo)


def init_db(engine=None, db_url: str = 'sqlite:///ts_data.db', echo: bool = False):
    """
    初始化数据库，创建所有表

    Args:
        engine: 已有的数据库引擎（可选）
        db_url: 数据库连接URL（当 engine 为 None 时使用）
        echo: 是否打印SQL语句

    Returns:
        Engine: 数据库引擎实例
    """
    if engine is None:
        engine = get_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """
    获取数据库会话

    Args:
        engine: 数据库引擎

    Returns:
        Session: SQLAlchemy 会话实例
    """
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session()


def drop_all_tables(engine):
    """
    删除所有表（谨慎使用）

    Args:
        engine: 数据库引擎
    """
    Base.metadata.drop_all(engine)
