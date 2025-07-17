from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware
from shared.app_info import get_app_name

app = FastAPI()  

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origin_regex=r"http://localhost:\d+",
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/word-of-day") 
def word_of_day():     
    return { "word": "feces" }

@app.get("/app-name")
def app_name():
    return { "appName": get_app_name() }