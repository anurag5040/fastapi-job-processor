from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from app.models import JobStatus

class JobCreate(BaseModel):
    data: List[int]
    operation: str

class JobResponse(BaseModel):
    job_id: UUID
    status: JobStatus

class JobStatusResponse(BaseModel):
    status: JobStatus

class JobResultResponse(BaseModel):
    result: Optional[int]
    status: JobStatus

class JobFullResponse(BaseModel):
    job_id: UUID
    data: list[int]
    operation: str
    status: JobStatus
    result: Optional[int]

class JobListResponse(BaseModel):
    jobs: list[JobFullResponse]

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
