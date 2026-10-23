"""Ciclo de vida básico de trabajos."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from uuid import uuid4


class JobStatus(str, Enum):
    PENDING = "pendiente"
    PROCESSING = "procesando"
    COMPLETED = "completado"
    CANCELLED = "cancelado"
    FAILED = "fallido"


_ALLOWED = {
    JobStatus.PENDING: {JobStatus.PROCESSING, JobStatus.CANCELLED, JobStatus.FAILED},
    JobStatus.PROCESSING: {JobStatus.COMPLETED, JobStatus.CANCELLED, JobStatus.FAILED},
    JobStatus.COMPLETED: set(), JobStatus.CANCELLED: set(), JobStatus.FAILED: set(),
}


@dataclass
class Job:
    id: str = field(default_factory=lambda: uuid4().hex)
    status: JobStatus = JobStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    inputs: dict = field(default_factory=dict)
    parameters: dict = field(default_factory=dict)
    outputs: list = field(default_factory=list)
    error: str | None = None


class JobManager:
    def __init__(self):
        self._jobs = {}
        self._lock = RLock()

    def create(self, inputs, parameters):
        with self._lock:
            job = Job(inputs=dict(inputs), parameters=dict(parameters))
            self._jobs[job.id] = job
            return job

    def get(self, job_id):
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(f"No existe el trabajo {job_id}.")
            return self._jobs[job_id]

    def transition(self, job_id, status, error=None):
        with self._lock:
            job = self.get(job_id)
            if status not in _ALLOWED[job.status]:
                raise ValueError(f"Transición no permitida: {job.status.value} -> {status.value}.")
            job.status = status
            job.updated_at = datetime.now(timezone.utc).isoformat()
            job.error = error
            return job
