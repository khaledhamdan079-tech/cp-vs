from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
import math
from ..database import get_db
from ..models import (
    User, Tournament, TournamentSlot, TournamentInvite, TournamentMatch,
    TournamentRoundSchedule, Contest, ContestStatus, TournamentStatus,
    TournamentInviteStatus, TournamentMatchStatus
)
from ..schemas import (
    TournamentCreate, TournamentResponse, TournamentSlotResponse,
    TournamentInviteCreate, TournamentInviteResponse, TournamentMatchResponse,
    TournamentRoundScheduleUpdate, TournamentRoundScheduleResponse,
    TournamentBracketResponse
)
from ..dependencies import get_confirmed_user

router = APIRouter(prefix="/api/tournaments", tags=["tournaments"])


def calculate_num_rounds(num_participants: int) -> int:
    """Calculate number of rounds needed for tournament"""
    return int(math.log2(num_participants))


def check_overlapping_contests(user_id, round_schedules: List[TournamentRoundSchedule], db: Session) -> Optional[str]:
    """Check if user has overlapping contests with tournament rounds. Returns error message if overlap found."""
    from uuid import UUID
    # Convert user_id to UUID if it's a string
    if isinstance(user_id, str):
        try:
            user_id = UUID(user_id)
        except ValueError:
            pass  # Keep as string if conversion fails
    
    for schedule in round_schedules:
        round_start = schedule.start_time
        round_end = round_start + timedelta(hours=2)
        
        # Check for overlapping contests (exclude tournament matches)
        # Overlap condition: (contest_start < round_end) AND (contest_end > round_start)
        # This catches overlaps including exact time matches
        overlapping = db.query(Contest).filter(
            Contest.tournament_match_id.is_(None),  # Only non-tournament contests
            Contest.status.in_([ContestStatus.SCHEDULED, ContestStatus.ACTIVE]),
            or_(
                Contest.user1_id == user_id,
                Contest.user2_id == user_id
            ),
            Contest.start_time <= round_end,  # <= to include exact matches
            Contest.end_time >= round_start   # >= to include exact matches
        ).first()
        
        if overlapping:
            return f"User has a conflicting contest scheduled for round {schedule.round_number} ({round_start} - {round_end})"
    
    return None


@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament_data: TournamentCreate,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Create a new tournament"""
    # Validate num_participants
    if tournament_data.num_participants not in [4, 8, 16, 32, 64]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of participants must be 4, 8, 16, 32, or 64"
        )
    
    # Validate difficulty
    if tournament_data.difficulty not in [1, 2, 3, 4]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Difficulty must be between 1 and 4"
        )
    
    # Create tournament
    tournament = Tournament(
        creator_id=current_user.id,
        num_participants=tournament_data.num_participants,
        difficulty=tournament_data.difficulty,
        status=TournamentStatus.PENDING
    )
    db.add(tournament)
    db.commit()
    db.refresh(tournament)
    
    # Create empty slots
    for i in range(1, tournament_data.num_participants + 1):
        slot = TournamentSlot(
            tournament_id=tournament.id,
            slot_number=i,
            status="PENDING"
        )
        db.add(slot)
    
    db.commit()
    db.refresh(tournament)
    
    # Load relationships
    slots = db.query(TournamentSlot).filter(TournamentSlot.tournament_id == tournament.id).all()
    
    return TournamentResponse(
        id=tournament.id,
        creator_id=tournament.creator_id,
        creator_handle=current_user.handle,
        num_participants=tournament.num_participants,
        difficulty=tournament.difficulty,
        status=tournament.status.value,
        created_at=tournament.created_at,
        start_time=tournament.start_time,
        slots=[TournamentSlotResponse(
            id=slot.id,
            slot_number=slot.slot_number,
            user_id=slot.user_id,
            user_handle=None,
            status=slot.status
        ) for slot in slots],
        invites=[],
        matches=[],
        round_schedules=[]
    )


@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """List tournaments where user is creator or participant"""
    # Get tournaments where user is creator
    created_tournaments = db.query(Tournament).filter(
        Tournament.creator_id == current_user.id
    ).all()
    
    # Get tournaments where user is a participant
    participant_slots = db.query(TournamentSlot).filter(
        TournamentSlot.user_id == current_user.id
    ).all()
    participant_tournament_ids = [slot.tournament_id for slot in participant_slots]
    participant_tournaments = db.query(Tournament).filter(
        Tournament.id.in_(participant_tournament_ids)
    ).all()
    
    # Combine and deduplicate
    all_tournaments = {t.id: t for t in created_tournaments + participant_tournaments}.values()
    
    result = []
    for tournament in all_tournaments:
        creator = db.query(User).filter(User.id == tournament.creator_id).first()
        slots = db.query(TournamentSlot).filter(TournamentSlot.tournament_id == tournament.id).all()
        invites = db.query(TournamentInvite).filter(TournamentInvite.tournament_id == tournament.id).all()
        matches = db.query(TournamentMatch).filter(TournamentMatch.tournament_id == tournament.id).all()
        round_schedules = db.query(TournamentRoundSchedule).filter(
            TournamentRoundSchedule.tournament_id == tournament.id
        ).order_by(TournamentRoundSchedule.round_number).all()
        
        # Build slot responses
        slot_responses = []
        for slot in slots:
            user_handle = None
            if slot.user_id:
                user = db.query(User).filter(User.id == slot.user_id).first()
                user_handle = user.handle if user else None
            slot_responses.append(TournamentSlotResponse(
                id=slot.id,
                slot_number=slot.slot_number,
                user_id=slot.user_id,
                user_handle=user_handle,
                status=slot.status
            ))
        
        # Build invite responses
        invite_responses = []
        for invite in invites:
            invited_user = db.query(User).filter(User.id == invite.invited_user_id).first()
            slot = db.query(TournamentSlot).filter(TournamentSlot.id == invite.slot_id).first()
            invite_responses.append(TournamentInviteResponse(
                id=invite.id,
                tournament_id=invite.tournament_id,
                slot_id=invite.slot_id,
                slot_number=slot.slot_number if slot else 0,
                invited_user_id=invite.invited_user_id,
                invited_user_handle=invited_user.handle if invited_user else "Unknown",
                status=invite.status.value,
                created_at=invite.created_at,
                responded_at=invite.responded_at
            ))
        
        # Build match responses
        match_responses = []
        for match in matches:
            user1 = db.query(User).filter(User.id == match.user1_id).first()
            user2 = db.query(User).filter(User.id == match.user2_id).first()
            winner = db.query(User).filter(User.id == match.winner_id).first() if match.winner_id else None
            match_responses.append(TournamentMatchResponse(
                id=match.id,
                round_number=match.round_number,
                slot1_id=match.slot1_id,
                slot2_id=match.slot2_id,
                user1_id=match.user1_id,
                user2_id=match.user2_id,
                user1_handle=user1.handle if user1 else "Unknown",
                user2_handle=user2.handle if user2 else "Unknown",
                contest_id=match.contest_id,
                winner_id=match.winner_id,
                winner_handle=winner.handle if winner else None,
                status=match.status.value,
                start_time=match.start_time,
                end_time=match.end_time
            ))
        
        # Build round schedule responses
        round_schedule_responses = [
            TournamentRoundScheduleResponse(
                id=rs.id,
                round_number=rs.round_number,
                start_time=rs.start_time
            ) for rs in round_schedules
        ]
        
        result.append(TournamentResponse(
            id=tournament.id,
            creator_id=tournament.creator_id,
            creator_handle=creator.handle if creator else "Unknown",
            num_participants=tournament.num_participants,
            difficulty=tournament.difficulty,
            status=tournament.status.value,
            created_at=tournament.created_at,
            start_time=tournament.start_time,
            slots=slot_responses,
            invites=invite_responses,
            matches=match_responses,
            round_schedules=round_schedule_responses
        ))
    
    return result


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Get tournament details"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Check if user is creator or participant
    is_creator = tournament.creator_id == current_user.id
    is_participant = db.query(TournamentSlot).filter(
        TournamentSlot.tournament_id == tournament.id,
        TournamentSlot.user_id == current_user.id
    ).first() is not None
    
    if not (is_creator or is_participant):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this tournament"
        )
    
    creator = db.query(User).filter(User.id == tournament.creator_id).first()
    slots = db.query(TournamentSlot).filter(TournamentSlot.tournament_id == tournament.id).all()
    invites = db.query(TournamentInvite).filter(TournamentInvite.tournament_id == tournament.id).all()
    matches = db.query(TournamentMatch).filter(TournamentMatch.tournament_id == tournament.id).all()
    round_schedules = db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id
    ).order_by(TournamentRoundSchedule.round_number).all()
    
    # Build responses (same as list_tournaments)
    slot_responses = []
    for slot in slots:
        user_handle = None
        if slot.user_id:
            user = db.query(User).filter(User.id == slot.user_id).first()
            user_handle = user.handle if user else None
        slot_responses.append(TournamentSlotResponse(
            id=slot.id,
            slot_number=slot.slot_number,
            user_id=slot.user_id,
            user_handle=user_handle,
            status=slot.status
        ))
    
    invite_responses = []
    for invite in invites:
        invited_user = db.query(User).filter(User.id == invite.invited_user_id).first()
        slot = db.query(TournamentSlot).filter(TournamentSlot.id == invite.slot_id).first()
        invite_responses.append(TournamentInviteResponse(
            id=invite.id,
            tournament_id=invite.tournament_id,
            slot_id=invite.slot_id,
            slot_number=slot.slot_number if slot else 0,
            invited_user_id=invite.invited_user_id,
            invited_user_handle=invited_user.handle if invited_user else "Unknown",
            status=invite.status.value,
            created_at=invite.created_at,
            responded_at=invite.responded_at
        ))
    
    match_responses = []
    for match in matches:
        user1 = db.query(User).filter(User.id == match.user1_id).first()
        user2 = db.query(User).filter(User.id == match.user2_id).first()
        winner = db.query(User).filter(User.id == match.winner_id).first() if match.winner_id else None
        match_responses.append(TournamentMatchResponse(
            id=match.id,
            round_number=match.round_number,
            slot1_id=match.slot1_id,
            slot2_id=match.slot2_id,
            user1_id=match.user1_id,
            user2_id=match.user2_id,
            user1_handle=user1.handle if user1 else "Unknown",
            user2_handle=user2.handle if user2 else "Unknown",
            contest_id=match.contest_id,
            winner_id=match.winner_id,
            winner_handle=winner.handle if winner else None,
            status=match.status.value,
            start_time=match.start_time,
            end_time=match.end_time
        ))
    
    round_schedule_responses = [
        TournamentRoundScheduleResponse(
            id=rs.id,
            round_number=rs.round_number,
            start_time=rs.start_time
        ) for rs in round_schedules
    ]
    
    return TournamentResponse(
        id=tournament.id,
        creator_id=tournament.creator_id,
        creator_handle=creator.handle if creator else "Unknown",
        num_participants=tournament.num_participants,
        difficulty=tournament.difficulty,
        status=tournament.status.value,
        created_at=tournament.created_at,
        start_time=tournament.start_time,
        slots=slot_responses,
        invites=invite_responses,
        matches=match_responses,
        round_schedules=round_schedule_responses
    )


@router.put("/{tournament_id}/round-schedules", response_model=List[TournamentRoundScheduleResponse])
async def set_round_schedules(
    tournament_id: str,
    schedules_data: TournamentRoundScheduleUpdate,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Set round start times for tournament (creator only)"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the tournament creator can set round schedules"
        )
    
    if tournament.status == TournamentStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify round schedules after tournament has started"
        )
    
    num_rounds = calculate_num_rounds(tournament.num_participants)
    
    # Validate all rounds are provided
    if len(schedules_data.round_schedules) != num_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must provide schedules for all {num_rounds} rounds"
        )
    
    # Validate round numbers
    round_numbers = [s.round_number for s in schedules_data.round_schedules]
    if set(round_numbers) != set(range(1, num_rounds + 1)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Round numbers must be 1 through {num_rounds}"
        )
    
    # Validate start times are in future
    now = datetime.utcnow()
    for schedule in schedules_data.round_schedules:
        if schedule.start_time <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Round {schedule.round_number} start time must be in the future"
            )
    
    # Validate no overlaps (each round is 2 hours)
    sorted_schedules = sorted(schedules_data.round_schedules, key=lambda x: x.round_number)
    for i in range(len(sorted_schedules) - 1):
        current_end = sorted_schedules[i].start_time + timedelta(hours=2)
        next_start = sorted_schedules[i + 1].start_time
        if current_end > next_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Round {sorted_schedules[i].round_number} overlaps with round {sorted_schedules[i + 1].round_number}"
            )
    
    # Delete existing schedules
    db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id
    ).delete()
    
    # Create new schedules
    for schedule_data in schedules_data.round_schedules:
        schedule = TournamentRoundSchedule(
            tournament_id=tournament.id,
            round_number=schedule_data.round_number,
            start_time=schedule_data.start_time
        )
        db.add(schedule)
    
    db.commit()
    
    # Return updated schedules
    round_schedules = db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id
    ).order_by(TournamentRoundSchedule.round_number).all()
    
    return [
        TournamentRoundScheduleResponse(
            id=rs.id,
            round_number=rs.round_number,
            start_time=rs.start_time
        ) for rs in round_schedules
    ]


@router.post("/{tournament_id}/invites", response_model=TournamentInviteResponse)
async def send_invite(
    tournament_id: str,
    invite_data: TournamentInviteCreate,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Send an invite to a user for a tournament slot"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the tournament creator can send invites"
        )
    
    # Validate slot belongs to tournament
    slot = db.query(TournamentSlot).filter(
        TournamentSlot.id == invite_data.slot_id,
        TournamentSlot.tournament_id == tournament.id
    ).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    
    # Validate slot is empty or has rejected invite
    if slot.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot is already filled"
        )
    
    # Validate user exists
    invited_user = db.query(User).filter(User.id == invite_data.invited_user_id).first()
    if not invited_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invited user not found"
        )
    
    # Validate user not already invited to this tournament
    existing_invite = db.query(TournamentInvite).filter(
        TournamentInvite.tournament_id == tournament.id,
        TournamentInvite.invited_user_id == invite_data.invited_user_id,
        TournamentInvite.status == TournamentInviteStatus.PENDING
    ).first()
    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a pending invite for this tournament"
        )
    
    # Validate user not already in tournament
    existing_slot = db.query(TournamentSlot).filter(
        TournamentSlot.tournament_id == tournament.id,
        TournamentSlot.user_id == invite_data.invited_user_id
    ).first()
    if existing_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a participant in this tournament"
        )
    
    # Check for overlapping contests
    round_schedules = db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id
    ).all()
    if round_schedules:
        overlap_error = check_overlapping_contests(invite_data.invited_user_id, round_schedules, db)
        if overlap_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=overlap_error
            )
    
    # Create invite
    invite = TournamentInvite(
        tournament_id=tournament.id,
        slot_id=invite_data.slot_id,
        invited_user_id=invite_data.invited_user_id,
        status=TournamentInviteStatus.PENDING
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    return TournamentInviteResponse(
        id=invite.id,
        tournament_id=invite.tournament_id,
        slot_id=invite.slot_id,
        slot_number=slot.slot_number,
        invited_user_id=invite.invited_user_id,
        invited_user_handle=invited_user.handle,
        status=invite.status.value,
        created_at=invite.created_at,
        responded_at=invite.responded_at
    )


@router.post("/{tournament_id}/invites/{invite_id}/accept", response_model=TournamentInviteResponse)
async def accept_invite(
    tournament_id: str,
    invite_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Accept a tournament invite"""
    invite = db.query(TournamentInvite).filter(
        TournamentInvite.id == invite_id,
        TournamentInvite.tournament_id == tournament_id
    ).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    if invite.invited_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite is not for you"
        )
    
    if invite.status != TournamentInviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite is not pending"
        )
    
    # Update slot
    slot = db.query(TournamentSlot).filter(TournamentSlot.id == invite.slot_id).first()
    if slot.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot is already filled"
        )
    
    slot.user_id = current_user.id
    slot.status = "ACCEPTED"
    
    # Update invite
    invite.status = TournamentInviteStatus.ACCEPTED
    invite.responded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(invite)
    
    invited_user = db.query(User).filter(User.id == invite.invited_user_id).first()
    
    return TournamentInviteResponse(
        id=invite.id,
        tournament_id=invite.tournament_id,
        slot_id=invite.slot_id,
        slot_number=slot.slot_number,
        invited_user_id=invite.invited_user_id,
        invited_user_handle=invited_user.handle if invited_user else "Unknown",
        status=invite.status.value,
        created_at=invite.created_at,
        responded_at=invite.responded_at
    )


@router.post("/{tournament_id}/invites/{invite_id}/reject", response_model=TournamentInviteResponse)
async def reject_invite(
    tournament_id: str,
    invite_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Reject a tournament invite"""
    invite = db.query(TournamentInvite).filter(
        TournamentInvite.id == invite_id,
        TournamentInvite.tournament_id == tournament_id
    ).first()
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    if invite.invited_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite is not for you"
        )
    
    # Update invite
    invite.status = TournamentInviteStatus.REJECTED
    invite.responded_at = datetime.utcnow()
    
    # Clear slot if it was filled by this invite
    slot = db.query(TournamentSlot).filter(TournamentSlot.id == invite.slot_id).first()
    if slot and slot.user_id == current_user.id:
        slot.user_id = None
        slot.status = "PENDING"
    
    db.commit()
    db.refresh(invite)
    
    invited_user = db.query(User).filter(User.id == invite.invited_user_id).first()
    
    return TournamentInviteResponse(
        id=invite.id,
        tournament_id=invite.tournament_id,
        slot_id=invite.slot_id,
        slot_number=slot.slot_number if slot else 0,
        invited_user_id=invite.invited_user_id,
        invited_user_handle=invited_user.handle if invited_user else "Unknown",
        status=invite.status.value,
        created_at=invite.created_at,
        responded_at=invite.responded_at
    )


@router.post("/{tournament_id}/slots/{slot_id}/join", response_model=TournamentSlotResponse)
async def creator_join_slot(
    tournament_id: str,
    slot_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Creator adds themselves to a slot"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the tournament creator can join slots"
        )
    
    slot = db.query(TournamentSlot).filter(
        TournamentSlot.id == slot_id,
        TournamentSlot.tournament_id == tournament.id
    ).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    
    if slot.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot is already filled"
        )
    
    slot.user_id = current_user.id
    slot.status = "ACCEPTED"
    db.commit()
    db.refresh(slot)
    
    return TournamentSlotResponse(
        id=slot.id,
        slot_number=slot.slot_number,
        user_id=slot.user_id,
        user_handle=current_user.handle,
        status=slot.status
    )


def generate_bracket_matches(tournament: Tournament, round_number: int, db: Session) -> List[TournamentMatch]:
    """Generate matches for a round"""
    if round_number == 1:
        # Round 1: Pair slots 1-2, 3-4, 5-6, etc.
        slots = db.query(TournamentSlot).filter(
            TournamentSlot.tournament_id == tournament.id
        ).order_by(TournamentSlot.slot_number).all()
        
        matches = []
        for i in range(0, len(slots), 2):
            if i + 1 < len(slots):
                slot1 = slots[i]
                slot2 = slots[i + 1]
                if slot1.user_id and slot2.user_id:
                    match = TournamentMatch(
                        tournament_id=tournament.id,
                        round_number=round_number,
                        slot1_id=slot1.id,
                        slot2_id=slot2.id,
                        user1_id=slot1.user_id,
                        user2_id=slot2.user_id,
                        status=TournamentMatchStatus.SCHEDULED
                    )
                    matches.append(match)
        return matches
    else:
        # Subsequent rounds: Pair winners from previous round
        previous_matches = db.query(TournamentMatch).filter(
            TournamentMatch.tournament_id == tournament.id,
            TournamentMatch.round_number == round_number - 1,
            TournamentMatch.winner_id.isnot(None)
        ).order_by(TournamentMatch.id).all()
        
        matches = []
        for i in range(0, len(previous_matches), 2):
            if i + 1 < len(previous_matches):
                match1 = previous_matches[i]
                match2 = previous_matches[i + 1]
                
                # Get slots for winners
                winner1_slot = db.query(TournamentSlot).filter(
                    TournamentSlot.tournament_id == tournament.id,
                    TournamentSlot.user_id == match1.winner_id
                ).first()
                winner2_slot = db.query(TournamentSlot).filter(
                    TournamentSlot.tournament_id == tournament.id,
                    TournamentSlot.user_id == match2.winner_id
                ).first()
                
                if winner1_slot and winner2_slot:
                    match = TournamentMatch(
                        tournament_id=tournament.id,
                        round_number=round_number,
                        slot1_id=winner1_slot.id,
                        slot2_id=winner2_slot.id,
                        user1_id=match1.winner_id,
                        user2_id=match2.winner_id,
                        status=TournamentMatchStatus.SCHEDULED
                    )
                    matches.append(match)
        return matches


@router.post("/{tournament_id}/start", response_model=TournamentResponse)
async def start_tournament(
    tournament_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Start tournament (creator only, when all slots filled)"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the tournament creator can start the tournament"
        )
    
    if tournament.status == TournamentStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament has already started"
        )
    
    # Validate all slots filled
    slots = db.query(TournamentSlot).filter(TournamentSlot.tournament_id == tournament.id).all()
    unfilled_slots = [s for s in slots if s.user_id is None]
    if unfilled_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"All slots must be filled before starting. {len(unfilled_slots)} slot(s) still empty."
        )
    
    # Validate round schedules are set
    num_rounds = calculate_num_rounds(tournament.num_participants)
    round_schedules = db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id
    ).all()
    if len(round_schedules) != num_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Round schedules must be set for all {num_rounds} rounds before starting"
        )
    
    # Get round 1 schedule
    round1_schedule = db.query(TournamentRoundSchedule).filter(
        TournamentRoundSchedule.tournament_id == tournament.id,
        TournamentRoundSchedule.round_number == 1
    ).first()
    
    if not round1_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Round 1 schedule not found"
        )
    
    # Generate bracket matches for round 1
    round1_matches = generate_bracket_matches(tournament, 1, db)
    
    if len(round1_matches) != tournament.num_participants // 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate matches for round 1"
        )
    
    # Create Contests for each match
    from ..models import ContestScore
    
    for match in round1_matches:
        contest = Contest(
            tournament_match_id=match.id,
            user1_id=match.user1_id,
            user2_id=match.user2_id,
            difficulty=tournament.difficulty,
            start_time=round1_schedule.start_time,
            end_time=round1_schedule.start_time + timedelta(hours=2),
            status=ContestStatus.SCHEDULED
        )
        db.add(contest)
        db.flush()  # Get contest.id
        
        match.contest_id = contest.id
        match.start_time = round1_schedule.start_time
        match.end_time = round1_schedule.start_time + timedelta(hours=2)
        db.add(match)
        
        # Create initial scores
        score1 = ContestScore(contest_id=contest.id, user_id=match.user1_id, total_points=0)
        score2 = ContestScore(contest_id=contest.id, user_id=match.user2_id, total_points=0)
        db.add(score1)
        db.add(score2)
    
    # Update tournament status
    tournament.status = TournamentStatus.ACTIVE
    tournament.start_time = datetime.utcnow()
    
    db.commit()
    
    # Return updated tournament
    return await get_tournament(tournament_id, current_user, db)


@router.get("/{tournament_id}/bracket", response_model=TournamentBracketResponse)
async def get_bracket(
    tournament_id: str,
    current_user: User = Depends(get_confirmed_user),
    db: Session = Depends(get_db)
):
    """Get bracket structure for visualization"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Check authorization
    is_creator = tournament.creator_id == current_user.id
    is_participant = db.query(TournamentSlot).filter(
        TournamentSlot.tournament_id == tournament.id,
        TournamentSlot.user_id == current_user.id
    ).first() is not None
    
    if not (is_creator or is_participant):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this tournament"
        )
    
    num_rounds = calculate_num_rounds(tournament.num_participants)
    rounds_data = []
    
    for round_num in range(1, num_rounds + 1):
        matches = db.query(TournamentMatch).filter(
            TournamentMatch.tournament_id == tournament.id,
            TournamentMatch.round_number == round_num
        ).order_by(TournamentMatch.id).all()
        
        round_matches = []
        for match in matches:
            user1 = db.query(User).filter(User.id == match.user1_id).first()
            user2 = db.query(User).filter(User.id == match.user2_id).first()
            winner = db.query(User).filter(User.id == match.winner_id).first() if match.winner_id else None
            
            round_matches.append({
                "id": str(match.id),
                "slot1_id": str(match.slot1_id),
                "slot2_id": str(match.slot2_id),
                "user1_id": str(match.user1_id),
                "user2_id": str(match.user2_id),
                "user1_handle": user1.handle if user1 else "Unknown",
                "user2_handle": user2.handle if user2 else "Unknown",
                "winner_id": str(match.winner_id) if match.winner_id else None,
                "winner_handle": winner.handle if winner else None,
                "status": match.status.value,
                "contest_id": str(match.contest_id) if match.contest_id else None
            })
        
        rounds_data.append({
            "round_number": round_num,
            "matches": round_matches
        })
    
    return TournamentBracketResponse(rounds=rounds_data)
