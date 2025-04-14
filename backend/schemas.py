from pydantic import BaseModel
from typing import Optional, Any
import datetime


# Function schemas
class FunctionBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: str
    language: str
    timeout: int = 30  # Default timeout of 30 seconds


class FunctionCreate(FunctionBase):
    pass


class Function(FunctionBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True


# Execution log schemas
class ExecutionLogBase(BaseModel):
    function_id: int
    status: str  # "success" or "failure"
    execution_time: float
    error_log: Optional[str] = None
    output: Optional[str] = None


class ExecutionLogCreate(ExecutionLogBase):
    pass


class ExecutionLog(ExecutionLogBase):
    id: int
    created_at: datetime.datetime = datetime.datetime.now()

    class Config:
        orm_mode = True