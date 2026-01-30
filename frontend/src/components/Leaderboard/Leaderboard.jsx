import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../../api/client';
import './Leaderboard.css';

const Leaderboard = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const limit = 50;

  useEffect(() => {
    fetchLeaderboard();
  }, [offset]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/users/leaderboard?limit=${limit}&offset=${offset}`);
      const newUsers = response.data;
      
      if (newUsers.length < limit) {
        setHasMore(false);
      }
      
      if (offset === 0) {
        setUsers(newUsers);
      } else {
        setUsers([...users, ...newUsers]);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      setOffset(offset + limit);
    }
  };

  const filteredUsers = searchQuery
    ? users.filter((user) =>
        user.handle.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users;

  return (
    <div className="leaderboard-page">
      <div className="leaderboard-header">
        <h1>Leaderboard</h1>
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by handle..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="leaderboard-container">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Handle</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.length === 0 && !loading ? (
              <tr>
                <td colSpan="3" className="no-data">
                  No users found
                </td>
              </tr>
            ) : (
              filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td className="rank">{user.rank}</td>
                  <td>
                    <Link to={`/users/${user.handle}`} className="user-link">
                      {user.handle}
                    </Link>
                  </td>
                  <td className="rating">{user.rating}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {loading && (
          <div className="loading">Loading...</div>
        )}

        {hasMore && !loading && !searchQuery && (
          <div className="load-more-container">
            <button onClick={handleLoadMore} className="btn-load-more">
              Load More
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
