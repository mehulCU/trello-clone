from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://trello_user:1234@localhost:5432/trello"

engine = create_engine("postgresql://trello_user:1234@localhost:5432/trello")

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()