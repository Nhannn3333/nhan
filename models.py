# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    displayname = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    failed_attempts = Column(Integer, default=0)  # Số lần đăng nhập sai
    pin_code = Column(String, nullable=True)  # Mã PIN để reset mật khẩu
