from sqlalchemy import Column, Integer, String, JSON, Enum as PgEnum
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
import enum
from app.db import Base

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    data = Column(JSON, nullable=False)
    operation = Column(String, nullable=False)
    status = Column(PgEnum(JobStatus), default=JobStatus.PENDING)
    result = Column(Integer, nullable=True)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)