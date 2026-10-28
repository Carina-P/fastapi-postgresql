from fastapi import FastAPI
from app.routers import customers, products, orders

app = FastAPI()

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(customers.router)


@app.get("/health")
def health():
    return {"status": "ok"}
