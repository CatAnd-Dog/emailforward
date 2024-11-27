from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role
import hashlib


def init_db():
    # 创建数据库引擎
    engine = create_engine("sqlite:///./users.db", echo=True)
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    # 创建Session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 检查是否存在admin用户
        admin_user = session.query(User).filter_by(username="admin").first()
        if not admin_user:
            # 创建admin用户
            password = hashlib.sha256("admin".encode()).hexdigest()
            admin_user = User(
                username="admin", password=password, role="admin", key="admin"
            )
            session.add(admin_user)
            print("Admin user created.")
        else:
            print("Admin user already exists.")

        # 检查是否存在admin角色
        admin_role = session.query(Role).filter_by(role="admin").first()
        if not admin_role:
            # 创建admin角色
            admin_role = Role(role="admin", email="@localhost.com")
            session.add(admin_role)
            print("Admin role created.")
        else:
            print("Admin role already exists.")

        # 提交更改
        session.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()
    print("Database initialized with EmailSubmission table!")


if __name__ == "__main__":
    init_db()
