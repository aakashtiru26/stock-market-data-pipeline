from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import PipelineLog
from pipeline.scheduler import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.get("/status")
def get_pipeline_status(db: Session = Depends(get_db)):
    latest_log = db.query(PipelineLog).order_by(PipelineLog.timestamp.desc()).first()
    if not latest_log:
        return {"status": "No pipeline runs recorded."}
    return latest_log

@router.post("/trigger")
def trigger_pipeline(background_tasks: BackgroundTasks, is_historical: bool = False):
    """
    Manually trigger the pipeline.
    """
    background_tasks.add_task(run_pipeline, is_historical)
    return {"message": f"Pipeline triggered in background. Historical: {is_historical}"}
