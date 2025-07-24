from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.health import router as health_router
from api.routes.image import router as image_router
from api.routes.video import router as video_router

load_dotenv()

app = FastAPI(title="Fal FastAPI Starter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router, prefix="/api")
app.include_router(video_router, prefix="/api")
app.include_router(health_router, prefix="/api")
