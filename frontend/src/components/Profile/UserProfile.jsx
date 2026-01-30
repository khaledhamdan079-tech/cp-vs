import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './UserProfile.css';

const UserProfile = () => {
  const { handle } = useParams();
  const [profile, setProfile] = useState(null);
  const [recentContests, setRecentContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfile();
    fetchRecentContests();
  }, [handle]);

  const fetchProfile = async () => {
    try {
      const response = await apiClient.get(`/api/users/${handle}/profile`);
      setProfile(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'User not found');
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentContests = async () => {
    try {
      // Get all contests and filter for this user
      const response = await apiClient.get('/api/contests/public/latest?limit=50');
      const allContests = response.data;
      const userContests = allContests.filter(
        (contest) =>
          contest.user1_handle === handle || contest.user2_handle === handle
      );
      setRecentContests(userContests.slice(0, 10));
    } catch (err) {
      console.error('Error fetching recent contests:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error || !profile) {
    return (
      <div className="error-container">
        <h2>User Not Found</h2>
        <p>{error || 'The user you are looking for does not exist.'}</p>
        <Link to="/leaderboard" className="btn-back">
          Back to Leaderboard
        </Link>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <div className="profile-header">
        <div className="profile-info">
          <h1>{profile.handle}</h1>
          <div className="profile-meta">
            <span className="rating-badge">Rating: {profile.rating}</span>
            <span className="member-since">
              Member since {formatLocalDateTime(profile.created_at, { dateStyle: 'long' })}
            </span>
          </div>
        </div>
      </div>

      <div className="profile-stats">
        <div className="stat-card">
          <div className="stat-value">{profile.total_contests}</div>
          <div className="stat-label">Total Contests</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{profile.wins}</div>
          <div className="stat-label">Wins</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{profile.losses}</div>
          <div className="stat-label">Losses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{profile.draws}</div>
          <div className="stat-label">Draws</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{profile.win_rate.toFixed(1)}%</div>
          <div className="stat-label">Win Rate</div>
        </div>
      </div>

      <div className="profile-section">
        <h2>Recent Contests</h2>
        {recentContests.length === 0 ? (
          <p className="no-data">No contests yet</p>
        ) : (
          <div className="contests-list">
            {recentContests.map((contest) => {
              const isUser1 = contest.user1_handle === handle;
              const userPoints = isUser1 ? contest.user1_points : contest.user2_points;
              const opponentPoints = isUser1 ? contest.user2_points : contest.user1_points;
              const opponentHandle = isUser1 ? contest.user2_handle : contest.user1_handle;
              const userRatingChange = isUser1
                ? contest.user1_rating_change
                : contest.user2_rating_change;
              const result =
                userPoints > opponentPoints
                  ? 'win'
                  : userPoints < opponentPoints
                  ? 'loss'
                  : 'draw';

              return (
                <div key={contest.id} className={`contest-item ${result}`}>
                  <div className="contest-opponent">
                    vs{' '}
                    <Link to={`/users/${opponentHandle}`} className="opponent-link">
                      {opponentHandle}
                    </Link>
                  </div>
                  <div className="contest-score">
                    {userPoints} - {opponentPoints}
                  </div>
                  {userRatingChange !== null && (
                    <div
                      className={`rating-change ${
                        userRatingChange >= 0 ? 'positive' : 'negative'
                      }`}
                    >
                      {userRatingChange >= 0 ? '+' : ''}
                      {userRatingChange}
                    </div>
                  )}
                  <div className="contest-date">
                    {formatLocalDateTime(contest.end_time)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
