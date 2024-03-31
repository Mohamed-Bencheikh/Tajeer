import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from database import fetch_user
# Secret key for encoding/decoding JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Sample user database
# users_db = {
#     "user1": {"username": "user1"},
#     "user2": {"username": "user2"},
#     # Add more users as needed
# }

# Function to generate access token


def create_access_token(username: str, expires_delta: timedelta):
    to_encode = {"sub": username, "exp": datetime.utcnow() + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to verify JWT token


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = fetch_user(username)
        if user:
            return username
        else:
            return None  # User not found
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.JWTError:
        return None  # Invalid token


# Secret key for encoding/decoding JWT tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
# For demo, we set 5min as the lifetime for the generated token
TOKEN_EXPIRE_MINUTES = 5

# Security helper functions
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authenticate user function


def authenticate_user(username: str, password: str):
    user = fetch_user(username)
    if user and password == user["password"]:
        return user
    return None

# Create access token function


def create_access_token(username: str, expires_delta: timedelta):
    to_encode = {"sub": username, "exp": datetime.utcnow() + expires_delta}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token route for generating access tokens


async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        username=user["username"], expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route requiring authentication


async def protected_route(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Access Granted!", "user": user}
