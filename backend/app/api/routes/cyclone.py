from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db_session
from app.models.schemas import CurrentCyclone
from app.services.cyclone_service import CycloneService

router = APIRouter(prefix="/cyclone", tags=["cyclone"])


@router.get("/current", response_model=CurrentCyclone)
def get_current_cyclone(db: Session = Depends(get_db_session)) -> CurrentCyclone:
    service = CycloneService(db_session=db)
    return service.get_current_cyclone()
