import random
import string
import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_username
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from models import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dùng passlib để hash mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dùng bộ nhớ tạm thời để lưu thông tin về các lần đăng nhập không thành công và mã PIN
failed_logins = {}
pin_codes = {}

class UserCreate(BaseModel):
    displayname: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    pin: str = None  # Thêm trường pin để gửi mã pin

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    user_data = get_user_by_username(db, user.username)
    
    # Kiểm tra số lần đăng nhập sai
    if user.username not in failed_logins:
        failed_logins[user.username] = 0
    
    # Nếu người dùng đã nhập sai mật khẩu 3 lần
    if failed_logins[user.username] >= 3:
        if user.pin != pin_codes.get(user.username):
            raise HTTPException(status_code=401, detail="Invalid PIN")
        else:
            failed_logins[user.username] = 0  # Reset số lần đăng nhập sai sau khi nhập đúng PIN
            pin_codes.pop(user.username)  # Xóa mã PIN đã sử dụng

    # Kiểm tra mật khẩu
    if not user_data or not pwd_context.verify(user.password, user_data.hashed_password):
        failed_logins[user.username] += 1
        if failed_logins[user.username] >= 3:
            pin_code = ''.join(random.choices(string.digits, k=6))
            pin_codes[user.username] = pin_code
            print(f"Generated PIN for {user.username}: {pin_code}")  # In mã PIN ra console server
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": f"Welcome {user_data.displayname}!"}

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        return {"message": "Username already exists"}
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(db, displayname=user.displayname, username=user.username, hashed_password=hashed_password)
    return {"message": "User created successfully", "user_id": new_user.id}
