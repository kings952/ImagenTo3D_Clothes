import pytest
from backend.jobs.manager import JobManager, JobStatus


def test_job_lifecycle():
    manager = JobManager()
    job = manager.create({"reference": "shirt.png"}, {"mode": "oversize"})
    assert job.status is JobStatus.PENDING
    manager.transition(job.id, JobStatus.PROCESSING)
    manager.transition(job.id, JobStatus.COMPLETED)
    assert manager.get(job.id).status is JobStatus.COMPLETED


def test_invalid_transition_is_rejected():
    manager = JobManager()
    job = manager.create({}, {})
    with pytest.raises(ValueError):
        manager.transition(job.id, JobStatus.COMPLETED)


def test_terminal_job_cannot_restart():
    manager = JobManager()
    job = manager.create({}, {})
    manager.transition(job.id, JobStatus.CANCELLED)
    with pytest.raises(ValueError):
        manager.transition(job.id, JobStatus.PROCESSING)
