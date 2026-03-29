from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.card import Card
from app.models.label import Label
from app.models.checklist import ChecklistItem
from app.models.member import CardMember
from pydantic import BaseModel
from typing import List
from app.models.card import Card
from app.models.comment import Comment
from app.models.activity import Activity

from fastapi import UploadFile, File
import os
from app.models.attachment import Attachment

router = APIRouter()
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# 🔥 REORDER CARDS (MOVE TO TOP)
# =========================
class CardOrder(BaseModel):
    order: List[int]

@router.put("/cards/reorder")
def reorder_cards(data: CardOrder, db: Session = Depends(get_db)):
    if not data.order:
        raise HTTPException(status_code=400, detail="Order list is empty")

    cards = db.query(Card).filter(Card.id.in_(data.order)).all()

    if len(cards) != len(data.order):
        raise HTTPException(status_code=400, detail="Invalid card IDs")

    list_ids = set(card.list_id for card in cards)
    if len(list_ids) != 1:
        raise HTTPException(
            status_code=400,
            detail="All cards must belong to same list"
        )

    for index, card_id in enumerate(data.order):
        card = next((c for c in cards if c.id == card_id), None)
        if card:
            card.position = index

    db.commit()
    return {"message": "Cards reordered"}


# =========================
# CREATE CARD
# =========================
@router.post("/cards")
def create_card(title: str, list_id: int, db: Session = Depends(get_db)):
    last_card = (
        db.query(Card)
        .filter(Card.list_id == list_id)
        .order_by(Card.position.desc())
        .first()
    )

    new_position = last_card.position + 1 if last_card else 0

    card = Card(title=title, list_id=list_id, position=new_position)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


# =========================
# GET CARDS (UPDATED 🔥)
# =========================
@router.get("/cards/{list_id}")
def get_cards(list_id: int, db: Session = Depends(get_db)):
    cards = (
        db.query(Card)
        .filter(Card.list_id == list_id, Card.archived == False)
        .order_by(Card.position)
        .all()
    )

    result = []
    for card in cards:
        result.append({
            "id": card.id,
            "title": card.title,
            "description": card.description,
            "due_date": card.due_date,
            "cover_image": card.cover_image,

            # 🔥 COMMENTS
            "comments": [
                {"id": c.id, "text": c.text}
                for c in card.comments
            ] if card.comments else [],

            # 🔥 ACTIVITY LOG
            "activity": [
                {"id": a.id, "action": a.action}
                for a in card.activities
            ] if card.activities else [],

            "labels": [
                {"id": l.id, "name": l.name, "color": l.color}
                for l in card.labels
            ],
            "checklist": [
                {"id": i.id, "text": i.text, "completed": i.completed}
                for i in card.checklist
            ],
            "members": [
                {"id": m.id, "name": m.name}
                for m in card.members
            ],
            "attachments": [
                {"id": a.id, "file_name": a.file_name, "file_path": a.file_path}
                for a in card.attachments
            ]
        })

    return result
    

# =========================
# UPDATE CARD
# =========================
@router.put("/cards/{card_id}")
def update_card(card_id: int, title: str, description: str, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.title = title
    card.description = description

    db.commit()
    return {"message": "Card updated"}


# =========================
# ARCHIVE CARD
# =========================
@router.put("/cards/{card_id}/archive")
def archive_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.archived = True
    db.commit()

    return {"message": "Card archived"}


# =========================
# MOVE CARD
# =========================
@router.put("/cards/{card_id}/move")
def move_card(card_id: int, new_list_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.list_id = new_list_id

    last_card = (
        db.query(Card)
        .filter(Card.list_id == new_list_id)
        .order_by(Card.position.desc())
        .first()
    )

    card.position = last_card.position + 1 if last_card else 0

    db.commit()

    return {"message": "Card moved"}


# =========================
# LABELS
# =========================
@router.post("/cards/{card_id}/labels")
def add_label(card_id: int, name: str, color: str, db: Session = Depends(get_db)):
    label = Label(name=name, color=color, card_id=card_id)
    db.add(label)
    db.commit()
    return {"message": "Label added"}




@router.delete("/labels/{label_id}")
def delete_label(label_id: int, db: Session = Depends(get_db)):
    label = db.query(Label).filter(Label.id == label_id).first()

    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    db.delete(label)
    db.commit()
    return {"message": "Deleted"}


# =========================
# CHECKLIST
# =========================
@router.post("/cards/{card_id}/checklist")
def add_item(card_id: int, text: str, db: Session = Depends(get_db)):
    item = ChecklistItem(text=text, card_id=card_id)
    db.add(item)
    db.commit()
    return {"message": "Added"}


@router.put("/checklist/{item_id}")
def toggle_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.completed = not item.completed
    db.commit()
    return {"message": "Updated"}


# =========================
# MEMBERS
# =========================
@router.post("/cards/{card_id}/members")
def add_member(card_id: int, name: str, db: Session = Depends(get_db)):
    member = CardMember(name=name, card_id=card_id)
    db.add(member)
    db.commit()
    return {"message": "Added"}


# =========================
# DUE DATE
# =========================
@router.put("/cards/{card_id}/due")
def set_due(card_id: int, due_date: str, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.due_date = due_date
    db.commit()
    return {"message": "Due date set"}

@router.get("/cards/search/{board_id}")
def search_cards(board_id: int, query: str, db: Session = Depends(get_db)):
    cards = db.query(Card).filter(Card.title.ilike(f"%{query}%")).all()

    result = []
    for c in cards:
        result.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "cover_image": c.cover_image,
            "list_id": c.list_id, 
            "due_date": c.due_date,
            "labels": [{"id": l.id, "name": l.name, "color": l.color} for l in c.labels],
            "members": [{"id": m.id, "name": m.name} for m in c.members],
        })

    return result

@router.get("/cards/filter/{board_id}")
def filter_cards(
    board_id: int,
    label: str = None,
    member: str = None,
    due: str = None,
    db: Session = Depends(get_db),
):
    cards = db.query(Card).all()

    result = []

    for c in cards:
        if label and not any(l.name == label for l in c.labels):
            continue

        if member and not any(m.name == member for m in c.members):
            continue

        if due and c.due_date != due:
            continue

        result.append({
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "list_id": c.list_id, 
            "due_date": c.due_date,
            "labels": [{"id": l.id, "name": l.name, "color": l.color} for l in c.labels],
            "members": [{"id": m.id, "name": m.name} for m in c.members],
        })

    return result

@router.post("/cards/{card_id}/upload")
async def upload_file(
    card_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    attachment = Attachment(
        file_name=file.filename,
        file_path=file_path,
        card_id=card_id,
    )

    db.add(attachment)
    db.commit()

    return {"message": "File uploaded"}

@router.put("/cards/{card_id}/cover")
def set_cover(card_id: int, file_path: str, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    card.cover_image = file_path
    db.commit()

    return {"message": "Cover set"}

# =========================
# ADD COMMENT
# =========================
@router.post("/cards/{card_id}/comments")
def add_comment(card_id: int, text: str, db: Session = Depends(get_db)):
    comment = Comment(text=text, card_id=card_id)
    db.add(comment)

    # log activity
    activity = Activity(action=f"Comment added: {text}", card_id=card_id)
    db.add(activity)

    db.commit()
    return {"message": "Comment added"}

@router.get("/cards/{card_id}/comments")
def get_comments(card_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.card_id == card_id).all()

@router.get("/cards/{card_id}/comments")
def get_comments(card_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.card_id == card_id).all()