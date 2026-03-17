from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api import category_router
from app.api import user_router
from app.api import product_router

app = FastAPI(title="WishList Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers
app.include_router(category_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)

@app.get("/")
def root(): 
    return {"message" : "Wi$h Li$t backend running"}