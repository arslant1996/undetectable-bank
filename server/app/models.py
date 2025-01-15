from sqlalchemy import create_engine, Column, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)

class BankAccountDB(Base):
    __tablename__ = "bank_accounts"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    account_number = Column(String, unique=True)
    balance = Column(Float)

class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    from_account_id = Column(String, ForeignKey("bank_accounts.id"))
    to_account_id = Column(String, ForeignKey("bank_accounts.id"))
    amount = Column(Float)
    timestamp = Column(String)

class User(BaseModel):
    id: UUID
    name: str
    email: str

class BankAccount(BaseModel):
    id: UUID
    user_id: UUID
    account_number: str
    balance: float = Field(gt=0)

class Transaction(BaseModel):
    id: UUID
    from_account_id: UUID
    to_account_id: UUID
    amount: float = Field(gt=0)
    timestamp: datetime