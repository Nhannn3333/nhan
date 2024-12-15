from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from crud import SessionLocal, get_user_by_username, create_user, update_failed_attempts, reset_failed_attempts, set_user_pin, verify_user_pin, update_password
from models import User
import random
import hashlib
import requests  # Thêm thư viện requests để tải HTML từ GitHub Pages

app = FastAPI()

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

# Hàm tải trang HTML từ GitHub Pages
def get_html_from_github_page(file_name: str) -> str:
    url = f"https://nhannn3333.github.io/Nhan_html/{file_name}"  # Đảm bảo link GitHub Page chính xác
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: Unable to fetch {file_name}"

# Trang đăng ký
@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    html_content = get_html_from_github_page("signUp.html")
    return HTMLResponse(content=html_content, status_code=200)

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
        html_content = get_html_from_github_page("signUp.html")
        return HTMLResponse(content=html_content.replace("<!-- error message -->", "Username already exists!"), status_code=400)

    create_user(db, displayname, username, hash_password(password))
    return RedirectResponse(url="/login", status_code=302)

# Trang đăng nhập
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    html_content = get_html_from_github_page("index.html")
    return HTMLResponse(content=html_content, status_code=200)

# Xử lý đăng nhập
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        html_content = get_html_from_github_page("index.html")
        return HTMLResponse(content=html_content.replace("<!-- error message -->", "User not found!"), status_code=400)

    # Kiểm tra số lần nhập sai
    if user.failed_attempts >= 3:
        # Tạo mã PIN và yêu cầu nhập
        pin_code = str(random.randint(100000, 999999))
        set_user_pin(db, user, pin_code)
        html_content = get_html_from_github_page("pin.html")
        return HTMLResponse(content=html_content.replace("{{ pin }}", pin_code), status_code=200)

    # Kiểm tra mật khẩu
    if user.hashed_password != hash_password(password):
        update_failed_attempts(db, user)
        html_content = get_html_from_github_page("index.html")
        return HTMLResponse(content=html_content.replace("<!-- error message -->", "Invalid password!"), status_code=400)

    # Đăng nhập thành công, reset số lần nhập sai
    reset_failed_attempts(db, user)
    html_content = get_html_from_github_page("index.html")
    return HTMLResponse(content=html_content.replace("<!-- success message -->", "Login successful!"), status_code=200)

# Trang nhập mã PIN
@app.post("/verify_pin", response_class=HTMLResponse)
def verify_pin(request: Request, username: str = Form(...), pin: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        html_content = get_html_from_github_page("index.html")
        return HTMLResponse(content=html_content.replace("<!-- error message -->", "User not found!"), status_code=400)

    if not verify_user_pin(db, user, pin):
        html_content = get_html_from_github_page("pin.html")
        return HTMLResponse(content=html_content.replace("{{ pin }}", "Invalid PIN. Please try again!"), status_code=400)

    # Mã PIN đúng, chuyển đến trang đổi mật khẩu
    return RedirectResponse(url=f"/reset_password?username={username}", status_code=302)

# Trang đổi mật khẩu
@app.get("/reset_password", response_class=HTMLResponse)
def reset_password_page(request: Request, username: str):
    html_content = get_html_from_github_page("reset.html")
    return HTMLResponse(content=html_content.replace("{{ username }}", username), status_code=200)

# Xử lý đổi mật khẩu
@app.post("/reset_password", response_class=HTMLResponse)
def reset_password(request: Request, username: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if user is None:
        html_content = get_html_from_github_page("index.html")
        return HTMLResponse(content=html_content.replace("<!-- error message -->", "User not found!"), status_code=400)

    # Cập nhật mật khẩu mới
    update_password(db, user, hash_password(new_password))
    reset_failed_attempts(db, user)
    return RedirectResponse(url="/login", status_code=302)
