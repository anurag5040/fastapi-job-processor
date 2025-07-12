from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from app.db import get_session
from app.models import Job, JobStatus, User
from app.api.schemas import JobCreate, JobResponse, JobStatusResponse, JobResultResponse, JobListResponse, JobFullResponse
from app.tasks import process_job
from app.api.deps import get_current_user  

router = APIRouter()

@router.post("/jobs/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)  
):
    if job.operation not in ("square_sum", "cube_sum"):
        raise HTTPException(status_code=400, detail="Unsupported operation. Supported operations: square_sum, cube_sum")
    new_job = Job(data=job.data, operation=job.operation)
    session.add(new_job)
    await session.commit()
    await session.refresh(new_job)
    process_job.delay(str(new_job.id))
    return JobResponse(job_id=new_job.id, status=new_job.status)

@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)  
):
    job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(status=job.status)

@router.get("/jobs/{job_id}/result", response_model=JobResultResponse)
async def get_job_result(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)  
):
    job = (await session.execute(select(Job).where(Job.id == job_id))).scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResultResponse(result=job.result, status=job.status)

@router.get("/jobsList/", response_model=JobListResponse)
async def list_jobs(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)  
):
    result = await session.execute(select(Job))
    jobs = result.scalars().all()
    return JobListResponse(jobs=[
        JobFullResponse(
            job_id=job.id,
            data=job.data,
            operation=job.operation,
            status=job.status,
            result=job.result
        ) for job in jobs
    ])
