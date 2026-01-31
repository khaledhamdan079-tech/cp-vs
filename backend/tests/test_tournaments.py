"""
Comprehensive tests for tournament functionality
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status
import uuid

from app.models import (
    Tournament, TournamentSlot, TournamentInvite, TournamentMatch,
    TournamentRoundSchedule, Contest, ContestStatus, TournamentStatus,
    TournamentInviteStatus, TournamentMatchStatus, User
)
from app.auth import create_access_token, get_password_hash


class TestTournamentCreation:
    """Test tournament creation"""
    
    def test_create_tournament_4_participants(self, client, auth_headers):
        """Test creating a tournament with 4 participants"""
        response = client.post(
            "/api/tournaments/",
            json={"num_participants": 4, "difficulty": 2},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["num_participants"] == 4
        assert data["difficulty"] == 2
        assert data["status"] == "pending"
        assert len(data["slots"]) == 4
        assert all(slot["slot_number"] == i + 1 for i, slot in enumerate(data["slots"]))
    
    def test_create_tournament_8_participants(self, client, auth_headers):
        """Test creating a tournament with 8 participants"""
        response = client.post(
            "/api/tournaments/",
            json={"num_participants": 8, "difficulty": 3},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["num_participants"] == 8
        assert len(data["slots"]) == 8
    
    def test_create_tournament_invalid_participants(self, client, auth_headers):
        """Test creating tournament with invalid number of participants"""
        response = client.post(
            "/api/tournaments/",
            json={"num_participants": 5, "difficulty": 2},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_tournament_invalid_difficulty(self, client, auth_headers):
        """Test creating tournament with invalid difficulty"""
        response = client.post(
            "/api/tournaments/",
            json={"num_participants": 8, "difficulty": 5},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRoundSchedules:
    """Test round schedule management"""
    
    def test_set_round_schedules_4_participants(self, client, auth_headers, tournament_4_participants):
        """Test setting round schedules for 4-participant tournament (2 rounds)"""
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)  # 1 hour gap after 2-hour round
        
        response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["round_number"] == 1
        assert data[1]["round_number"] == 2
    
    def test_set_round_schedules_overlapping(self, client, auth_headers, tournament_4_participants):
        """Test that overlapping round schedules are rejected"""
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=1)  # Overlaps with round 1
        
        response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_set_round_schedules_past_time(self, client, auth_headers, tournament_4_participants):
        """Test that past times are rejected"""
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": past_time.isoformat()},
                    {"round_number": 2, "start_time": (past_time + timedelta(hours=3)).isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_set_round_schedules_wrong_count(self, client, auth_headers, tournament_4_participants):
        """Test that wrong number of rounds is rejected"""
        round1_time = datetime.utcnow() + timedelta(days=1)
        
        response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestInvites:
    """Test invite management"""
    
    def test_send_invite(self, client, auth_headers, auth_headers_user2, tournament_4_participants, test_user, test_user2):
        """Test sending an invite"""
        # First set round schedules (required for overlap checking)
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        
        # Get a slot (tournament was created by test_user, so use auth_headers)
        client.current_user_ref[0] = test_user  # Ensure user is set
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data, f"Response keys: {list(tournament_data.keys())}"
        assert len(tournament_data["slots"]) > 0, f"Slots: {tournament_data.get('slots', [])}"
        slot_id = tournament_data["slots"][0]["id"]
        
        # Send invite
        client.current_user_ref[0] = test_user  # Ensure user is set before sending invite
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites",
            json={
                "invited_user_id": str(test_user2.id),
                "slot_id": slot_id
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "pending"
        assert data["invited_user_id"] == str(test_user2.id)
    
    def test_accept_invite(self, client, auth_headers, auth_headers_user2, tournament_4_participants, test_user, test_user2, db):
        """Test accepting an invite"""
        # Set round schedules
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        
        # Get a slot and send invite
        client.current_user_ref[0] = test_user  # Ensure user is set
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data
        slot_id = tournament_data["slots"][0]["id"]
        
        client.current_user_ref[0] = test_user  # Ensure user is set before sending invite
        invite_response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites",
            json={
                "invited_user_id": str(test_user2.id),
                "slot_id": slot_id
            },
            headers=auth_headers
        )
        invite_id = invite_response.json()["id"]
        
        # Accept invite
        client.current_user_ref[0] = test_user2  # Set user2 for accepting
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites/{invite_id}/accept",
            headers=auth_headers_user2
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "accepted"
        
        # Verify slot is filled
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        slot = next(s for s in tournament_response.json()["slots"] if s["id"] == slot_id)
        assert slot["user_id"] == str(test_user2.id)
    
    def test_reject_invite(self, client, auth_headers, auth_headers_user2, tournament_4_participants, test_user, test_user2):
        """Test rejecting an invite"""
        # Set round schedules
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        
        # Get a slot and send invite
        client.current_user_ref[0] = test_user  # Ensure user is set
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data
        slot_id = tournament_data["slots"][0]["id"]
        
        client.current_user_ref[0] = test_user  # Ensure user is set before sending invite
        invite_response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites",
            json={
                "invited_user_id": str(test_user2.id),
                "slot_id": slot_id
            },
            headers=auth_headers
        )
        invite_id = invite_response.json()["id"]
        
        # Reject invite
        client.current_user_ref[0] = test_user2  # Set user2 for rejecting
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites/{invite_id}/reject",
            headers=auth_headers_user2
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "rejected"
    
    def test_creator_join_slot(self, client, auth_headers, tournament_4_participants):
        """Test creator joining a slot"""
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        slot_id = tournament_response.json()["slots"][0]["id"]
        
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/slots/{slot_id}/join",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user_id"] is not None


class TestTournamentStart:
    """Test tournament starting"""
    
    def test_start_tournament_all_slots_filled(self, client, auth_headers, auth_headers_user2, auth_headers_user3, tournament_4_participants, test_user, test_user2, test_user3, db):
        """Test starting tournament when all slots are filled"""
        # Set round schedules (must be done before filling slots)
        client.current_user_ref[0] = test_user  # Ensure user is set
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        schedule_response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert schedule_response.status_code == status.HTTP_200_OK, f"Failed to set schedules: {schedule_response.json()}"
        
        # Fill all slots
        client.current_user_ref[0] = test_user  # Ensure user is set
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data
        slots = tournament_data["slots"]
        
        # Creator joins slot 1
        client.current_user_ref[0] = test_user  # Ensure user is set
        client.post(
            f"/api/tournaments/{tournament_4_participants.id}/slots/{slots[0]['id']}/join",
            headers=auth_headers
        )
        
        # Send invites for remaining 3 slots (slots 2, 3, 4)
        # slots[1:] gives us slots[1], slots[2], slots[3] which are slots 2, 3, 4
        for i, slot in enumerate(slots[1:], 1):
            if i == 1:
                invite_user = test_user2
                invite_headers = auth_headers_user2
            elif i == 2:
                invite_user = test_user3
                invite_headers = auth_headers_user3
            else:
                # Create additional users if needed
                try:
                    password_hash = get_password_hash("testpass123")
                except:
                    password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
                
                new_user = User(
                    id=uuid.uuid4(),
                    handle=f"testuser{i+3}",
                    password_hash=password_hash,
                    rating=1200,
                    is_confirmed=True
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                invite_user = new_user
                token = create_access_token(data={"sub": str(new_user.id)})
                invite_headers = {"Authorization": f"Bearer {token}"}
            
            # Set creator as current user for sending invite
            client.current_user_ref[0] = test_user
            
            invite_response = client.post(
                f"/api/tournaments/{tournament_4_participants.id}/invites",
                json={
                    "invited_user_id": str(invite_user.id),
                    "slot_id": slot["id"]
                },
                headers=auth_headers
            )
            invite_id = invite_response.json()["id"]
            
            # Set invited user as current user for accepting
            client.current_user_ref[0] = invite_user
            client.post(
                f"/api/tournaments/{tournament_4_participants.id}/invites/{invite_id}/accept",
                headers=invite_headers
            )
        
        # Verify all slots are filled before starting
        client.current_user_ref[0] = test_user  # Ensure user is set
        verify_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        verify_data = verify_response.json()
        filled_slots = [s for s in verify_data["slots"] if s["user_id"] is not None]
        assert len(filled_slots) == 4, f"Expected 4 filled slots, got {len(filled_slots)}. Slots: {verify_data['slots']}"
        
        # Refresh slots from database to ensure they're up to date
        from app.models import TournamentSlot
        db_slots = db.query(TournamentSlot).filter(
            TournamentSlot.tournament_id == tournament_4_participants.id
        ).all()
        filled_db_slots = [s for s in db_slots if s.user_id is not None]
        assert len(filled_db_slots) == 4, f"Expected 4 filled slots in DB, got {len(filled_db_slots)}"
        
        # Start tournament
        client.current_user_ref[0] = test_user  # Ensure user is set before starting
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/start",
            headers=auth_headers
        )
        if response.status_code != status.HTTP_200_OK:
            print(f"Start tournament failed: {response.status_code}, {response.json()}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "active"
        assert len(data["matches"]) == 2  # 4 participants = 2 matches in round 1
    
    def test_start_tournament_missing_schedules(self, client, auth_headers, tournament_4_participants, test_user, db):
        """Test that tournament cannot start without round schedules"""
        # Fill all slots without setting schedules
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        slots = tournament_response.json()["slots"]
        
        # Fill slots
        for slot in slots:
            client.post(
                f"/api/tournaments/{tournament_4_participants.id}/slots/{slot['id']}/join",
                headers=auth_headers
            )
        
        # Try to start without schedules
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/start",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestBracketGeneration:
    """Test bracket generation logic"""
    
    def test_bracket_generation_round1(self, client, auth_headers, tournament_4_participants, test_user, test_user2, test_user3, db):
        """Test bracket generation for round 1"""
        # Set schedules and fill slots
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        
        # Fill all slots
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data
        slots = tournament_data["slots"]
        
        # Create users and fill slots
        users = [test_user, test_user2, test_user3]
        try:
            password_hash = get_password_hash("testpass123")
        except:
            password_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        
        new_user = User(
            id=uuid.uuid4(),
            handle="testuser4",
            password_hash=password_hash,
            rating=1100,
            is_confirmed=True
        )
        db.add(new_user)
        db.commit()
        users.append(new_user)
        
        for i, slot in enumerate(slots):
            if i == 0:
                # Creator joins slot
                client.current_user_ref[0] = test_user
                client.post(
                    f"/api/tournaments/{tournament_4_participants.id}/slots/{slot['id']}/join",
                    headers=auth_headers
                )
            else:
                # Send invite as creator
                client.current_user_ref[0] = test_user
                invite_response = client.post(
                    f"/api/tournaments/{tournament_4_participants.id}/invites",
                    json={
                        "invited_user_id": str(users[i].id),
                        "slot_id": slot["id"]
                    },
                    headers=auth_headers
                )
                # Accept invite as invited user
                client.current_user_ref[0] = users[i]
                token = create_access_token(data={"sub": str(users[i].id)})
                user_headers = {"Authorization": f"Bearer {token}"}
                client.post(
                    f"/api/tournaments/{tournament_4_participants.id}/invites/{invite_response.json()['id']}/accept",
                    headers=user_headers
                )
        
        # Start tournament (reset to creator)
        client.current_user_ref[0] = test_user
        
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/start",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Check bracket
        bracket_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}/bracket",
            headers=auth_headers
        )
        assert bracket_response.status_code == status.HTTP_200_OK
        bracket = bracket_response.json()
        assert len(bracket["rounds"]) == 2
        assert len(bracket["rounds"][0]["matches"]) == 2  # Round 1: 2 matches
        # Round 2 matches are only generated when round 1 completes, so check that round 2 exists but is empty
        assert len(bracket["rounds"][1]["matches"]) == 0   # Round 2: no matches yet (will be generated when round 1 completes)


class TestOverlapChecking:
    """Test overlap checking for invites"""
    
    def test_invite_overlap_check(self, client, auth_headers, auth_headers_user2, tournament_4_participants, test_user, test_user2, db):
        """Test that invites are rejected if user has overlapping contests"""
        from app.models import Contest, ContestScore
        
        # Set tournament round schedules
        client.current_user_ref[0] = test_user  # Ensure user is set
        round1_time = datetime.utcnow() + timedelta(days=1)
        round2_time = round1_time + timedelta(hours=3)
        schedule_response = client.put(
            f"/api/tournaments/{tournament_4_participants.id}/round-schedules",
            json={
                "round_schedules": [
                    {"round_number": 1, "start_time": round1_time.isoformat()},
                    {"round_number": 2, "start_time": round2_time.isoformat()}
                ]
            },
            headers=auth_headers
        )
        assert schedule_response.status_code == status.HTTP_200_OK, f"Failed to set schedules: {schedule_response.json()}"
        
        # Create an overlapping contest for test_user2
        # The contest overlaps exactly with round 1 (same start and end times)
        # Use a time that slightly overlaps to ensure detection
        contest_start = round1_time
        contest_end = round1_time + timedelta(hours=2)
        overlapping_contest = Contest(
            id=uuid.uuid4(),
            user1_id=test_user2.id,
            user2_id=uuid.uuid4(),  # Dummy user
            difficulty=2,
            start_time=contest_start,
            end_time=contest_end,
            status=ContestStatus.SCHEDULED
        )
        db.add(overlapping_contest)
        db.commit()
        db.refresh(overlapping_contest)  # Ensure it's persisted
        
        # Verify contest was created and times match
        from app.models import Contest
        verify_contest = db.query(Contest).filter(Contest.id == overlapping_contest.id).first()
        assert verify_contest is not None, "Contest was not created"
        assert verify_contest.user1_id == test_user2.id, "Contest user1_id mismatch"
        assert verify_contest.start_time == contest_start, f"Start time mismatch: {verify_contest.start_time} != {contest_start}"
        assert verify_contest.end_time == contest_end, f"End time mismatch: {verify_contest.end_time} != {contest_end}"
        
        # Verify round schedules exist
        from app.models import TournamentRoundSchedule
        round_schedules = db.query(TournamentRoundSchedule).filter(
            TournamentRoundSchedule.tournament_id == tournament_4_participants.id
        ).all()
        assert len(round_schedules) == 2, f"Expected 2 round schedules, got {len(round_schedules)}"
        assert round_schedules[0].start_time == round1_time, f"Round 1 schedule mismatch: {round_schedules[0].start_time} != {round1_time}"
        
        # Try to send invite
        client.current_user_ref[0] = test_user  # Ensure user is set
        tournament_response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert tournament_response.status_code == status.HTTP_200_OK
        tournament_data = tournament_response.json()
        assert "slots" in tournament_data
        slot_id = tournament_data["slots"][0]["id"]
        
        # Manually test overlap check
        from app.routers.tournaments import check_overlapping_contests
        overlap_error = check_overlapping_contests(test_user2.id, round_schedules, db)
        assert overlap_error is not None, f"Overlap check should detect conflict. Round schedules: {[(r.round_number, r.start_time) for r in round_schedules]}"
        
        client.current_user_ref[0] = test_user  # Ensure user is set before sending invite
        response = client.post(
            f"/api/tournaments/{tournament_4_participants.id}/invites",
            json={
                "invited_user_id": str(test_user2.id),
                "slot_id": slot_id
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Expected 400, got {response.status_code}: {response.json()}"
        assert "conflicting" in response.json()["detail"].lower() or "overlap" in response.json()["detail"].lower()


class TestTournamentList:
    """Test tournament listing"""
    
    def test_list_tournaments(self, client, auth_headers, tournament_4_participants):
        """Test listing tournaments"""
        response = client.get("/api/tournaments/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(t["id"] == str(tournament_4_participants.id) for t in data)
    
    def test_get_tournament_details(self, client, auth_headers, tournament_4_participants):
        """Test getting tournament details"""
        response = client.get(
            f"/api/tournaments/{tournament_4_participants.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(tournament_4_participants.id)
        assert data["num_participants"] == 4
        assert len(data["slots"]) == 4
