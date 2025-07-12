from celery import Celery
from app.db import SyncSession
from sqlalchemy.future import select
from app.models import Job, JobStatus

celery = Celery("tasks", broker="redis://redis:6379/0")

@celery.task
def process_job(job_id):
    from app.models import Job, JobStatus
    import time

    with SyncSession() as session:
        job = session.query(Job).filter(Job.id == job_id).one()
        job.status = JobStatus.IN_PROGRESS
        session.commit()
        try:
            time.sleep(2)
            if job.operation == "square_sum":
                job.result = sum([x**2 for x in job.data])
                job.status = JobStatus.SUCCESS
            elif job.operation == "cube_sum":
                job.result = sum([x**3 for x in job.data])
                job.status = JobStatus.SUCCESS
            else:
                job.status = JobStatus.FAILED
            session.commit()  
        except Exception:
            job.status = JobStatus.FAILED
            session.commit()