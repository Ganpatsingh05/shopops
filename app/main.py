from fastapi import FastAPI

app = FastAPI(
    title="ShopOps API",
    description="Cloud-native E-Commerce Product and Order API",
    version="0.1.0",
)


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