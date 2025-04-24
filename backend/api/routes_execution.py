from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend import crud, models
from backend.engine.executor import execute_function_engine

router = APIRouter()

@router.post("/functions/{id}/execute", tags=["execution"])
async def execute_function(id: int, db: Session = Depends(get_db)):
    
    # Fetching the function by ID
    function = crud.get_function(db, id=id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")

    # Passing the function to the execution engine in docka-wocka
    try:
        result = execute_function_engine(function) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

    # Logging the result in the ExecutionLogs table
    crud.log_execution_result(db, function_id=id, result=result)

    return {"status": "success", "result": result}

@router.get("/functions/{id}/logs", tags=["execution"])
async def get_function_logs(id: int, db: Session = Depends(get_db)):
    # Fetching logs for the function
    logs = crud.get_logs_for_function(db, function_id=id)
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")

    return {"status": "success", "logs": logs}
