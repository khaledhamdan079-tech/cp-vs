import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './ChallengeCard.css';

const ChallengeCard = ({ challenge, onUpdate }) => {
  const { user } = useAuth();
  const isChallenger = challenge.challenger.id === user?.id;
  const isChallenged = challenge.challenged.id === user?.id;

  const handleAccept = async () => {
    try {
      await apiClient.post(`/api/challenges/${challenge.id}/accept`);
      onUpdate();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to accept challenge');
    }
  };

  const handleReject = async () => {
    try {
      await apiClient.post(`/api/challenges/${challenge.id}/reject`);
      onUpdate();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to reject challenge');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return '#ffc107';
      case 'accepted':
        return '#28a745';
      case 'rejected':
        return '#dc3545';
      default:
        return '#666';
    }
  };

  return (
    <div className="challenge-card">
      <div className="challenge-header">
        <div>
          <h3>
            {challenge.challenger.handle} vs {challenge.challenged.handle}
          </h3>
          <span
            className="status-badge"
            style={{ backgroundColor: getStatusColor(challenge.status) }}
          >
            {challenge.status.toUpperCase()}
          </span>
        </div>
      </div>
      <div className="challenge-details">
        <p>
          <strong>Difficulty:</strong> {challenge.difficulty}
        </p>
        <p>
          <strong>Suggested Start:</strong>{' '}
          {formatLocalDateTime(challenge.suggested_start_time)}
        </p>
        <p>
          <strong>Created:</strong> {formatLocalDateTime(challenge.created_at)}
        </p>
      </div>
      {isChallenged && challenge.status === 'pending' && (
        <div className="challenge-actions">
          <button onClick={handleAccept} className="btn-accept">
            Accept
          </button>
          <button onClick={handleReject} className="btn-reject">
            Reject
          </button>
        </div>
      )}
      {isChallenger && challenge.status === 'pending' && (
        <p className="waiting-message">Waiting for response...</p>
      )}
    </div>
  );
};

export default ChallengeCard;
