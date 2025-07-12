from app.models import Job, JobStatus
from app.db import SyncSession
from app.tasks import process_job
import uuid
import pytest

def clear_jobs():
    with SyncSession() as session:
        session.query(Job).delete()
        session.commit()

@pytest.fixture(autouse=True)
def run_around_tests():
    clear_jobs()
    yield
    clear_jobs()

def test_process_job_square_sum():
    with SyncSession() as session:
        job = Job(id=uuid.uuid4(), data=[2, 3], operation="square_sum", status=JobStatus.PENDING)
        session.add(job)
        session.commit()
        job_id = job.id
    process_job(str(job_id))
    with SyncSession() as session:
        job = session.query(Job).filter(Job.id == job_id).one()
        assert job.status == JobStatus.SUCCESS
        assert job.result == 13

def test_process_job_cube_sum():
    with SyncSession() as session:
        job = Job(id=uuid.uuid4(), data=[2, 3], operation="cube_sum", status=JobStatus.PENDING)
        session.add(job)
        session.commit()
        job_id = job.id
    process_job(str(job_id))
    with SyncSession() as session:
        job = session.query(Job).filter(Job.id == job_id).one()
        assert job.status == JobStatus.SUCCESS
        assert job.result == 35  # 2^3 + 3^3 = 8 + 27 = 35

def test_process_job_invalid_op():
    with SyncSession() as session:
        job = Job(id=uuid.uuid4(), data=[2, 3], operation="invalid", status=JobStatus.PENDING)
        session.add(job)
        session.commit()
        job_id = job.id
    process_job(str(job_id))
    with SyncSession() as session:
        job = session.query(Job).filter(Job.id == job_id).one()
        assert job.status == JobStatus.FAILED
        assert job.result is None

def test_process_job_exception():
    with SyncSession() as session:
        job = Job(id=uuid.uuid4(), data=None, operation="square_sum", status=JobStatus.PENDING)
        session.add(job)
        session.commit()
        job_id = job.id
    process_job(str(job_id))
    with SyncSession() as session:
        job = session.query(Job).filter(Job.id == job_id).one()
        assert job.status == JobStatus.FAILED
        assert job.result is None
