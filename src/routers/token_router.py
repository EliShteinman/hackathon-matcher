from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from src.app.dependencies import get_db, get_token_service, get_user_service
from src.models.enums import MatchRequestStatus
from src.schemas.match_schemas import TokenActionResponse, TokenDetailsResponse
from src.services.token_service import TokenService
from src.services.user_service import UserService

router = APIRouter(prefix="/api/tokens", tags=["tokens"])


@router.get("/{uuid}/details", response_model=TokenDetailsResponse)
async def get_token_details(
    uuid: str,
    token_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(get_user_service),
):
    token, match_request = await token_service.get_token_details(uuid)
    initiator = await user_service.get_user_by_id(match_request.initiator_id)
    target = await user_service.get_user_by_id(match_request.target_id)
    return TokenDetailsResponse(
        initiator_name=initiator.full_name,
        initiator_branch=initiator.branch,
        target_name=target.full_name,
        match_id=match_request.id,
        is_expired=datetime.now(UTC) > token.expires_at,
        is_used=token.is_used,
    )


@router.post("/{uuid}/approve", response_model=TokenActionResponse)
async def approve_match(
    uuid: str,
    token_service: TokenService = Depends(get_token_service),
    db=Depends(get_db),
):
    await token_service.approve(uuid)
    await db.commit()
    return TokenActionResponse(message="השותפות אושרה בהצלחה!", status=MatchRequestStatus.APPROVED)


@router.post("/{uuid}/reject", response_model=TokenActionResponse)
async def reject_match(
    uuid: str,
    token_service: TokenService = Depends(get_token_service),
    db=Depends(get_db),
):
    await token_service.reject(uuid)
    await db.commit()
    return TokenActionResponse(message="הבקשה נדחתה.", status=MatchRequestStatus.REJECTED)
