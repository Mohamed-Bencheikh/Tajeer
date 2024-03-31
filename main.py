from database import users_collection
from typing import Union
import database as db
from models import User, LoginUser, Token
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pymongo import MongoClient
from authentication import authenticate_user, create_access_token, protected_route
import authentication as auth

app = FastAPI()
# OAuth2 Security Scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


# inlHA7sbN8Yi4srm
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    # return RedirectResponse(url="/user/login")


@app.post("/connect")
def connect(username: str = Form(...), password: str = Form(...)):
    uri = f"mongodb+srv://{username}:{password}@cluster0.koz4qat.mongodb.net/?retryWrites=true&w=majority"
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        return "You successfully connected to MongoDB!"
    except Exception as e:
        return e
# Define the route to serve the HTML form


@app.get("/login", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):

    try:
        user = users_collection.find_one({
            "username": username,
            "password": password
        })
        if user:
            return templates.TemplateResponse("index2.html",
                                              {"request": request, "user": user['username']})
        else:
            return templates.TemplateResponse(
                "form.html", {"request": request, "error": "Invalid user or password!"})

    except Exception as e:
        return templates.TemplateResponse("form.html", {"request": request, "error": str(e)})


@app.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/register")
def create_user(request: Request,
                fullname: str = Form(...),
                username: str = Form(...),
                password: str = Form(...),
                email: str = Form(...)
                ):
    # hashed_password = pwd_context.hash(password)
    try:
        db.create_user(fullname, username, email, password)
        return templates.TemplateResponse("blank.html", {"request": request, "user": fullname})
    except Exception as e:
        return "Operation failed: "+str(e)


@app.get("/users")
async def get_all_users():
    try:
        return db.fetch_all_users()
    except Exception as e:
        return "Operation failed: " + str(e)


@app.get("/user/{username}", response_model=Union[User, str])
async def get_user(username: str):
    try:
        return db.fetch_user(username)
    except Exception as e:
        return "Operaion failed: " + str(e)


@app.put("/update/{username}")
def update_user(username: str, data: dict):
    try:
        return db.update_user(username, data)
    except Exception as e:
        return "Operation failed: "+str(e)


@app.delete("/delete/{username}")
def delete_user(username: str):
    try:
        return db.remove_user(username)
    except Exception as e:
        return "Operation failed: "+str(e)


############################


async def get_current_user(request: Request):
    try:
        # Extract username and password from the request form
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")

        if not username or not password:
            raise HTTPException(
                status_code=400, detail="Username or password is missing")

        # Check if the provided username and password match a user in the database
        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if not user:
            raise HTTPException(
                status_code=401, detail="Invalid username or password")

        return user
    except Exception as e:
        # raise HTTPException(status_code=500, detail=str(e))
        return "error: "+str(e)

############################


@app.post('/upload')
async def upload_audio(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):

    fname = file.filename
    if fname.endswith('.mp3') or fname.endswith('.wav'):
        with open(f"audio_{fname}", "wb") as audio:
            audio.write(await file.read())
        return {"message": "Audio uploaded successfully"}
    else:
        return "Invalid file format. Please upload an MP3 or WAV file."


@app.get('/profile')
def profile(request: Request, token: str = Depends(protected_route)):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get('/test')
def test(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


@app.get('/forgot-password')
def forgot_password(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})


# Token route for generating access tokens
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth.login_for_access_token(form_data)

# Protected route requiring authentication


# @app.get("/protected")
# async def protected_route(token: str = Depends(oauth2_scheme)):
#     return await auth.protected_route(token)


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request, token: str = Depends(protected_route)):
    return templates.TemplateResponse("welcome.html", {
        "request": request
    })
