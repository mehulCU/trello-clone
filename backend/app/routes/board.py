from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.board import Board

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE BOARD
@router.post("/boards")
def create_board(title: str, db: Session = Depends(get_db)):
    board = Board(title=title, background="#0079bf")  # default blue
    try:
        board = Board(title=title)
        db.add(board)
        db.commit()
        db.refresh(board)
        return board
    except Exception as e:
        print("ERROR:", e)  # 🔥 THIS WILL SHOW REAL ERROR
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/boards")
def get_boards(db: Session = Depends(get_db)):
    boards = db.query(Board).all()

    return [
        {
            "id": b.id,
            "title": b.title,
            "background": b.background
        }
        for b in boards
    ]

@router.put("/boards/{board_id}/background")
def update_background(board_id: int, background: str, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    board.background = background
    db.commit()

    return {"message": "Background updated"}