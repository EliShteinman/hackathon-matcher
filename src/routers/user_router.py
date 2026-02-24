from fastapi import APIRouter, Depends

from src.app.dependencies import get_current_user_id, get_match_repository, get_user_service
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.schemas.user_schemas import AvailableUserItem, MatchInfoResponse, UserMeResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/available", response_model=list[AvailableUserItem])
async def get_available_users(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
):
    users = await user_service.get_available_users(current_user_id)
    return [
        AvailableUserItem(
            id=u.id,
            full_name=u.full_name,
            branch=u.branch,
            display=f"{u.full_name} - {u.branch}",
        )
        for u in users
    ]


@router.get("/me", response_model=UserMeResponse)
async def get_me(
    current_user_id: int = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service),
    match_repo: MatchRepositoryInterface = Depends(get_match_repository),
):
    user = await user_service.get_user_by_id(current_user_id)
    match_info = None

    active_match = await match_repo.get_active_by_user_id(current_user_id)
    if active_match:
        is_initiator = active_match.initiator_id == current_user_id
        partner_id = active_match.target_id if is_initiator else active_match.initiator_id
        partner = await user_service.get_user_by_id(partner_id)
        match_info = MatchInfoResponse(
            match_id=active_match.id,
            partner_name=partner.full_name,
            partner_branch=partner.branch,
            partner_email=partner.email if active_match.status.value == "approved" else None,
            partner_class_name=partner.class_name if active_match.status.value == "approved" else None,
            is_initiator=is_initiator,
            status=active_match.status.value,
        )

    return UserMeResponse(
        id=user.id,
        full_name=user.full_name,
        branch=user.branch,
        email=user.email,
        class_name=user.class_name,
        status=user.status,
        match_info=match_info,
    )
