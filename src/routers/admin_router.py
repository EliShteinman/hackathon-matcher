from fastapi import APIRouter, Depends, File, UploadFile

from src.app.dependencies import get_admin_service, get_admin_verified, get_match_repository, get_user_service
from src.models.enums import UserStatus
from src.repositories.interfaces.match_repository import MatchRepositoryInterface
from src.schemas.admin_schemas import (
    AdminUserItem,
    ExcelUploadResponse,
    MetricsResponse,
    SystemSettingsResponse,
    UpdateSettingsRequest,
)
from src.services.admin_service import AdminService
from src.services.user_service import UserService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/excel/upload", response_model=ExcelUploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    _admin: bool = Depends(get_admin_verified),
    admin_service: AdminService = Depends(get_admin_service),
):
    content = await file.read()
    count = await admin_service.upload_excel(content)
    return ExcelUploadResponse(imported_count=count, message=f"יובאו {count} משתתפים בהצלחה")


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    _admin: bool = Depends(get_admin_verified),
    user_service: UserService = Depends(get_user_service),
):
    counts = await user_service.get_metrics()
    return MetricsResponse(
        available=counts.get(UserStatus.AVAILABLE, 0),
        pending=counts.get(UserStatus.PENDING, 0),
        matched=counts.get(UserStatus.MATCHED, 0),
        total=sum(counts.values()),
    )


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    _admin: bool = Depends(get_admin_verified),
    admin_service: AdminService = Depends(get_admin_service),
):
    settings = await admin_service.get_settings()
    return SystemSettingsResponse(
        is_globally_locked=settings.is_globally_locked,
        deadline=settings.deadline,
        last_excel_upload_at=settings.last_excel_upload_at,
    )


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    body: UpdateSettingsRequest,
    _admin: bool = Depends(get_admin_verified),
    admin_service: AdminService = Depends(get_admin_service),
):
    settings = await admin_service.update_settings(
        is_globally_locked=body.is_globally_locked,
        deadline=body.deadline,
    )
    return SystemSettingsResponse(
        is_globally_locked=settings.is_globally_locked,
        deadline=settings.deadline,
        last_excel_upload_at=settings.last_excel_upload_at,
    )


@router.get("/users", response_model=list[AdminUserItem])
async def get_all_users(
    _admin: bool = Depends(get_admin_verified),
    user_service: UserService = Depends(get_user_service),
    match_repo: MatchRepositoryInterface = Depends(get_match_repository),
):
    users = await user_service.get_all_users()
    result: list[AdminUserItem] = []
    for user in users:
        partner_name = None
        match = await match_repo.get_active_by_user_id(user.id)
        if match:
            partner_id = match.target_id if match.initiator_id == user.id else match.initiator_id
            partner = await user_service.get_user_by_id(partner_id)
            if partner:
                partner_name = partner.full_name
        result.append(
            AdminUserItem(
                id=user.id,
                id_number=user.id_number,
                email=user.email,
                full_name=user.full_name,
                branch=user.branch,
                class_name=user.class_name,
                status=user.status,
                partner_name=partner_name,
            )
        )
    return result
