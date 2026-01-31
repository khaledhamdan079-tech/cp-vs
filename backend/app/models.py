from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, TypeDecorator, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from .database import Base


# UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            # PostgreSQL UUID type handles conversion automatically
            return value
        else:
            # SQLite: convert to string
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            # PostgreSQL returns UUID directly
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(value)
        else:
            # SQLite: convert from string
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


class ChallengeStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ContestStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"


class TournamentStatus(str, enum.Enum):
    PENDING = "pending"
    REGISTERING = "registering"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentInviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TournamentMatchStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    handle = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rating = Column(Integer, default=1000, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_confirmed = Column(Boolean, default=False, nullable=False, index=True)
    confirmation_deadline = Column(DateTime, nullable=True)

    # Relationships
    challenges_sent = relationship("Challenge", foreign_keys="Challenge.challenger_id", back_populates="challenger")
    challenges_received = relationship("Challenge", foreign_keys="Challenge.challenged_id", back_populates="challenged")
    contests_user1 = relationship("Contest", foreign_keys="Contest.user1_id", back_populates="user1")
    contests_user2 = relationship("Contest", foreign_keys="Contest.user2_id", back_populates="user2")
    rating_history = relationship("RatingHistory", back_populates="user")
    tournament_slots = relationship("TournamentSlot", back_populates="user")
    tournament_invites_sent = relationship("TournamentInvite", foreign_keys="TournamentInvite.invited_user_id", back_populates="invited_user")
    tournaments_created = relationship("Tournament", foreign_keys="Tournament.creator_id", back_populates="creator")


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    challenger_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    challenged_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-4
    suggested_start_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ChallengeStatus), default=ChallengeStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    challenger = relationship("User", foreign_keys=[challenger_id], back_populates="challenges_sent")
    challenged = relationship("User", foreign_keys=[challenged_id], back_populates="challenges_received")
    contest = relationship("Contest", back_populates="challenge", uselist=False)


class Contest(Base):
    __tablename__ = "contests"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(GUID(), ForeignKey("challenges.id"), nullable=True, unique=True)
    tournament_match_id = Column(GUID(), ForeignKey("tournament_matches.id"), nullable=True)
    user1_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    user2_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    difficulty = Column(Integer, nullable=False)  # 1-4
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(SQLEnum(ContestStatus), default=ContestStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    challenge = relationship("Challenge", back_populates="contest")
    tournament_match = relationship("TournamentMatch", back_populates="contest", foreign_keys=[tournament_match_id], uselist=False)
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="contests_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="contests_user2")
    problems = relationship("ContestProblem", back_populates="contest", cascade="all, delete-orphan")
    scores = relationship("ContestScore", back_populates="contest", cascade="all, delete-orphan")
    rating_history = relationship("RatingHistory", back_populates="contest")


class ContestProblem(Base):
    __tablename__ = "contest_problems"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    contest_id = Column(GUID(), ForeignKey("contests.id"), nullable=False)
    problem_index = Column(String, nullable=False)  # 'A', 'B', 'C', 'D', 'E', 'F'
    problem_code = Column(String, nullable=False)  # e.g., "1234A"
    problem_url = Column(String, nullable=False)
    points = Column(Integer, nullable=False)  # 100, 200, 300, 400, 500, 600
    division = Column(Integer, nullable=False)
    solved_by = Column(GUID(), ForeignKey("users.id"), nullable=True)
    solved_at = Column(DateTime, nullable=True)

    # Relationships
    contest = relationship("Contest", back_populates="problems")
    solver = relationship("User")


class ContestScore(Base):
    __tablename__ = "contest_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    contest_id = Column(GUID(), ForeignKey("contests.id"), nullable=False)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    total_points = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contest = relationship("Contest", back_populates="scores")
    user = relationship("User")


class RatingHistory(Base):
    __tablename__ = "rating_history"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    contest_id = Column(GUID(), ForeignKey("contests.id"), nullable=False)
    rating_before = Column(Integer, nullable=False)
    rating_after = Column(Integer, nullable=False)
    rating_change = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="rating_history")
    contest = relationship("Contest", back_populates="rating_history")


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    creator_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    num_participants = Column(Integer, nullable=False)  # 4, 8, 16, 32, or 64
    difficulty = Column(Integer, nullable=False)  # 1-4
    status = Column(SQLEnum(TournamentStatus), default=TournamentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_time = Column(DateTime, nullable=True)  # When all slots filled

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="tournaments_created")
    slots = relationship("TournamentSlot", back_populates="tournament", cascade="all, delete-orphan")
    invites = relationship("TournamentInvite", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("TournamentMatch", back_populates="tournament", cascade="all, delete-orphan")
    round_schedules = relationship("TournamentRoundSchedule", back_populates="tournament", cascade="all, delete-orphan")


class TournamentSlot(Base):
    __tablename__ = "tournament_slots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(GUID(), ForeignKey("tournaments.id"), nullable=False)
    slot_number = Column(Integer, nullable=False)  # 1 to num_participants
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    status = Column(String, default="PENDING")  # PENDING or ACCEPTED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tournament = relationship("Tournament", back_populates="slots")
    user = relationship("User", back_populates="tournament_slots")


class TournamentInvite(Base):
    __tablename__ = "tournament_invites"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(GUID(), ForeignKey("tournaments.id"), nullable=False)
    slot_id = Column(GUID(), ForeignKey("tournament_slots.id"), nullable=False)
    invited_user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(TournamentInviteStatus), default=TournamentInviteStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="invites")
    slot = relationship("TournamentSlot")
    invited_user = relationship("User", foreign_keys=[invited_user_id], back_populates="tournament_invites_sent")


class TournamentRoundSchedule(Base):
    __tablename__ = "tournament_round_schedules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(GUID(), ForeignKey("tournaments.id"), nullable=False)
    round_number = Column(Integer, nullable=False)  # 1, 2, 3...
    start_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tournament = relationship("Tournament", back_populates="round_schedules")


class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(GUID(), ForeignKey("tournaments.id"), nullable=False)
    round_number = Column(Integer, nullable=False)  # 1, 2, 3...
    slot1_id = Column(GUID(), ForeignKey("tournament_slots.id"), nullable=False)
    slot2_id = Column(GUID(), ForeignKey("tournament_slots.id"), nullable=False)
    user1_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    user2_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    contest_id = Column(GUID(), ForeignKey("contests.id"), nullable=True)
    winner_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(TournamentMatchStatus), default=TournamentMatchStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    slot1 = relationship("TournamentSlot", foreign_keys=[slot1_id])
    slot2 = relationship("TournamentSlot", foreign_keys=[slot2_id])
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    contest = relationship("Contest", foreign_keys=[contest_id], uselist=False)
    winner = relationship("User", foreign_keys=[winner_id])
