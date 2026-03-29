from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.list import List
from pydantic import BaseModel
from typing import List as ListType

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# ✅ CREATE LIST
# =========================
@router.post("/lists")
def create_list(title: str, board_id: int, db: Session = Depends(get_db)):
    lists = db.query(List).filter(List.board_id == board_id).all()
    position = len(lists)

    new_list = List(title=title, board_id=board_id, position=position)
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


# =========================
# ✅ GET LISTS
# =========================
@router.get("/lists/{board_id}")
def get_lists(board_id: int, db: Session = Depends(get_db)):
    return db.query(List).filter(List.board_id == board_id).order_by(List.position).all()


# =========================
# ✅ UPDATE LIST
# =========================
@router.put("/lists/{list_id}")
def update_list(list_id: int, title: str, db: Session = Depends(get_db)):
    list_obj = db.query(List).filter(List.id == list_id).first()

    if not list_obj:
        return {"error": "List not found"}

    list_obj.title = title
    db.commit()

    return {"message": "List updated"}


# =========================
# ✅ DELETE LIST
# =========================
@router.delete("/lists/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):
    list_obj = db.query(List).filter(List.id == list_id).first()

    if not list_obj:
        return {"error": "List not found"}

    db.delete(list_obj)
    db.commit()

    return {"message": "List deleted"}


# =========================
# 🔥 FIXED REORDER LISTS
# =========================

class ListOrder(BaseModel):
    order: ListType[int]


@router.put("/lists/reorder")
def reorder_lists(data: ListOrder, db: Session = Depends(get_db)):
    if not data.order:
        return {"error": "Empty order list"}

    for index, list_id in enumerate(data.order):
        list_obj = db.query(List).filter(List.id == list_id).first()

        if list_obj:
            list_obj.position = index

    db.commit()

    return {
        "message": "Lists reordered successfully",
        "new_order": data.order
    }