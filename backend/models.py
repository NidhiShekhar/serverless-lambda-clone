from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import relationship
import datetime
from .db import Base

class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    language = Column(String)
    code = Column(Text)
    timeout = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship with execution logs
    execution_logs = relationship("ExecutionLog", back_populates="function")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    function_id = Column(Integer, ForeignKey("functions.id"))
    status = Column(String)  # "success" or "failure"
    execution_time = Column(Float)
    error_log = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship with function
    function = relationship("Function", back_populates="execution_logs")