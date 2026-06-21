from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Pydantic Schema <-> API Input/Output
#So pydantic :
    # Convert Python objects into API responses
    # Validate incoming/outgoing data

# --- User ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- Category ---
class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Expense ---
class ExpenseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    amount: float
    category_id: int

class ExpenseOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    amount: float
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True



# from_attributes=True
    #it allows Pydantic to read data from the SQLAlchemy object returned by the database query. It does not create the database relationship itself. That relationship already exists through the SQLAlchemy model.

# Example of from_attributes=True:
    #     A very simple example:

    # SQLAlchemy model (database object)
    # class Category(Base):
    #     __tablename__ = "categories"

    #     id = Column(Integer, primary_key=True)
    #     name = Column(String)

    # Imagine SQLAlchemy returns:

    # category = Category(
    #     id=1,
    #     name="Books"
    # )

    # This is a Python object, not a dictionary.

    # You access it like:

    # category.id      # 1
    # category.name    # "Books"
    # Pydantic schema
    # class CategoryOut(BaseModel):
    #     id: int
    #     name: str

    #     class Config:
    #         from_attributes = True

    # Now Pydantic can do:

    # response = CategoryOut.model_validate(category)

    # print(response)

    # Output:

    # CategoryOut(
    #     id=1,
    #     name='Books'
    # )

    # because from_attributes=True allows Pydantic to read:

    # category.id
    # category.name

    # from the SQLAlchemy object.

    # Without from_attributes=True, Pydantic expects something like:

    # {
    #     "id": 1,
    #     "name": "Books"
    # }
    # (a dictionary) instead of a SQLAlchemy object.