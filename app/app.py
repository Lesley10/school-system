from fastapi import FastAPI
from routes.school import router as schoolRouter

app = FastAPI()

app.include_router(schoolRouter)