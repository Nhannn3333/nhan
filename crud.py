from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from models import User

# Khai báo Base class cho SQLAlchemy
Base = declarative_base()

# Cấu hình cơ sở dữ liệu SQLite
DATABASE_URL = "sqlite:///./test.db"

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Tạo các bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Tạo SessionLocal để tương tác với cơ sở dữ liệu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm lấy thông tin người dùng dựa trên username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Hàm tạo người dùng mới
def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    db_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hàm tăng số lần đăng nhập sai
def increment_failed_attempts(db: Session, user: User):
    user.failed_attempts += 1
    if user.failed_attempts >= 3:
        user.is_locked = True  # Khóa tài khoản nếu vượt quá 3 lần
    db.commit()
    db.refresh(user)

# Hàm đặt lại số lần đăng nhập sai về 0
def reset_failed_attempts(db: Session, user: User):
    user.failed_attempts = 0
    db.commit()
    db.refresh(user)
