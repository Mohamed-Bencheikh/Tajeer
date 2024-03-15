from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Define the route to serve the HTML form
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Define the route to handle form submission
@app.post("/submit")
async def submit_form(name: str, email: str):
    # Process form data
    data = {"name": name, "email": email}

    # Send data to API
    api_url = "https://example.com/api/endpoint"
    response = requests.post(api_url, json=data)

    if response.status_code == 200:
        return {"message": "Data submitted successfully"}
    else:
        return {"message": "Error submitting data"}

