from test import UserRole, users_collection
from typing import Union

import uvicorn
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
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
  return RedirectResponse(url="/user/login")


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request, user: str):
  return templates.TemplateResponse("welcome.html", {
      "request": request,
      "user": user
  })


# Define the route to serve the HTML form
@app.get("/user/login", response_class=HTMLResponse)
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


@app.post("/user/register")
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


@app.post("/user/login")
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

############################
async def get_current_user(request: Request):
  try:
      # Extract username and password from the request form
      form_data = await request.form()
      username = form_data.get("username")
      password = form_data.get("password")

      if not username or not password:
          raise HTTPException(status_code=400, detail="Username or password is missing")

      # Check if the provided username and password match a user in the database
      user = users_collection.find_one({
          "username": username,
          "password": password
      })

      if not user:
          raise HTTPException(status_code=401, detail="Invalid username or password")

      return user
  except Exception as e:
      # raise HTTPException(status_code=500, detail=str(e))
    return "error: "+str(e)

############################
@app.post('/upload')
async def upload_audio(file: UploadFile = File(...),current_user: dict = Depends(get_current_user)):
    
  fname = file.filename
  if fname.endswith('.mp3') or fname.endswith('.wav'):
    with open(f"audio_{fname}", "wb") as audio:
        audio.write(await file.read())
    return {"message": "Audio uploaded successfully"}
  else:
    return "Invalid file format. Please upload an MP3 or WAV file."
  
if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
