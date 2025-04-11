from sqlalchemy.orm import Session
import time
from . import models, schemas


# Function CRUD operations
def create_function(db: Session, function: schemas.FunctionCreate):
    db_function = models.Function(**function.dict())
    db.add(db_function)
    db.commit()
    db.refresh(db_function)
    return db_function


def get_function(db: Session, id: int):
    return db.query(models.Function).filter(models.Function.id == id).first()


def get_all_functions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Function).offset(skip).limit(limit).all()


def delete_function(db: Session, id: int):
    db_function = get_function(db, id)
    if db_function:
        db.delete(db_function)
        db.commit()
        return True
    return False


# Execution Logs CRUD operations
def create_execution_log(db: Session, log: schemas.ExecutionLogCreate):
    db_log = models.ExecutionLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs_for_function(db: Session, function_id: int):
    return db.query(models.ExecutionLog).filter(
        models.ExecutionLog.function_id == function_id
    ).all()


def log_execution_result(db: Session, function_id: int, result: dict):
    # Extract data from result
    status = "success" if "output" in result else "failure"
    error_log = result.get("error", None)

    # Create the log entry using the ExecutionLogCreate schema
    log_data = {
        "function_id": function_id,
        "status": status,
        "execution_time": time.time(),  # You might want to pass actual execution time
        "error_log": error_log if error_log else None,
        "output": result.get("output", None)
    }

    log_entry = schemas.ExecutionLogCreate(**log_data)
    return create_execution_log(db, log_entry)