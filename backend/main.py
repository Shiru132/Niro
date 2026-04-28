from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from backend.api.farm import router as farm_router


app = FastAPI()

app.include_router(farm_router, prefix="/farm")