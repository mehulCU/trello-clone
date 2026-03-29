from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# 🔥 IMPORT ALL MODELS (VERY IMPORTANT)
from app.models.board import Board
from app.models.card import Card
from app.models.label import Label
from app.models.checklist import ChecklistItem
from app.models.member import CardMember
from app.models.attachment import Attachment
from fastapi.staticfiles import StaticFiles
from app.models.comment import Comment
from app.models.activity import Activity



# 🔥 IMPORT ROUTES
from app.routes import board, card, list

app = FastAPI()
import os
from fastapi.staticfiles import StaticFiles

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "../uploads")),
    name="uploads",
)
# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 CREATE TABLES
Base.metadata.create_all(bind=engine)

# 🔥 INCLUDE ROUTES
app.include_router(board.router)
app.include_router(card.router)
app.include_router(list.router)