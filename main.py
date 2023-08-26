""" Необходимо создать базу данных для интернет-магазина. База данных должна состоять из трёх таблиц: товары, заказы и пользователи.
— Таблица «Товары» должна содержать информацию о доступных товарах, их описаниях и ценах.
— Таблица «Заказы» должна содержать информацию о заказах, сделанных пользователями.
— Таблица «Пользователи» должна содержать информацию о зарегистрированных пользователях магазина.
• Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY), имя, фамилия, адрес электронной почты и пароль.
• Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
• Таблица товаров должна содержать следующие поля: id (PRIMARY KEY), название, описание и цена.

Создайте модели pydantic для получения новых данных и возврата существующих в БД для каждой из трёх таблиц.
Реализуйте CRUD операции для каждой из таблиц через создание маршрутов, REST API. """

from fastapi import FastAPI
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, ForeignKey, MetaData
from sqlalchemy.future import select
from databases import Database
from typing import List
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)

metadata = MetaData()

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("email", String, unique=True),
    Column("password", String),
)

products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("description", String),
    Column("price", Float),
)

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("product_id", Integer, ForeignKey("products.id")),
    Column("order_date", String),
    Column("status", String),
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

metadata.create_all(engine)

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    order_date: str
    status: str

class ProductResponse(ProductCreate):
    id: int

class UserResponse(UserCreate):
    id: int

class OrderResponse(OrderCreate):
    id: int

@app.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    query = products.insert().values(**product.model_dump())
    product_id = await database.execute(query)
    return {**product.model_dump(), "id": product_id}

@app.get("/products/", response_model=List[ProductResponse])
async def get_products():
    query = products.select()
    return await database.fetch_all(query)

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    query = users.insert().values(**user.model_dump())
    user_id = await database.execute(query)
    return {**user.model_dump(), "id": user_id}

@app.get("/users/", response_model=List[UserResponse])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate):
    query = orders.insert().values(**order.model_dump())
    order_id = await database.execute(query)
    return {**order.model_dump(), "id": order_id}

@app.get("/orders/", response_model=List[OrderResponse])
async def get_orders():
    query = orders.select()
    return await database.fetch_all(query)

@app.get("/products/{product_id}", response_model=ProductResponse)  
async def get_product(product_id: int):
    query = products.select().where(products.c.id == product_id)
    return await database.fetch_one(query)

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate):
    query = products.update().where(products.c.id == product_id).values(**product.model_dump())
    await database.execute(query)
    return {**product.model_dump(), "id": product_id} 

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    query = products.delete().where(products.c.id == product_id)
    await database.execute(query)
    return {"message": "Товар удален"}

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)

@app.put("/users/{user_id}", response_model=UserResponse)  
async def update_user(user_id: int, user: UserCreate):
    query = users.update().where(users.c.id == user_id).values(**user.model_dump())
    await database.execute(query)
    return {**user.model_dump(), "id": user_id}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {"message": "Пользователь удален"}


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)  

@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order: OrderCreate):
    query = orders.update().where(orders.c.id == order_id).values(**order.model_dump())
    await database.execute(query)
    return {**order.model_dump(), "id": order_id}

@app.delete("/orders/{order_id}")  
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {"message": "Заказ удален"}

@app.post("/populate_data/")
async def populate_data():

    # Заполняем таблицу users
    for i in range(1, 11):
        user = {
            "first_name": f"Имя{i}",
            "last_name": f"Фамилия{i}",
            "email": f"user{i}@example.com",
            "password": f"password{i}"
        }
        query = users.insert().values(**user)
        await database.execute(query)
    
    # Заполняем таблицу products
    for i in range(1, 6):
        product = {
            "name": f"Товар{i}",
            "description": f"Название Товара {i}",
            "price": i * 100.0
        }
        query = products.insert().values(**product)
        await database.execute(query)
    
    # Произвольно заполняем таблицу orders
    for i in range(1, 11):
        order = {
            "user_id": i % 10 + 1,
            "product_id": (i % 5) + 1,
            "order_date": "2023-08-26",
            "status": "в работе"
        }
        query = orders.insert().values(**order)
        await database.execute(query)
    
    return {"message": "Данные заполнены"}