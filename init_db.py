#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EmailForward - 数据库初始化工具
在系统启动时自动初始化数据库，创建必要的表和初始用户/角色
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role
import hashlib
import logging
import os
import random
import string

# 配置日志
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """
    对密码进行哈希处理
    
    Args:
        password: 原始密码
    
    Returns:
        哈希后的密码
    """
    return hashlib.sha256(password.encode()).hexdigest()

def generate_random_key(length=36):
    """
    生成随机密钥
    
    Args:
        length: 密钥长度
    
    Returns:
        随机密钥字符串
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def init_db(db_url="sqlite:///./users.db", echo=False):
    """
    初始化数据库，创建表格和初始用户
    
    Args:
        db_url: 数据库连接URL
        echo: 是否打印SQL语句
    
    Returns:
        bool: 初始化是否成功
    """
    try:
        # 检查数据库文件是否存在
        db_file = db_url.split("///")[-1]
        db_exists = os.path.exists(db_file) if "sqlite" in db_url else True
        
        # 创建数据库引擎
        engine = create_engine(db_url, echo=echo)
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 创建Session
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 检查是否存在admin用户
            admin_user = session.query(User).filter_by(username="admin").first()
            if not admin_user:
                # 生成随机密钥
                random_key = generate_random_key()
                
                # 创建admin用户
                password = hash_password("admin")
                admin_user = User(
                    username="admin", password=password, role="admin", key=random_key
                )
                session.add(admin_user)
                logger.info(f"Admin user created with random key: {random_key}")
            else:
                logger.info("Admin user already exists.")

            # 检查是否存在admin角色
            admin_role = session.query(Role).filter_by(role="admin").first()
            if not admin_role:
                # 生成随机密钥(如果admin用户已存在，则使用不同的随机密钥)
                random_key = generate_random_key()
                
                # 创建admin角色
                admin_role = Role(role="admin", email="@localhost.com", key=random_key)
                session.add(admin_role)
                logger.info(f"Admin role created with random key: {random_key}")
            else:
                logger.info("Admin role already exists.")

            # 提交更改
            session.commit()
            logger.info("Database initialized successfully!")
            
            # 如果是新创建的数据库，记录一条特殊信息
            if not db_exists:
                logger.warning("新数据库已创建! 默认管理员账号: admin, 密码: admin，请及时修改!")
                
            return True
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


if __name__ == "__main__":
    # 配置控制台日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    
    if init_db(echo=True):
        print("Database initialization completed.")
    else:
        print("Database initialization failed.")
