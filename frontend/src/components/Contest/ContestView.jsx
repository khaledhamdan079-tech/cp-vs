import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import ProblemCard from './ProblemCard';
import Leaderboard from './Leaderboard';
import { formatLocalDateTime, getTimeRemaining, utcToLocal } from '../../utils/dateUtils';
import './ContestView.css';

const ContestView = () => {
  const { contestId } = useParams();
  const { user } = useAuth();
  const [contest, setContest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    fetchContest();
    // Poll every 10 seconds if contest is active, or if contest is scheduled and less than 2 minutes before start
    const interval = setInterval(() => {
      if (contest) {
        const now = new Date();
        const startTime = utcToLocal(contest.start_time);
        const timeUntilStart = startTime - now;
        const twoMinutes = 2 * 60 * 1000; // 2 minutes in milliseconds
        
        // Poll if contest is active, or if scheduled and less than 2 minutes before start
        if (contest.status === 'active' || 
            (contest.status === 'scheduled' && timeUntilStart <= twoMinutes && timeUntilStart > 0)) {
          fetchContest();
        }
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [contestId, contest?.status, contest?.start_time]);

  // Update current time every second for time remaining display or when contest is about to start
  useEffect(() => {
    if (contest) {
      const now = new Date();
      const startTime = utcToLocal(contest.start_time);
      const timeUntilStart = startTime - now;
      const twoMinutes = 2 * 60 * 1000; // 2 minutes in milliseconds
      
      // Update time if contest is active, or if scheduled and less than 2 minutes before start
      if (contest.status === 'active' || 
          (contest.status === 'scheduled' && timeUntilStart <= twoMinutes && timeUntilStart > 0)) {
        const timeInterval = setInterval(() => {
          setCurrentTime(new Date());
        }, 1000);

        return () => clearInterval(timeInterval);
      }
    }
  }, [contest?.status, contest?.start_time]);

  const fetchContest = async () => {
    try {
      const response = await apiClient.get(`/api/contests/${contestId}`);
      setContest(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load contest');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading contest...</div>;
  }

  if (error) {
    return (
      <div className="error-container">
        <p>{error}</p>
        <Link to="/dashboard">Back to Dashboard</Link>
      </div>
    );
  }

  const now = currentTime;
  const startTime = utcToLocal(contest.start_time);
  const endTime = utcToLocal(contest.end_time);
  const hasStarted = now >= startTime;
  const isActive = contest.status === 'active';
  const isCompleted = contest.status === 'completed';

  return (
    <div className="contest-view">
      <div className="contest-header">
        <h1>
          {contest.user1_handle} vs {contest.user2_handle}
        </h1>
        <div className="contest-meta">
          <span className="badge difficulty">Difficulty: {contest.difficulty}</span>
          <span className={`badge status ${contest.status}`}>
            {contest.status.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="contest-info">
        <p>
          <strong>Start Time:</strong> {formatLocalDateTime(contest.start_time)}
        </p>
        <p>
          <strong>End Time:</strong> {formatLocalDateTime(contest.end_time)}
        </p>
        {isActive && (
          <p className="time-remaining">
            <strong>Time Remaining:</strong>{' '}
            {getTimeRemaining(contest.end_time).formatted}
          </p>
        )}
      </div>

      {!hasStarted && !isCompleted && (
        <div className="waiting-message">
          Contest will start at {formatLocalDateTime(contest.start_time)}
        </div>
      )}

      {hasStarted && (
        <>
          <Leaderboard scores={contest.scores} />
          <div className="problems-section">
            <h2>Problems</h2>
            {contest.problems.length === 0 ? (
              <p>No problems available yet.</p>
            ) : (
              <div className="problems-grid">
                {contest.problems.map((problem) => (
                  <ProblemCard 
                    key={problem.id} 
                    problem={problem}
                    currentUserId={user?.id}
                    user1Id={contest.user1_id}
                    user2Id={contest.user2_id}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}

      <div className="contest-actions">
        <Link to="/dashboard" className="btn-back">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default ContestView;
