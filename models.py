# models.py
from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    displayname = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    failed_attempts = Column(Integer, default=0)  # Thêm trường đếm số lần đăng nhập sai
    is_locked = Column(Boolean, default=False)  # Trạng thái khóa tài khoản
