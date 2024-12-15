from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    displayname = Column(String, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    failed_attempts = Column(Integer, default=0)  # Số lần nhập sai mật khẩu
    pin_code = Column(String, nullable=True)  # Mã PIN tạm thời
