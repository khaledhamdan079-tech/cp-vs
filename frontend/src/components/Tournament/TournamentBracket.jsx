import { Link } from 'react-router-dom';
import { formatLocalDateTime } from '../../utils/dateUtils';
import './TournamentBracket.css';

const TournamentBracket = ({ tournament }) => {
  if (!tournament.matches || tournament.matches.length === 0) {
    return <div className="no-matches">Tournament hasn't started yet.</div>;
  }

  // Group matches by round
  const matchesByRound = {};
  tournament.matches.forEach(match => {
    if (!matchesByRound[match.round_number]) {
      matchesByRound[match.round_number] = [];
    }
    matchesByRound[match.round_number].push(match);
  });

  const rounds = Object.keys(matchesByRound).sort((a, b) => parseInt(a) - parseInt(b));

  return (
    <div className="tournament-bracket">
      <h2>Tournament Bracket</h2>
      <div className="bracket-container">
        {rounds.map(roundNum => (
          <div key={roundNum} className="bracket-round">
            <h3>Round {roundNum}</h3>
            <div className="matches-list">
              {matchesByRound[roundNum].map(match => (
                <div key={match.id} className="match-card">
                  <div className="match-players">
                    <div className={`player ${match.winner_id === match.user1_id ? 'winner' : ''}`}>
                      {match.user1_handle}
                    </div>
                    <div className="vs">vs</div>
                    <div className={`player ${match.winner_id === match.user2_id ? 'winner' : ''}`}>
                      {match.user2_handle}
                    </div>
                  </div>
                  <div className="match-info">
                    <p>Status: {match.status}</p>
                    {match.start_time && (
                      <p>Start: {formatLocalDateTime(match.start_time)}</p>
                    )}
                    {match.winner_handle && (
                      <p className="winner-info">Winner: {match.winner_handle}</p>
                    )}
                    {match.contest_id && (
                      <Link to={`/contests/${match.contest_id}`} className="view-contest-link">
                        View Contest
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TournamentBracket;
