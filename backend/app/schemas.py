from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional, List
from datetime import datetime, timezone
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    handle: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "handle": "tourist"
            }
        }


class UserCreate(UserBase):
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "handle": "tourist",
                "password": "securepassword123"
            }
        }


class UserResponse(UserBase):
    id: UUID
    rating: int
    created_at: datetime
    is_confirmed: bool

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format with timezone"""
        if dt is None:
            return None
        # If datetime is naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


class RegistrationResponse(UserResponse):
    """Response for registration including confirmation details"""
    problem_link: str
    deadline: Optional[datetime] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

    @field_serializer('deadline')
    def serialize_deadline(self, dt: Optional[datetime], _info):
        """Serialize deadline to ISO format with timezone"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


class ConfirmationStatusResponse(BaseModel):
    """Response for confirmation status check"""
    is_confirmed: bool
    deadline: Optional[datetime] = None
    time_remaining: Optional[int] = None  # seconds remaining
    problem_link: str

    @field_serializer('deadline')
    def serialize_deadline(self, dt: Optional[datetime], _info):
        """Serialize deadline to ISO format with timezone"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Challenge schemas
class ChallengeBase(BaseModel):
    difficulty: int
    suggested_start_time: datetime


class ChallengeCreate(ChallengeBase):
    challenged_user_id: Optional[UUID] = None
    challenged_handle: Optional[str] = None


class ChallengeResponse(ChallengeBase):
    id: UUID
    challenger_id: UUID
    challenged_id: UUID
    status: str
    created_at: datetime
    challenger: UserResponse
    challenged: UserResponse

    @field_serializer('suggested_start_time', 'created_at')
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format with timezone"""
        if dt is None:
            return None
        # If datetime is naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


# Contest schemas
class ContestProblemResponse(BaseModel):
    id: UUID
    problem_index: str
    problem_code: str
    problem_url: Optional[str] = None
    points: int
    solved_by: Optional[UUID] = None
    solved_at: Optional[datetime] = None

    @field_serializer('solved_at')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        """Serialize datetime to ISO format with timezone"""
        if dt is None:
            return None
        # If datetime is naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        return cls.model_validate(obj)


class ContestScoreResponse(BaseModel):
    user_id: UUID
    user_handle: str
    total_points: int


class ContestResponse(BaseModel):
    id: UUID
    user1_id: UUID
    user2_id: UUID
    user1_handle: str
    user2_handle: str
    difficulty: int
    start_time: datetime
    end_time: datetime
    status: str
    problems: List[ContestProblemResponse] = []
    scores: List[ContestScoreResponse] = []

    @field_serializer('start_time', 'end_time')
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format with timezone"""
        if dt is None:
            return None
        # If datetime is naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


# User search schema
class UserSearchResponse(BaseModel):
    id: UUID
    handle: str
    rating: int

    class Config:
        from_attributes = True


# Leaderboard schema
class LeaderboardEntryResponse(BaseModel):
    rank: int
    handle: str
    rating: int
    id: UUID

    class Config:
        from_attributes = True


# User profile schema
class UserProfileResponse(BaseModel):
    id: UUID
    handle: str
    rating: int
    created_at: datetime
    total_contests: int
    wins: int
    losses: int
    draws: int
    win_rate: float

    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime, _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


# Public contest schema (without sensitive data)
class PublicContestResponse(BaseModel):
    id: UUID
    user1_handle: str
    user2_handle: str
    difficulty: int
    start_time: datetime
    end_time: datetime
    status: str
    user1_points: int
    user2_points: int
    user1_rating_change: Optional[int] = None
    user2_rating_change: Optional[int] = None

    @field_serializer('start_time', 'end_time')
    def serialize_datetime(self, dt: datetime, _info):
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True
