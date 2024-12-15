# crud.py
from sqlalchemy.orm import Session
from models import User
import random
import string
from sqlalchemy.orm import Session
from models import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    db_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def increment_login_attempts(db: Session, user: User):
    user.login_attempts += 1
    if user.login_attempts >= 3:
        user.is_locked = True
    db.commit()
    return user

def reset_login_attempts(db: Session, user: User):
    user.login_attempts = 0
    user.is_locked = False
    db.commit()
    return user
