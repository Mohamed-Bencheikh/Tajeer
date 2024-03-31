# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import User
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from auth import pwd_context, get_password_hash

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
app = FastAPI()
# OAuth2 Security Scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the current user from the access token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = users_db.tokens_db.get(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(username=user_data.get("sub"))


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/welcome")
async def welcome(user: User = Depends(get_current_user)):
    return {"message": f"Welcome, {user.username}!"}
