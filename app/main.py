from fastapi import FastAPI

from app.api.product import router as products_router

app = FastAPI(
    title="ShopOps API",
    description="Cloud-native E-Commerce Product and Order API",
    version="0.1.0",
)

app.include_router(products_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to ShopOps API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "shopops-api",
    }