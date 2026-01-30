import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './Homepage.css';

const Homepage = () => {
  const [topUsers, setTopUsers] = useState([]);
  const [latestMatches, setLatestMatches] = useState([]);
  const [topMatches, setTopMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, latestRes, topRes] = await Promise.all([
        apiClient.get('/api/users/leaderboard?limit=10'),
        apiClient.get('/api/contests/public/latest?limit=10'),
        apiClient.get('/api/contests/public/top?limit=5&sort_by=rating_change'),
      ]);
      setTopUsers(usersRes.data);
      setLatestMatches(latestRes.data);
      setTopMatches(topRes.data);
    } catch (error) {
      console.error('Error fetching homepage data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="homepage">
      <div className="homepage-hero">
        <h1>Welcome to CP VS</h1>
        <p>Compete head-to-head in Codeforces contests and climb the leaderboard!</p>
      </div>

      <div className="homepage-content">
        {/* Top Users Leaderboard */}
        <section className="homepage-section">
          <div className="section-header">
            <h2>Top Users</h2>
            <Link to="/leaderboard" className="btn-view-all">
              View All
            </Link>
          </div>
          <div className="leaderboard-table">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Handle</th>
                  <th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {topUsers.map((user) => (
                  <tr key={user.id}>
                    <td className="rank">{user.rank}</td>
                    <td>
                      <Link to={`/users/${user.handle}`} className="user-link">
                        {user.handle}
                      </Link>
                    </td>
                    <td className="rating">{user.rating}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Latest Matches */}
        <section className="homepage-section">
          <div className="section-header">
            <h2>Latest Matches</h2>
          </div>
          <div className="matches-list">
            {latestMatches.length === 0 ? (
              <p className="no-data">No matches yet</p>
            ) : (
              latestMatches.map((match) => (
                <div key={match.id} className="match-card">
                  <div className="match-participants">
                    <Link to={`/users/${match.user1_handle}`} className="participant-link">
                      {match.user1_handle}
                    </Link>
                    <span className="vs">vs</span>
                    <Link to={`/users/${match.user2_handle}`} className="participant-link">
                      {match.user2_handle}
                    </Link>
                  </div>
                  <div className="match-scores">
                    <span className="score">{match.user1_points}</span>
                    <span className="separator">-</span>
                    <span className="score">{match.user2_points}</span>
                  </div>
                  <div className="match-rating-changes">
                    {match.user1_rating_change !== null && (
                      <span className={`rating-change ${match.user1_rating_change >= 0 ? 'positive' : 'negative'}`}>
                        {match.user1_rating_change >= 0 ? '+' : ''}{match.user1_rating_change}
                      </span>
                    )}
                    {match.user2_rating_change !== null && (
                      <span className={`rating-change ${match.user2_rating_change >= 0 ? 'positive' : 'negative'}`}>
                        {match.user2_rating_change >= 0 ? '+' : ''}{match.user2_rating_change}
                      </span>
                    )}
                  </div>
                  <div className="match-date">
                    {formatLocalDateTime(match.end_time)}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Top Matches */}
        <section className="homepage-section">
          <div className="section-header">
            <h2>Top Matches</h2>
          </div>
          <div className="matches-list">
            {topMatches.length === 0 ? (
              <p className="no-data">No matches yet</p>
            ) : (
              topMatches.map((match) => (
                <div key={match.id} className="match-card">
                  <div className="match-participants">
                    <Link to={`/users/${match.user1_handle}`} className="participant-link">
                      {match.user1_handle}
                    </Link>
                    <span className="vs">vs</span>
                    <Link to={`/users/${match.user2_handle}`} className="participant-link">
                      {match.user2_handle}
                    </Link>
                  </div>
                  <div className="match-scores">
                    <span className="score">{match.user1_points}</span>
                    <span className="separator">-</span>
                    <span className="score">{match.user2_points}</span>
                  </div>
                  <div className="match-rating-changes">
                    {match.user1_rating_change !== null && (
                      <span className={`rating-change ${match.user1_rating_change >= 0 ? 'positive' : 'negative'}`}>
                        {match.user1_rating_change >= 0 ? '+' : ''}{match.user1_rating_change}
                      </span>
                    )}
                    {match.user2_rating_change !== null && (
                      <span className={`rating-change ${match.user2_rating_change >= 0 ? 'positive' : 'negative'}`}>
                        {match.user2_rating_change >= 0 ? '+' : ''}{match.user2_rating_change}
                      </span>
                    )}
                  </div>
                  <div className="match-date">
                    {formatLocalDateTime(match.end_time)}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Homepage;
