from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Khai báo Base class cho SQLAlchemy
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    displayname = Column(String)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    failed_attempts = Column(Integer, default=0)  # Số lần nhập sai mật khẩu
    is_locked = Column(Boolean, default=False)   # Trạng thái khóa tài khoản

# Cấu hình cơ sở dữ liệu SQLite
DATABASE_URL = "sqlite:///./test.db"

# Tạo engine kết nối đến cơ sở dữ liệu
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Tạo các bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Tạo SessionLocal để tương tác với cơ sở dữ liệu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm tìm người dùng theo username
def get_user_by_username(db: Session, username: str):
    """
    Lấy người dùng từ cơ sở dữ liệu dựa vào tên đăng nhập.
    """
    return db.query(User).filter(User.username == username).first()

# Hàm tạo người dùng mới
def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    """
    Tạo tài khoản người dùng mới và lưu vào cơ sở dữ liệu.
    """
    db_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Hàm khóa tài khoản người dùng
def lock_user_account(db: Session, user_id: int):
    """
    Khóa tài khoản của người dùng.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_locked = True
        db.commit()

# Hàm đặt lại số lần đăng nhập sai
def reset_failed_attempts(db: Session, user_id: int):
    """
    Đặt lại số lần nhập sai mật khẩu của người dùng về 0.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.failed_attempts = 0
        db.commit()

# Hàm tăng số lần nhập sai mật khẩu
def increment_failed_attempts(db: Session, user_id: int):
    """
    Tăng số lần nhập sai mật khẩu. Nếu đạt 3 lần, khóa tài khoản.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.failed_attempts += 1
        if user.failed_attempts >= 3:  # Nếu số lần sai đạt ngưỡng, khóa tài khoản
            user.is_locked = True
        db.commit()
