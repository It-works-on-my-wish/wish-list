from contextlib import asynccontextmanager

from app.api import category_router, product_router, user_router
from app.scheduler.scheduler import start_scheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="WishList Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)


@app.get("/")
def root():
    return {"message": "Wi$h Li$t backend running"}
