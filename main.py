from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = MetaData()

todos = Table(
    "todos",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("completed", Boolean),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/todos", response_model=List[TodoItem])
async def get_todos():
    query = todos.select()
    return await database.fetch_all(query)

@app.post("/todos", response_model=TodoItem)
async def create_todo(todo: TodoItem):
    query = todos.insert().values(id=todo.id, title=todo.title, completed=todo.completed)
    await database.execute(query)
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: int, updated_todo: TodoItem):
    query = todos.update().where(todos.c.id == todo_id).values(title=updated_todo.title, completed=updated_todo.completed)
    await database.execute(query)
    return updated_todo

@app.delete("/todos/{todo_id}", response_model=TodoItem)
async def delete_todo(todo_id: int):
    query = todos.delete().where(todos.c.id == todo_id)
    await database.execute(query)
    return {"id": todo_id, "title": "", "completed": False}
