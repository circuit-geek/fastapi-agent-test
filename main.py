from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    completed: bool = False

tasks = []

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    """
    Use this api to retrieve all the existing tasks that are there
    to be completed as mentioned
    :return: List of all the tasks in the list
    """
    return tasks

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    """
    Use this api to create a new task based on the user's description
    to create a new task
    :param task: {id: int, title: str, description: str, completed: bool}
    :return: task
    """
    tasks.append(task)
    return task