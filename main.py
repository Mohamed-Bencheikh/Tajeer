from test import UserRole, users_collection
from typing import Union

import uvicorn
from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pymongo import MongoClient

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


# inlHA7sbN8Yi4srm
@app.get("/")
def index():
  return RedirectResponse(url="/login")


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request, user: str):
  return templates.TemplateResponse("welcome.html", {
      "request": request,
      "user": user
  })


# Define the route to serve the HTML form
@app.get("/login", response_class=HTMLResponse)
async def form(request: Request):
  return templates.TemplateResponse("index.html", {"request": request})


@app.post("/connect")
def connect(username: str = Form(...), password: str = Form(...)):
  uri = f"mongodb+srv://{username}:{password}@cluster0.koz4qat.mongodb.net/?retryWrites=true&w=majority"
  try:
    client = MongoClient(uri)
    client.admin.command('ping')
    return "You successfully connected to MongoDB!"
  except Exception as e:
    return e


@app.post("/register")
def create_user(name: str = Form(...),
                username: str = Form(...),
                password: str = Form(...),
                email: str = Form(...),
                role: Union[UserRole, str] = Form(...)):
  # hashed_password = pwd_context.hash(password)
  doc = {
      "name": name,
      "username": username,
      "email": email,
      "password": password,
      "role": role
  }
  try:
    users_collection.insert_one(doc)
    return f"User {doc['username']} created successfully!"

  except Exception as e:
    return e


@app.get("/users")
def get_all_users():
  try:
    users = list(users_collection.find())
    return users
  except Exception as e:
    return e


@app.get("/user/{username}")
def get_user(username: str):
  try:
    user = users_collection.find_one({"username": username})
    return user['name']
  except Exception as e:
    return e


@app.post("/login")
def login(request: Request,username: str = Form(...), password: str = Form(...)):

  try:
    user = users_collection.find_one({
        "username": username,
        "password": password
    })
    if user:
      return templates.TemplateResponse("welcome.html",
                                {"request": request, "user": user['name']})
    else:
      return templates.TemplateResponse(
      "index.html", {"request": request, "error": "Invalid user or password!"})

  except Exception as e:
    return templates.TemplateResponse("index.html", {"request": request, "error": str(e)})

@app.post('upload')
def upload(file: UploadFile = Form(...)):
  return file.filename

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
