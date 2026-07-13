from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from models import Product
from database import session, engine
import database_models

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database_models.Base.metadata.create_all(bind=engine)

products = [
    Product(id=1, name="Product 1", description="Description 1", price=10.0, quantity=5),
    Product(id=2, name="Product 2", description="Description 2", price=20.0, quantity=3),
    Product(id=3, name="Product 3", description="Description 3", price=15.0, quantity=8),
    Product(id=4, name="Product 4", description="Description 4", price=12.0, quantity=6),
    Product(id=5, name="Product 5", description="Description 5", price=18.0, quantity=4),
    Product(id=6, name="Product 6", description="Description 6", price=25.0, quantity=2),
]


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    db = session()
    try:
        count = db.query(database_models.Product).count()
        if count == 0:
            for product in products:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()


init_db()


def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "quantity": product.quantity,
    }


@app.get("/")
def greet():
    return "welcome to tulusko"


@app.get("/products")
@app.get("/products/")
def get_all_product(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Product).all()
    return [serialize_product(product) for product in db_products]


@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return serialize_product(db_product)
    return {"detail": "Product not found"}


@app.post("/products")
@app.post("/products/")
def add_product(product: Product, db: Session = Depends(get_db)):
    db_product = database_models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return serialize_product(db_product)


@app.put("/products/{id}")
def update_product(id: int, updated_product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = updated_product.name
        db_product.description = updated_product.description
        db_product.price = updated_product.price
        db_product.quantity = updated_product.quantity
        db.commit()
        db.refresh(db_product)
        return serialize_product(db_product)
    return {"detail": "Product not found"}


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return {"detail": "Product deleted"}
    return {"detail": "Product not found"}