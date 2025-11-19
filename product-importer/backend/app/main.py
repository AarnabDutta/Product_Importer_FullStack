# FastAPI app initialization & routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import products, upload, progress, webhooks
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Product Importer API",
    description="Backend API for importing and managing products",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(upload.router)
app.include_router(progress.router)
app.include_router(webhooks.router)


@app.get("/")
def read_root():
    return {"message": "Product Importer API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
