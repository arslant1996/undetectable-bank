from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from pydantic import Extra

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List
import os

# Configuration using Pydantic Settings
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://bookdbadmin:dbpassword@db:5432/bookstore"

    class Config:
        env_file = ".env"
        extra = Extra.allow

settings = Settings()

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    accounts = relationship("BankAccount", back_populates="owner")

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    account = relationship("BankAccount", back_populates="transactions")

# Pydantic Models
class UserCreate(BaseModel):
    name: str

class BankAccountCreate(BaseModel):
    user_id: int

class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    description: str

class TransactionResponse(BaseModel):
    id: int
    amount: float
    description: str

    class Config:
        orm_mode = True

class BankAccountResponse(BaseModel):
    id: int
    balance: float
    transactions: List[TransactionResponse] = []

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    id: int
    name: str
    accounts: List[BankAccountResponse] = []

    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/accounts/", response_model=BankAccountResponse)
def create_account(account: BankAccountCreate, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.id == account.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_account = BankAccount(user_id=account.user_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: SessionLocal = Depends(get_db)):
    db_account = db.query(BankAccount).filter(BankAccount.id == transaction.account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    db_account.balance += transaction.amount
    db_transaction = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        description=transaction.description,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/accounts/transfer/")
def transfer_funds(source_account_id: int, target_account_id: int, amount: float, db: SessionLocal = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    source_account = db.query(BankAccount).filter(BankAccount.id == source_account_id).first()
    target_account = db.query(BankAccount).filter(BankAccount.id == target_account_id).first()

    if not source_account or not target_account:
        raise HTTPException(status_code=404, detail="Account not found")

    if source_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    source_account.balance -= amount
    target_account.balance += amount

    db.commit()
    return {"message": "Transfer successful"}

# Create tables
Base.metadata.drop_all(bind=engine) # remove this later
Base.metadata.create_all(bind=engine)

