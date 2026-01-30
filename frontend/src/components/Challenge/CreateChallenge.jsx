import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';
import UserSearch from './UserSearch';
import './CreateChallenge.css';

const CreateChallenge = () => {
  const [selectedUser, setSelectedUser] = useState(null);
  const [difficulty, setDifficulty] = useState(2);
  const [startTime, setStartTime] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!selectedUser) {
      setError('Please select a user to challenge');
      return;
    }

    if (!startTime) {
      setError('Please select a start time');
      return;
    }

    setLoading(true);

    try {
      await apiClient.post('/api/challenges/', {
        challenged_user_id: selectedUser.id,
        difficulty: parseInt(difficulty),
        suggested_start_time: new Date(startTime).toISOString(),
      });
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create challenge');
    } finally {
      setLoading(false);
    }
  };

  // Set default start time to 1 hour from now
  const getDefaultStartTime = () => {
    const date = new Date();
    date.setHours(date.getHours() + 1);
    date.setMinutes(0);
    date.setSeconds(0);
    return date.toISOString().slice(0, 16);
  };

  return (
    <div className="create-challenge">
      <h1>Create Challenge</h1>
      <form onSubmit={handleSubmit} className="challenge-form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Select User to Challenge</label>
          <UserSearch onSelect={setSelectedUser} selectedUser={selectedUser} />
          {selectedUser && (
            <p className="selected-user">Selected: {selectedUser.handle}</p>
          )}
        </div>

        <div className="form-group">
          <label>Difficulty (Division)</label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            required
          >
            <option value={1}>Difficulty 1 (Div 4)</option>
            <option value={2}>Difficulty 2 (Div 3)</option>
            <option value={3}>Difficulty 3 (Div 2)</option>
            <option value={4}>Difficulty 4 (Div 1)</option>
          </select>
        </div>

        <div className="form-group">
          <label>Suggested Start Time</label>
          <input
            type="datetime-local"
            value={startTime || getDefaultStartTime()}
            onChange={(e) => setStartTime(e.target.value)}
            required
            min={new Date().toISOString().slice(0, 16)}
          />
        </div>

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Creating Challenge...' : 'Create Challenge'}
        </button>
      </form>
    </div>
  );
};

export default CreateChallenge;
