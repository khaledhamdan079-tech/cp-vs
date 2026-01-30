import './Leaderboard.css';

const Leaderboard = ({ scores }) => {
  // Sort by points descending
  const sortedScores = [...scores].sort((a, b) => b.total_points - a.total_points);

  return (
    <div className="leaderboard">
      <h2>Leaderboard</h2>
      <div className="leaderboard-list">
        {sortedScores.map((score, index) => (
          <div
            key={score.user_id}
            className={`leaderboard-item ${index === 0 ? 'winner' : ''}`}
          >
            <div className="rank">#{index + 1}</div>
            <div className="user-info">
              <div className="handle">{score.user_handle}</div>
            </div>
            <div className="points">{score.total_points} pts</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Leaderboard;
