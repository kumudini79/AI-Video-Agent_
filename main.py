from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field,field_validator
from typing import Optional
from datetime import datetime,date
from enum import Enum
import logging
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

#configure the logging setUp
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)

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
            logger.info(f"entered error block with {v} ")
            raise ValueError("due_date cannot be in past")
        logger.info(f"dueDate is {v}")
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

@app.get("/tasks/{id}")
def get_givenTask(task_id:int):
    for task in dbTasks:
        if(task["id"]==task_id):
            logger.info(f"entered if block with {task_id}")
            return task
    logger.info(f"out of the block with {task_id}")
    raise HTTPException(status_code=400,detail=f"Task with {task_id} is not present")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    # Search for the task in the list
    for task in dbTasks:
        if task["id"] == task_id:
            logger.info(f"Deleting task with ID: {task_id}")
            dbTasks.remove(task)
            # Return a confirmation message
            return {"message": f"Task with ID {task_id} has been successfully deleted"}
            
    # If the loop finishes without finding the ID, raise a 404
    logger.warning(f"Delete failed. Task with ID {task_id} not found.")
    raise HTTPException(status_code=404, detail=f"Task with ID {task_id} is not present")




