from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.routes.alerts import router as alerts_router 
from app.scheduler.parser_task import run_parser_loop
from shared.app_info import get_app_name

app = FastAPI()  
app.include_router(alerts_router)

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

@app.on_event("startup")
async def startup_event():
    # Start the parser loop in the background
    print("Starting parser loop...")
    asyncio.create_task(run_parser_loop())