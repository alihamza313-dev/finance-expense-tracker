from sqlalchemy import String , DateTime , func, ForeignKey , Numeric
from database import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(primary_key = True , index = True)
    username : Mapped[str] = mapped_column(String(50) , unique = True , nullable = False)
    email : Mapped[str] = mapped_column(String(250) , unique = True , nullable = False)
    hashed_password : Mapped[str] = mapped_column(String(250),nullable = False)
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone = True) , server_default = func.now()) 
    categories: Mapped[list["Category"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    #with func.now() we can set the default value of created_at to the current timestamp when a new user is created by the posgresql database.

# Important PostgreSQL Concept
# This model translates roughly to:

# CREATE TABLE users (
#     id SERIAL PRIMARY KEY,
#     username VARCHAR(50) UNIQUE NOT NULL,
#     email VARCHAR(250) UNIQUE NOT NULL,
#     hashed_password VARCHAR(250) NOT NULL,
#     created_at TIMESTAMP DEFAULT NOW()
# );


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    owner: Mapped["User"] = relationship(
        back_populates="categories"
    )

    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    amount: Mapped[Numeric] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id")
    )

    owner: Mapped["User"] = relationship(
        back_populates="expenses"
    )

    category: Mapped["Category"] = relationship(
        back_populates="expenses"
    )



# SQLAlchemy Model <-> Database Table

# Pydantic Schema <-> API Input/Output