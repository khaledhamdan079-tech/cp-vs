import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import ChallengeCard from '../Challenge/ChallengeCard';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [contests, setContests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('challenges');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [challengesRes, contestsRes] = await Promise.all([
        apiClient.get('/api/challenges/'),
        apiClient.get('/api/contests/'),
      ]);
      setChallenges(challengesRes.data);
      setContests(contestsRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  const pendingChallenges = challenges.filter(
    (c) => c.status === 'pending' && c.challenged.id === user?.id
  );

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <Link to="/challenges/create" className="btn-create">
          Create Challenge
        </Link>
      </div>

      <div className="tabs">
        <button
          className={activeTab === 'challenges' ? 'active' : ''}
          onClick={() => setActiveTab('challenges')}
        >
          Challenges ({challenges.length})
        </button>
        <button
          className={activeTab === 'contests' ? 'active' : ''}
          onClick={() => setActiveTab('contests')}
        >
          Contests ({contests.length})
        </button>
      </div>

      {activeTab === 'challenges' && (
        <div className="challenges-section">
          {pendingChallenges.length > 0 && (
            <div className="section">
              <h2>Pending Challenges (You Received)</h2>
              <div className="challenges-list">
                {pendingChallenges.map((challenge) => (
                  <ChallengeCard
                    key={challenge.id}
                    challenge={challenge}
                    onUpdate={fetchData}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="section">
            <h2>All Challenges</h2>
            {challenges.length === 0 ? (
              <p className="empty-state">No challenges yet. Create one to get started!</p>
            ) : (
              <div className="challenges-list">
                {challenges.map((challenge) => (
                  <ChallengeCard
                    key={challenge.id}
                    challenge={challenge}
                    onUpdate={fetchData}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'contests' && (
        <div className="contests-section">
          {contests.length === 0 ? (
            <p className="empty-state">No contests yet. Accept a challenge to start a contest!</p>
          ) : (
            <div className="contests-list">
              {contests.map((contest) => (
                <div key={contest.id} className="contest-card">
                  <h3>
                    {contest.user1_handle} vs {contest.user2_handle}
                  </h3>
                  <p>Difficulty: {contest.difficulty}</p>
                  <p>Status: {contest.status}</p>
                  <p>
                    Start: {formatLocalDateTime(contest.start_time)}
                  </p>
                  <Link to={`/contests/${contest.id}`} className="btn-view">
                    View Contest
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
