import logging
import os
from contextlib import asynccontextmanager

import redis
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .db import Base, engine, get_db
from .models import Task
from .schemas import TaskCreate, TaskRead

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("platform-api")

def configure_tracing():
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    provider = TracerProvider(resource=Resource.create({"service.name": "platform-api"}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(provider)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

configure_tracing()
app = FastAPI(title="Cloud-Native Platform API", version="1.0.0", lifespan=lifespan)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
FastAPIInstrumentor.instrument_app(app)

def get_cache():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1)

@app.get("/health")
def health():
    return {"status": "ok", "service": "platform-api"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as exc:
        logger.exception("Database readiness check failed")
        raise HTTPException(status_code=503, detail="database unavailable") from exc
    return {"status": "ready"}

@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.id.desc()).limit(100).all()

@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(title=payload.title, description=payload.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    try:
        get_cache().delete("tasks:list")
    except Exception:
        logger.warning("Redis cache unavailable; continuing without cache")
    logger.info("task_created task_id=%s", task.id)
    return task

@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    db.delete(task)
    db.commit()
    try:
        get_cache().delete("tasks:list")
    except Exception:
        logger.warning("Redis cache unavailable; continuing without cache")
    return None
