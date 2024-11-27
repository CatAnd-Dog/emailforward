# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    UniqueConstraint,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 用于存储用户信息
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(15), nullable=False)
    key = Column(String(255), nullable=False)


# 用于存储角色信息
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(32), nullable=False)
    email = Column(String(120), nullable=False)

    __table_args__ = (UniqueConstraint("role", "email", name="uix_role_email"),)


# 用于存储邮件接收记录
class Record(Base):
    __tablename__ = "records"
    id = Column(Integer, primary_key=True, index=True)
    email_user = Column(String, nullable=False, index=True)
    email_domain = Column(String, nullable=False, index=True)
    from_field = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    text_plain = Column(Text, nullable=False)
    text_html = Column(Text, nullable=False)
    # is_able = Column(Integer, default=1)  # 是否允许
    created_at = Column(DateTime, default=func.now())  # 创建时间


# 用于存储邮件发送记录
class EmailSubmission(Base):
    __tablename__ = "email_submissions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)  # 发送者
    from_field = Column(String, nullable=False)  # 发送者邮箱
    to_field = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())  # 创建时间
