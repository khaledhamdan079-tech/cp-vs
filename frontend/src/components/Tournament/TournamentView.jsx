import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import UserSearch from '../Challenge/UserSearch';
import TournamentBracket from './TournamentBracket';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './TournamentView.css';

const TournamentView = () => {
  const { tournamentId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [tournament, setTournament] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [roundSchedules, setRoundSchedules] = useState([]);
  const [inviteError, setInviteError] = useState('');
  const [activeTab, setActiveTab] = useState('slots');

  useEffect(() => {
    fetchTournament();
  }, [tournamentId]);

  const fetchTournament = async () => {
    try {
      const response = await apiClient.get(`/api/tournaments/${tournamentId}`);
      setTournament(response.data);
      
      // Initialize round schedules if tournament hasn't started
      if (response.data.status === 'pending' || response.data.status === 'registering') {
        const numRounds = Math.log2(response.data.num_participants);
        const schedules = [];
        for (let i = 1; i <= Math.floor(numRounds); i++) {
          const existing = response.data.round_schedules.find(rs => rs.round_number === i);
          schedules.push({
            round_number: i,
            start_time: existing ? existing.start_time : ''
          });
        }
        setRoundSchedules(schedules);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load tournament');
    } finally {
      setLoading(false);
    }
  };

  const handleSendInvite = async () => {
    if (!selectedSlot || !selectedUser) {
      setInviteError('Please select a slot and a user');
      return;
    }

    setInviteError('');
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/invites`, {
        invited_user_id: selectedUser.id,
        slot_id: selectedSlot.id,
      });
      setSelectedSlot(null);
      setSelectedUser(null);
      fetchTournament();
    } catch (err) {
      setInviteError(err.response?.data?.detail || 'Failed to send invite');
    }
  };

  const handleAcceptInvite = async (inviteId) => {
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/invites/${inviteId}/accept`);
      fetchTournament();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to accept invite');
    }
  };

  const handleRejectInvite = async (inviteId) => {
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/invites/${inviteId}/reject`);
      fetchTournament();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reject invite');
    }
  };

  const handleJoinSlot = async (slotId) => {
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/slots/${slotId}/join`);
      fetchTournament();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to join slot');
    }
  };

  const handleSaveRoundSchedules = async () => {
    try {
      // Validate all schedules have times
      const incomplete = roundSchedules.find(rs => !rs.start_time);
      if (incomplete) {
        setError(`Please set a start time for round ${incomplete.round_number}`);
        return;
      }
      
      const schedules = roundSchedules.map(rs => ({
        round_number: rs.round_number,
        start_time: new Date(rs.start_time).toISOString(),
      }));
      
      await apiClient.put(`/api/tournaments/${tournamentId}/round-schedules`, {
        round_schedules: schedules,
      });
      fetchTournament();
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save round schedules');
    }
  };

  const handleStartTournament = async () => {
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/start`);
      fetchTournament();
      setActiveTab('bracket');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start tournament');
    }
  };

  const handleCancelTournament = async () => {
    if (!window.confirm('Are you sure you want to cancel this tournament? This action cannot be undone.')) {
      return;
    }
    
    try {
      await apiClient.post(`/api/tournaments/${tournamentId}/cancel`);
      // Navigate back to dashboard after cancellation
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to cancel tournament');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!tournament) {
    return <div className="error-message">Tournament not found</div>;
  }

  const isCreator = user && tournament.creator_id === user.id;
  const numRounds = Math.floor(Math.log2(tournament.num_participants));
  const allSlotsFilled = tournament.slots.every(slot => slot.user_id);
  const allRoundsScheduled = tournament.round_schedules.length === numRounds;
  const canStart = allSlotsFilled && allRoundsScheduled && tournament.status === 'pending';
  const canCancel = isCreator && tournament.status !== 'active' && tournament.status !== 'completed' && tournament.status !== 'cancelled';

  // Get pending invites for current user
  const pendingInvites = tournament.invites.filter(
    invite => invite.status === 'pending'
  );

  return (
    <div className="tournament-view">
      <div className="tournament-header">
        <div className="tournament-header-content">
          <h1>Tournament #{tournament.id.slice(0, 8)}</h1>
          <div className="tournament-info">
            <p><strong>Participants:</strong> {tournament.num_participants}</p>
            <p><strong>Difficulty:</strong> {tournament.difficulty}</p>
            <p><strong>Status:</strong> {tournament.status}</p>
            {tournament.start_time && (
              <p><strong>Started:</strong> {formatLocalDateTime(tournament.start_time)}</p>
            )}
          </div>
        </div>
        {canCancel && (
          <button 
            onClick={handleCancelTournament} 
            className="btn-cancel-tournament"
          >
            Cancel Tournament
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      {tournament.status === 'active' || tournament.status === 'completed' ? (
        <TournamentBracket tournament={tournament} />
      ) : (
        <>
          <div className="tabs">
            <button
              className={activeTab === 'slots' ? 'active' : ''}
              onClick={() => setActiveTab('slots')}
            >
              Slots & Invites
            </button>
            {isCreator && (
              <button
                className={activeTab === 'schedules' ? 'active' : ''}
                onClick={() => setActiveTab('schedules')}
              >
                Round Schedules
              </button>
            )}
          </div>

          {activeTab === 'slots' && (
            <div className="slots-section">
              {pendingInvites.length > 0 && (
                <div className="pending-invites">
                  <h2>Pending Invites (You Received)</h2>
                  {pendingInvites.map((invite) => (
                    <div key={invite.id} className="invite-card">
                      <p>Slot {invite.slot_number}</p>
                      <div>
                        <button
                          onClick={() => handleAcceptInvite(invite.id)}
                          className="btn-accept"
                        >
                          Accept
                        </button>
                        <button
                          onClick={() => handleRejectInvite(invite.id)}
                          className="btn-reject"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {isCreator && (
                <div className="invite-section">
                  <h2>Send Invite</h2>
                  <div className="invite-form">
                    <div className="form-group">
                      <label>Select Slot</label>
                      <select
                        value={selectedSlot?.id || ''}
                        onChange={(e) => {
                          const slot = tournament.slots.find(s => s.id === e.target.value);
                          setSelectedSlot(slot);
                        }}
                      >
                        <option value="">Select a slot</option>
                        {tournament.slots
                          .filter(slot => !slot.user_id)
                          .map(slot => (
                            <option key={slot.id} value={slot.id}>
                              Slot {slot.slot_number}
                            </option>
                          ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Select User</label>
                      <UserSearch onSelect={setSelectedUser} selectedUser={selectedUser} />
                    </div>
                    {inviteError && <div className="error-message">{inviteError}</div>}
                    <button onClick={handleSendInvite} className="btn-primary">
                      Send Invite
                    </button>
                  </div>
                </div>
              )}

              <div className="slots-grid">
                <h2>Tournament Slots</h2>
                <div className="slots-list">
                  {tournament.slots.map((slot) => (
                    <div key={slot.id} className={`slot-card ${slot.user_id ? 'filled' : 'empty'}`}>
                      <h3>Slot {slot.slot_number}</h3>
                      {slot.user_id ? (
                        <p>{slot.user_handle}</p>
                      ) : (
                        <>
                          <p>Empty</p>
                          {isCreator && (
                            <button
                              onClick={() => handleJoinSlot(slot.id)}
                              className="btn-join"
                            >
                              Join This Slot
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {isCreator && canStart && (
                <div className="start-section">
                  <button onClick={handleStartTournament} className="btn-start">
                    Start Tournament
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'schedules' && isCreator && (
            <div className="schedules-section">
              <h2>Round Schedules</h2>
              <p>Set start times for each round. Each round lasts 2 hours.</p>
              {roundSchedules.map((schedule, index) => (
                <div key={schedule.round_number} className="schedule-item">
                  <label>Round {schedule.round_number}</label>
                  <input
                    type="datetime-local"
                    value={schedule.start_time ? (
                      typeof schedule.start_time === 'string' && schedule.start_time.includes('T') 
                        ? schedule.start_time.slice(0, 16) 
                        : new Date(schedule.start_time).toISOString().slice(0, 16)
                    ) : ''}
                    onChange={(e) => {
                      const updated = [...roundSchedules];
                      updated[index].start_time = e.target.value;
                      setRoundSchedules(updated);
                    }}
                    min={new Date().toISOString().slice(0, 16)}
                  />
                </div>
              ))}
              <button onClick={handleSaveRoundSchedules} className="btn-primary">
                Save Round Schedules
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TournamentView;
