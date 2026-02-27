from fastapi import APIRouter
from app.api.v1 import themes, stocks, rankings, rankings_test, indices

api_router = APIRouter()

# Theme API
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])

# Stock API
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])

# Rankings API
api_router.include_router(rankings.router, prefix="/rankings", tags=["rankings"])

# Index API
api_router.include_router(indices.router, prefix="/indices", tags=["indices"])

# Test Rankings API
api_router.include_router(rankings_test.router, prefix="/rankings", tags=["rankings-test"])
