from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base
from crud import (
    get_user_by_username,
    create_user,
    update_failed_attempts,
    reset_failed_attempts,
    set_user_pin,
    verify_user_pin,
    update_password
)
from passlib.context import CryptContext
from pydantic import BaseModel
import random

# Khởi tạo FastAPI
app = FastAPI()

# Tạo bảng trong cơ sở dữ liệu
Base.metadata.create_all(bind=engine)

# Context mã hóa mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Khai báo các schema
class UserCreate(BaseModel):
    displayname: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PinVerification(BaseModel):
    username: str
    pin: str
    new_password: str

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        return {"message": "Username already exists"}
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(
        db, 
        displayname=user.displayname, 
        username=user.username, 
        hashed_password=hashed_password
    )
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if db_user.failed_attempts >= 3:
        # Yêu cầu mã PIN nếu nhập sai 3 lần
        pin_code = str(random.randint(1000, 9999))  # Tạo mã PIN ngẫu nhiên
        set_user_pin(db, db_user, pin_code)
        return {"message": "Too many failed attempts. Enter the PIN to proceed.", "pin_code": pin_code}

    if not pwd_context.verify(user.password, db_user.hashed_password):
        update_failed_attempts(db, db_user)
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Đăng nhập thành công
    reset_failed_attempts(db, db_user)
    return {"message": f"Welcome {db_user.displayname}!"}

@app.post("/verify-pin")
def verify_pin(data: PinVerification, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, data.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if verify_user_pin(db, db_user, data.pin):
        # Nếu mã PIN đúng, đổi mật khẩu
        hashed_password = pwd_context.hash(data.new_password)
        update_password(db, db_user, hashed_password)
        reset_failed_attempts(db, db_user)  # Reset số lần nhập sai
        set_user_pin(db, db_user, None)  # Xóa mã PIN
        return {"message": "Password updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid PIN")
