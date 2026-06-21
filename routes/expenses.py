from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from database import get_db
from models import Expense, Category
from schemas import ExpenseCreate, ExpenseOut
from auth.dependencies import get_current_user
from models import User

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseOut)
async def create_expense(
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify category belongs to user
    cat = await db.execute(
        select(Category).where(
            Category.id == data.category_id,
            Category.user_id == current_user.id
        )
    )
    if not cat.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Category not found")

    expense = Expense(**data.model_dump(), user_id=current_user.id)

    # this **data.model_dump() basically unpack comming data whic follow pydantic schema and in a dictoinary form but to store it into the database we need to convert it into a SQLAlchemy object and for that we use this syntax
    # # expense = Expense(    title="Food",    amount=500,    category_id=1,    user_id=10)
    # # So it is like we are converting the Pydantic object into a SQLAlchemy object

    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


@router.get("/", response_model=list[ExpenseOut])
async def get_expenses(
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Expense).where(Expense.user_id == current_user.id)
    if category_id:
        query = query.where(Expense.category_id == category_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{expense_id}", response_model=ExpenseOut)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseOut)
async def update_expense(
    expense_id: int,
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in data.model_dump().items():
        setattr(expense, key, value)

    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id
        )
    )
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    await db.delete(expense)
    await db.commit()
    return {"message": "Expense deleted"}










# Pydantic → SQLAlchemy → Database Flow
# 1. data: ExpenseCreate


# ExpenseCreate is a Pydantic schema.


# It validates incoming API data.


# Example request:
# {  "title": "Food",  "amount": 500,  "category_id": 1}
# FastAPI converts it into:
# data = ExpenseCreate(    title="Food",    amount=500,    category_id=1)

# 2. data.model_dump()


# Converts Pydantic object into a Python dictionary.


# Example:
# data.model_dump()
# Output:
# {    "title": "Food",    "amount": 500,    "category_id": 1}
# Note: It only creates a dictionary, it does not create a database object.

# 3. **data.model_dump()


# ** unpacks dictionary key-value pairs into keyword arguments.


# Example:
# Expense(**data.model_dump())
# is equal to:
# Expense(    title="Food",    amount=500,    category_id=1)

# 4. Expense(...)


# Expense is the SQLAlchemy database model.


# Creating Expense() creates a database model object.


# Example:
# expense = Expense(    title="Food",    amount=500,    category_id=1,    user_id=10)
# Now it is ready to store:
# db.add(expense)await db.commit()

# Complete line:
# expense = Expense(    **data.model_dump(),    user_id=current_user.id)
# Means:
# Pydantic object        |        | model_dump()        ↓Dictionary        |        | ** unpack        ↓SQLAlchemy Expense object        |        ↓Database record

# Reverse direction (Database → API Response)
# When returning data:
# return expense
# expense is a SQLAlchemy object.
# from_attributes=True allows Pydantic to read:
# expense.idexpense.titleexpense.amount
# and convert it into:
# {  "id": 1,  "title": "Food",  "amount": 500}
# Flow:
# SQLAlchemy object        |        | from_attributes=True        ↓Pydantic Response Schema        |        ↓JSON response

# Short Summary
# model_dump()→ Pydantic → Dictionary**→ Dictionary → Keyword argumentsSQLAlchemy Model()→ Creates database objectdb.add()→ Adds object to databasefrom_attributes=True→ Database object → Pydantic response