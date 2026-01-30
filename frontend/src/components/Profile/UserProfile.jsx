import { useState, useEffect, useCallback } from 'react';
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

  // Debug: Log component mount - ALWAYS log
  console.log('=== UserProfile component rendered ===', { 
    handle, 
    loading, 
    error: error ? error.substring(0, 50) : null,
    hasProfile: !!profile 
  });

  // CRITICAL: Always ensure we have a handle
  if (!handle) {
    console.error('No handle in URL params!');
  }

  const fetchProfile = useCallback(async () => {
    if (!handle) {
      setError('No handle provided');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      console.log('Fetching profile for handle:', handle);
      const response = await apiClient.get(`/api/users/${handle}/profile`);
      console.log('Profile data received:', response.data);
      setProfile(response.data);
    } catch (err) {
      console.error('Error fetching profile:', err);
      console.error('Error details:', err.response?.data);
      const errorMessage = err.response?.data?.detail || err.message || 'User not found';
      setError(errorMessage);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, [handle]);

  const fetchRecentContests = useCallback(async () => {
    if (!handle) return;
    
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
  }, [handle]);

  useEffect(() => {
    console.log('UserProfile useEffect triggered, handle:', handle);
    if (handle) {
      fetchProfile();
      fetchRecentContests();
    } else {
      setError('No handle provided');
      setLoading(false);
    }
  }, [handle, fetchProfile, fetchRecentContests]);

  // Always render something - never return null
  // Add explicit background color to ensure visibility
  console.log('UserProfile render state:', { handle, loading, error, profile: !!profile });
  
  // Safety check - ensure we always return valid JSX with visible content
  if (!handle) {
    return (
      <div style={{ 
        padding: '2rem', 
        backgroundColor: '#fff', 
        color: '#333',
        minHeight: '400px',
        border: '2px solid #dc3545' // Make it very visible
      }}>
        <h2 style={{ color: '#dc3545' }}>No Handle Provided</h2>
        <p style={{ color: '#333', margin: '1rem 0' }}>Please provide a user handle in the URL.</p>
        <Link to="/leaderboard" style={{ 
          color: '#667eea', 
          textDecoration: 'underline',
          display: 'inline-block',
          marginTop: '1rem'
        }}>
          Go to Leaderboard
        </Link>
      </div>
    );
  }

  // Render loading state with visible content
  if (loading) {
    return (
      <div className="user-profile" style={{ 
        minHeight: '400px', 
        backgroundColor: '#f5f5f5',
        padding: '2rem',
        color: '#333'
      }}>
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <h2 style={{ color: '#333', marginBottom: '1rem' }}>Loading Profile</h2>
          <p style={{ color: '#666' }}>Loading profile for: <strong style={{ color: '#667eea' }}>{handle}</strong></p>
          <div className="loading" style={{ marginTop: '1rem' }}>Please wait...</div>
        </div>
      </div>
    );
  }

  // Render error state with visible content
  if (error) {
    return (
      <div className="user-profile" style={{ 
        minHeight: '400px', 
        backgroundColor: '#fff',
        padding: '2rem'
      }}>
        <div className="error-container" style={{ 
          textAlign: 'center', 
          padding: '3rem',
          backgroundColor: '#fff',
          color: '#333'
        }}>
          <h2 style={{ color: '#dc3545', marginBottom: '1rem' }}>Error Loading Profile</h2>
          <p style={{ color: '#dc3545', margin: '1rem 0', fontSize: '1.1rem' }}>{error}</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Handle: <strong style={{ color: '#333' }}>{handle}</strong>
          </p>
          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link to="/leaderboard" className="btn-back" style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px'
            }}>
              Back to Leaderboard
            </Link>
            <Link to="/" className="btn-back" style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px'
            }}>
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Render not found state with visible content
  if (!profile) {
    return (
      <div className="user-profile" style={{ 
        minHeight: '400px', 
        backgroundColor: '#fff',
        padding: '2rem',
        color: '#333'
      }}>
        <div className="error-container" style={{ 
          textAlign: 'center', 
          padding: '3rem',
          backgroundColor: '#fff',
          color: '#333'
        }}>
          <h2 style={{ color: '#333', marginBottom: '1rem' }}>User Not Found</h2>
          <p style={{ color: '#666', fontSize: '1rem' }}>The user you are looking for does not exist.</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Handle: <strong style={{ color: '#333' }}>{handle}</strong>
          </p>
          <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link to="/leaderboard" className="btn-back" style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px'
            }}>
              Back to Leaderboard
            </Link>
            <Link to="/" className="btn-back" style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px'
            }}>
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  console.log('Rendering profile with data:', profile);
  console.log('Profile stats:', {
    total_contests: profile?.total_contests ?? 0,
    wins: profile?.wins ?? 0,
    losses: profile?.losses ?? 0,
    draws: profile?.draws ?? 0,
    win_rate: profile?.win_rate ?? 0
  });

  // Ensure profile data exists and has required fields
  if (!profile.handle) {
    console.error('Profile data is invalid - missing handle:', profile);
    return (
      <div className="user-profile" style={{ 
        minHeight: '400px', 
        backgroundColor: '#fff',
        padding: '2rem',
        color: '#333'
      }}>
        <div className="error-container">
          <h2 style={{ color: '#dc3545' }}>Invalid Profile Data</h2>
          <p>The profile data received is invalid.</p>
          <p style={{ fontSize: '0.9rem', color: '#666' }}>
            Handle: <strong>{handle}</strong>
          </p>
          <Link to="/leaderboard" className="btn-back">Back to Leaderboard</Link>
        </div>
      </div>
    );
  }

  try {
    return (
      <div className="user-profile" style={{ 
        minHeight: '100vh', 
        backgroundColor: '#f5f5f5',
        color: '#333',
        padding: '2rem'
      }}>
        <div className="profile-header">
          <div className="profile-info">
            <h1 style={{ color: 'white', margin: 0 }}>{profile.handle}</h1>
            <div className="profile-meta">
              <span className="rating-badge">Rating: {profile.rating || 1000}</span>
              {profile.created_at && (
                <span className="member-since">
                  Member since {(() => {
                    try {
                      return formatLocalDateTime(profile.created_at, { dateStyle: 'long' });
                    } catch (e) {
                      console.error('Error formatting date:', e);
                      try {
                        return new Date(profile.created_at).toLocaleDateString();
                      } catch (e2) {
                        return 'Unknown';
                      }
                    }
                  })()}
                </span>
              )}
            </div>
          </div>
        </div>

      <div className="profile-stats">
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#667eea' }}>{profile.total_contests ?? 0}</div>
          <div className="stat-label">Total Contests</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#28a745' }}>{profile.wins ?? 0}</div>
          <div className="stat-label">Wins</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#dc3545' }}>{profile.losses ?? 0}</div>
          <div className="stat-label">Losses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#ffc107' }}>{profile.draws ?? 0}</div>
          <div className="stat-label">Draws</div>
        </div>
        <div className="stat-card">
          <div className="stat-value" style={{ color: '#667eea' }}>{((profile.win_rate ?? 0)).toFixed(1)}%</div>
          <div className="stat-label">Win Rate</div>
        </div>
      </div>

      <div className="profile-section">
        <h2 style={{ color: '#333', marginBottom: '1rem' }}>Recent Contests</h2>
        {recentContests.length === 0 ? (
          <div className="no-data" style={{ 
            textAlign: 'center', 
            color: '#999', 
            padding: '2rem',
            backgroundColor: '#f9f9f9',
            borderRadius: '8px'
          }}>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>No contests yet</p>
            <p style={{ fontSize: '0.9rem' }}>
              {profile.total_contests === 0 
                ? 'This user hasn\'t participated in any contests yet.'
                : 'No recent contests to display.'}
            </p>
          </div>
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
                    {(() => {
                      try {
                        return formatLocalDateTime(contest.end_time);
                      } catch (e) {
                        console.error('Error formatting contest date:', e);
                        return new Date(contest.end_time).toLocaleString();
                      }
                    })()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      </div>
    );
  } catch (renderError) {
    console.error('Error rendering UserProfile:', renderError);
    return (
      <div className="user-profile" style={{ minHeight: '100vh', padding: '2rem' }}>
        <div className="error-container">
          <h2>Error Rendering Profile</h2>
          <p>An error occurred while rendering the profile page.</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Handle: <strong>{handle}</strong>
          </p>
          <p style={{ fontSize: '0.8rem', color: '#999', marginTop: '0.5rem' }}>
            Error: {renderError.message}
          </p>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link to="/leaderboard" className="btn-back">
              Back to Leaderboard
            </Link>
            <Link to="/" className="btn-back">
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }
};

export default UserProfile;
