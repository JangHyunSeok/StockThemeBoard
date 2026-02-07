from fastapi import APIRouter
from app.api.v1 import themes, stocks

api_router = APIRouter()

# Theme API
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])

# Stock API
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
