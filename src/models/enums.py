from enum import StrEnum


class UserStatus(StrEnum):
    AVAILABLE = "available"
    PENDING = "pending"
    MATCHED = "matched"


class MatchRequestStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
