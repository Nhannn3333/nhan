# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    displayname = Column(String, index=True)  # Thêm trường displayname
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
