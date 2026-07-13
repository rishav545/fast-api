from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


db_url = "postgresql://postgres:root@localhost:5432/fastapi"
engine = create_engine(db_url)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


