from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, categories, expenses

app = FastAPI(title="Finance Expense Tracker")


# CORS = Cross-Origin Resource Sharing

# It controls whether a frontend from another origin (domain/port) is allowed to call your FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS middleware:
# - Allows frontend and backend on different origins to communicate.

# allow_origins:
# - Which websites can call API.

# allow_credentials:
# - Allow cookies/auth credentials.

# allow_methods:
# - Allowed HTTP methods.

# allow_headers:
# - Allowed request headers (Authorization, Content-Type, etc.)


app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(expenses.router)