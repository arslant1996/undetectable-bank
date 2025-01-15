import os
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from server.app.models import Base, User
from server.app.connect import db_session, engine
from uuid import UUID


from typing import List

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}/accounts")
async def get_accounts(user_id: UUID, db: Session = Depends(get_db)):
    #return accounts
    pass

@app.post("/transfer")
async def transfer_funds(from_account_id: UUID, to_account_id: UUID, amount: float):
    # Perform transfer operation
    pass
