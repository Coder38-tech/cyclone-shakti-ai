from fastapi import APIRouter

from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.services.advisory_service import AdvisoryService

router = APIRouter(prefix="", tags=["advisory"])


@router.post("/generate-alert", response_model=AdvisoryResponse)
def generate_advisory(request: AdvisoryRequest) -> AdvisoryResponse:
    service = AdvisoryService()
    return service.generate(request)


@router.get("/advisory/languages")
def list_supported_languages() -> dict:
    return {"languages": AdvisoryService.supported_languages()}
