from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Secret key for encoding/decoding JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
# For demo, we set 5min as the lifetime for the generated token
TOKEN_EXPIRE_MINUTES = 5
# Security helper functions
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# OAuth2 Security Scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Sample user database
users_db = {
    "mohamed": {
        "username": "mohamed",
        "password": get_password_hash("m123"),
        "email": "mohamed@example.com",
    },
    "siinLab": {
        "username": "siinLab",
        "password": get_password_hash("S100"),
        "email": "contact@siinlab.com"
    }
}


# Pydantic model for token response


class Token(BaseModel):
    access_token: str
    token_type: str

# Pydantic model for user


class User(BaseModel):
    username: str
    email: Optional[str] = None

# Authenticate user function


def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return User(username=user["username"], email=user["email"])

# Create access token function


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token route for generating access tokens


@app.post("/token", response_model=Token)
async def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route requiring authentication


@app.get("/welcome", response_class=HTMLResponse)
async def welcome(request: User = Depends(authenticate_user)):
    return HTMLResponse(f"<h1>Welcome, {request.username}!</h1>")
