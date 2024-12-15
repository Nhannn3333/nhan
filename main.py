# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_username, create_user, increment_failed_attempts, reset_failed_attempts
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

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

class UserCreate(BaseModel):
    displayname: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        return {"message": "Username already exists"}
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(db, displayname=user.displayname, username=user.username, hashed_password=hashed_password)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user:
        return {"message": "Invalid username or password"}
    
    if db_user.is_locked:
        return {"message": "Account is locked due to multiple failed attempts. Please contact support."}

    if not pwd_context.verify(user.password, db_user.hashed_password):
        increment_failed_attempts(db, db_user)
        attempts_left = 3 - db_user.failed_attempts
        if db_user.is_locked:
            return {"message": "Account is locked due to multiple failed attempts. Please contact support."}
        return {"message": f"Invalid username or password. {attempts_left} attempts remaining."}

    # Reset failed attempts on successful login
    reset_failed_attempts(db, db_user)
    return {"message": f"Welcome {db_user.displayname}!"}
