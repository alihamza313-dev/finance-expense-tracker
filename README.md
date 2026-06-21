# Finance Expense Tracker

A full-stack personal finance application for tracking expenses by category, built with a FastAPI backend and a vanilla HTML/CSS/JavaScript frontend.

## Features

- User registration and login with JWT authentication
- Passwords hashed with bcrypt
- Create and delete expense categories
- Full CRUD for expenses (create, read, update, delete)
- Filter expenses by category
- Dashboard with total spend, monthly spend, and category-wise breakdown
- RESTful API with protected routes

## Tech stack

**Backend**
- FastAPI
- SQLAlchemy (async ORM)
- PostgreSQL
- Alembic (database migrations)
- JWT (python-jose) for authentication
- Passlib (bcrypt) for password hashing

**Frontend**
- HTML, CSS, JavaScript (no frameworks)
- Communicates with the backend via REST API calls (fetch)

## Project structure

```
pfms/
├── alembic/                 # Database migrations
├── alembic.ini
├── auth/
│   ├── hash.py               # Password hashing
│   └── jwt.py                 # JWT creation and decoding
├── routes/
│   ├── auth.py                # Register, login, current user
│   ├── categories.py          # Category CRUD
│   └── expenses.py            # Expense CRUD
├── database.py               # Async DB engine and session
├── dependencies.py           # Auth dependency (get_current_user)
├── models.py                  # SQLAlchemy models
├── schemas.py                 # Pydantic schemas
├── main.py                    # FastAPI app entrypoint
└── indexpfms/
    └── index.html             # Frontend (HTML/CSS/JS)
```

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/alihamza313-dev/finance-expense-tracker.git
   cd finance-expense-tracker
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your PostgreSQL connection string
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   ```

4. Run database migrations
   ```bash
   alembic upgrade head
   ```

5. Start the backend
   ```bash
   uvicorn main:app --reload
   ```

6. Open `indexpfms/index.html` in your browser (or serve it with a local server)

## API endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive a JWT |
| GET | `/auth/me` | Get current logged-in user |
| POST | `/categories/` | Create a category |
| GET | `/categories/` | List user's categories |
| DELETE | `/categories/{id}` | Delete a category |
| POST | `/expenses/` | Create an expense |
| GET | `/expenses/` | List expenses (optional `category_id` filter) |
| GET | `/expenses/{id}` | Get a single expense |
| PUT | `/expenses/{id}` | Update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |

## License

This project is open source and available for learning purposes.
