import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../../api/client';
import './CreateTournament.css';

const CreateTournament = () => {
  const [numParticipants, setNumParticipants] = useState(8);
  const [difficulty, setDifficulty] = useState(2);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    setLoading(true);

    try {
      const response = await apiClient.post('/api/tournaments/', {
        num_participants: parseInt(numParticipants),
        difficulty: parseInt(difficulty),
      });
      navigate(`/tournaments/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-tournament">
      <h1>Create Tournament</h1>
      <form onSubmit={handleSubmit} className="tournament-form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Number of Participants</label>
          <select
            value={numParticipants}
            onChange={(e) => setNumParticipants(e.target.value)}
            required
          >
            <option value={4}>4</option>
            <option value={8}>8</option>
            <option value={16}>16</option>
            <option value={32}>32</option>
            <option value={64}>64</option>
          </select>
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

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Creating Tournament...' : 'Create Tournament'}
        </button>
      </form>
    </div>
  );
};

export default CreateTournament;
