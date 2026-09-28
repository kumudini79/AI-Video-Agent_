from fastapi import FastAPI
from pydantic import BaseModel,Field,field_validator
from typing import Optional
from datetime import datetime,date
from enum import Enum
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class priorityEnum(str,Enum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"

class statusEnum(str,Enum):
    TODO="todo"
    IN_PROGRESS="in_progress"
    DONE="done"

class taskCreate(BaseModel):
    title:str=Field(...,min_length=3,max_length=100)
    description:Optional[str]=Field(default=None,description="Description is optional")
    priority:priorityEnum=Field(default=priorityEnum.MEDIUM,description="Default is medium")
    status:statusEnum=Field(default=statusEnum.TODO,description="Default is todo")
    due_date:Optional[date]=Field(default=None,description="dueDate is optional")
@field_validator("due_date")
@classmethod
def due_date_must_be_in_future(cls,v:Optional[date])->Optional[date]:
    if v is not None and v<date.today():
        raise ValueError("due_date cannot be in past")
    return v
class taskRepsone(taskCreate):
    id:int
    created_at:datetime

    class Config:
        from_attributes=True

dbTasks=[]
task_id_counter=1

@app.post("/task",response_model=taskRepsone)
def task_Creation(task_input:taskCreate):
    global task_id_counter

    server_generated_fields={
        "id":task_id_counter,
        "created_at":datetime.now()
    }

    new_task={**task_input.model_dump(),**server_generated_fields}
    dbTasks.append(new_task)
    task_id_counter+=1
    return new_task

@app.get("/tasks")
def get_tasks():
    return dbTasks




