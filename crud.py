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

# Hàm lấy user theo username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Hàm tạo user mới
def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    db_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hàm cập nhật số lần nhập sai mật khẩu
def update_failed_attempts(db: Session, user: User):
    user.failed_attempts += 1
    db.commit()

# Hàm reset số lần nhập sai
def reset_failed_attempts(db: Session, user: User):
    user.failed_attempts = 0
    db.commit()

# Hàm gán mã PIN cho user
def set_user_pin(db: Session, user: User, pin: str):
    user.pin_code = pin
    db.commit()

# Hàm kiểm tra mã PIN của user
def verify_user_pin(db: Session, user: User, pin: str):
    return user.pin_code == pin

# Hàm cập nhật mật khẩu mới
def update_password(db: Session, user: User, new_hashed_password: str):
    user.hashed_password = new_hashed_password
    db.commit()
