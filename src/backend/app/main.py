from fastapi import FastAPI, HTTPException
from app.api import category_router
from app.api import user_router
from app.api import product_router

app = FastAPI(title="WishList Backend")

#include routers
app.include_router(category_router.router)
app.include_router(user_router.router)
app.include_router(product_router.router)

@app.get("/")
def root(): 
    return {"message" : "Wi$h Li$t backend running"}