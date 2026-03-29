
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os

# 🔥 DATABASE
from app.database import engine
from app.models import Base

# 🔥 IMPORT ALL MODELS (VERY IMPORTANT)
from app.models.board import Board
from app.models.card import Card
from app.models.label import Label
from app.models.checklist import ChecklistItem
from app.models.member import CardMember
from app.models.attachment import Attachment
from app.models.comment import Comment
from app.models.activity import Activity

# 🔥 IMPORT ROUTES
from app.routes import board, card, list

# 🚀 CREATE APP
app = FastAPI()

# 🔥 CREATE TABLES
Base.metadata.create_all(bind=engine)

# 📁 HANDLE UPLOADS (VERY IMPORTANT FOR RENDER)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "../uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)

# ✅ CORS (ALLOW ALL FOR NOW)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 INCLUDE ROUTES
app.include_router(board.router)
app.include_router(card.router)
app.include_router(list.router)


# ✅ OPTIONAL ROOT (GOOD FOR TESTING)
@app.get("/")
def root():
    return {"message": "Trello Clone API is running 🚀"}


