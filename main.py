# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_username, create_user, lock_user_account
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Thêm middleware để xử lý CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dùng passlib để hash mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mô hình dữ liệu cho đăng ký và đăng nhập
class UserCreate(BaseModel):
    displayname: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Endpoint mặc định tại đường dẫn "/"
@app.get("/")
def read_root():
    return {"message": "Welcome to the Authentication Service!"}

# API đăng ký người dùng mới
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        return {"message": "Username already exists"}
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(db, displayname=user.displayname, username=user.username, hashed_password=hashed_password)
    return {"message": "User created successfully", "user_id": new_user.id}

# API đăng nhập người dùng
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user:
        return {"message": "Invalid username or password"}

    # Kiểm tra nếu tài khoản bị khóa
    if db_user.is_locked:
        return {"message": "Account is locked due to too many failed login attempts"}

    # Xác thực mật khẩu
    if not pwd_context.verify(user.password, db_user.hashed_password):
        db_user.failed_attempts += 1
        db.commit()

        # Khóa tài khoản nếu vượt quá 3 lần thất bại
        if db_user.failed_attempts >= 3:
            lock_user_account(db, db_user.id)
            return {"message": "Account is locked due to too many failed login attempts"}

        return {"message": "Invalid username or password"}
    
    # Reset số lần thất bại sau khi đăng nhập thành công
    db_user.failed_attempts = 0
    db.commit()

    return {"message": f"Welcome {db_user.displayname}!"}
