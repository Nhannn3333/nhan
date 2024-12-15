# crud.py
from sqlalchemy.orm import Session
from models import User
import random
import string

# Lấy user theo username
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Tạo user mới
def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    db_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Cập nhật số lần nhập sai
def increment_failed_attempts(db: Session, user: User):
    user.failed_attempts += 1
    db.commit()

# Reset số lần nhập sai
def reset_failed_attempts(db: Session, user: User):
    user.failed_attempts = 0
    db.commit()

# Cập nhật mã PIN
def set_user_pin(db: Session, user: User, pin: str):
    user.pin_code = pin
    db.commit()

# Sinh mã PIN ngẫu nhiên
def generate_pin_code():
    return ''.join(random.choices(string.digits, k=6))  # Mã PIN 6 chữ số
