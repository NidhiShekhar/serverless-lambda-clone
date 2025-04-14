from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import crud, schemas
from backend.db import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Function, status_code=status.HTTP_201_CREATED)
def create_function(function: schemas.FunctionCreate, db: Session = Depends(get_db)):
    """Create a new serverless function"""
    return crud.create_function(db=db, function=function)


@router.get("/", response_model=List[schemas.Function])
def read_functions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all serverless functions"""
    functions = crud.get_all_functions(db, skip=skip, limit=limit)
    return functions


@router.get("/{function_id}", response_model=schemas.Function)
def read_function(function_id: int, db: Session = Depends(get_db)):
    """Get a specific serverless function by ID"""
    db_function = crud.get_function(db, id=function_id)
    if db_function is None:
        raise HTTPException(status_code=404, detail="Function not found")
    return db_function


@router.delete("/{function_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_function(function_id: int, db: Session = Depends(get_db)):
    """Delete a serverless function"""
    success = crud.delete_function(db, id=function_id)
    if not success:
        raise HTTPException(status_code=404, detail="Function not found")
    return None


@router.get("/{function_id}/logs", response_model=List[schemas.ExecutionLog])
def read_function_logs(function_id: int, db: Session = Depends(get_db)):
    """Get all execution logs for a specific function"""
    # First verify the function exists
    db_function = crud.get_function(db, id=function_id)
    if db_function is None:
        raise HTTPException(status_code=404, detail="Function not found")

    # Get the logs
    logs = crud.get_logs_for_function(db, function_id=function_id)
    return logs