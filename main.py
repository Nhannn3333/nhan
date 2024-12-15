from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User
from database import get_db
from pydantic import BaseModel

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic models
class UserCreate(BaseModel):
    displayname: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Helpers
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, displayname: str, username: str, hashed_password: str):
    new_user = User(displayname=displayname, username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

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
    
    if db_user.failed_attempts >= 3:
        return {"message": "Account locked due to too many failed login attempts"}
    
    if not pwd_context.verify(user.password, db_user.hashed_password):
        db_user.failed_attempts += 1
        db.commit()
        remaining_attempts = 3 - db_user.failed_attempts
        if db_user.failed_attempts >= 3:
            return {"message": "Account locked due to too many failed login attempts"}
        return {"message": f"Invalid credentials. {remaining_attempts} attempts remaining."}
    
    # Reset failed attempts on successful login
    db_user.failed_attempts = 0
    db.commit()
    return {"message": f"Welcome {db_user.displayname}!"}
