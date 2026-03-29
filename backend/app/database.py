from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://trello_db_fknp_user:qEHTKtig7xwuSTHAIz4UufsL4tKZ9nqq@dpg-d74gc4npm1nc738u4gg0-a/trello_db_fknp"

engine = create_engine("postgresql://trello_db_fknp_user:qEHTKtig7xwuSTHAIz4UufsL4tKZ9nqq@dpg-d74gc4npm1nc738u4gg0-a/trello_db_fknp")

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
