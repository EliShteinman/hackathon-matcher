from fastapi import APIRouter, Depends

from src.app.dependencies import get_cancellation_service, get_current_user_id, get_db, get_match_service
from src.schemas.match_schemas import CreateMatchRequest, MatchResponse
from src.services.cancellation_service import CancellationService
from src.services.match_service import MatchService

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.post("", response_model=MatchResponse)
async def create_match(
    body: CreateMatchRequest,
    current_user_id: int = Depends(get_current_user_id),
    match_service: MatchService = Depends(get_match_service),
    db=Depends(get_db),
):
    match_request = await match_service.initiate_match(current_user_id, body.target_user_id)
    await db.commit()
    return MatchResponse(
        id=match_request.id,
        initiator_id=match_request.initiator_id,
        target_id=match_request.target_id,
        status=match_request.status,
        created_at=match_request.created_at,
    )


@router.delete("/{match_id}")
async def cancel_match(
    match_id: int,
    current_user_id: int = Depends(get_current_user_id),
    cancellation_service: CancellationService = Depends(get_cancellation_service),
    db=Depends(get_db),
):
    await cancellation_service.cancel_match(current_user_id, match_id)
    await db.commit()
    return {"message": "ההתאמה בוטלה בהצלחה"}
