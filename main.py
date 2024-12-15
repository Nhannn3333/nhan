from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from crud import SessionLocal, get_user_by_username, create_user, update_failed_attempts, reset_failed_attempts, set_user_pin, verify_user_pin, update_password
from models import User
import random
import hashlib

app = FastAPI()

# Cấu hình Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Dependency để tạo session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm băm mật khẩu (SHA256)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Trang đăng ký
@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("signUp.html", {"request": request})

# Xử lý đăng ký
@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    displayname: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_username(db, username)
    if user:
        return templates.TemplateResponse("signUp.html", {"request": request, "error": "Username already exists!"})

    create_user(db, displayname, username, hash_password(password))
    return RedirectResponse(url="/login", status_code=302)

# Trang đăng nhập
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Xử lý đăng nhập
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        return templates.TemplateResponse("index.html", {"request": request, "error": "User not found!"})

    # Kiểm tra số lần nhập sai
    if user.failed_attempts >= 3:
        # Tạo mã PIN và yêu cầu nhập
        pin_code = str(random.randint(100000, 999999))
        set_user_pin(db, user, pin_code)
        return templates.TemplateResponse("pin.html", {"request": request, "username": username, "pin": pin_code})

    # Kiểm tra mật khẩu
    if user.hashed_password != hash_password(password):
        update_failed_attempts(db, user)
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid password!"})

    # Đăng nhập thành công, reset số lần nhập sai
    reset_failed_attempts(db, user)
    return templates.TemplateResponse("index.html", {"request": request, "success": "Login successful!"})

# Trang nhập mã PIN
@app.post("/verify_pin", response_class=HTMLResponse)
def verify_pin(request: Request, username: str = Form(...), pin: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        return templates.TemplateResponse("index.html", {"request": request, "error": "User not found!"})

    if not verify_user_pin(db, user, pin):
        return templates.TemplateResponse("pin.html", {"request": request, "username": username, "pin": "Invalid PIN. Please try again!"})

    # Mã PIN đúng, chuyển đến trang đổi mật khẩu
    return RedirectResponse(url=f"/reset_password?username={username}", status_code=302)

# Trang đổi mật khẩu
@app.get("/reset_password", response_class=HTMLResponse)
def reset_password_page(request: Request, username: str):
    return templates.TemplateResponse("reset.html", {"request": request, "username": username})

# Xử lý đổi mật khẩu
@app.post("/reset_password", response_class=HTMLResponse)
def reset_password(request: Request, username: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        return templates.TemplateResponse("index.html", {"request": request, "error": "User not found!"})

    # Cập nhật mật khẩu mới
    update_password(db, user, hash_password(new_password))
    reset_failed_attempts(db, user)
    return RedirectResponse(url="/login", status_code=302)
