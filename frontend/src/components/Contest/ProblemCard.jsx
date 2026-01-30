import { formatLocalDateTime } from '../../utils/dateUtils';
import './ProblemCard.css';

const ProblemCard = ({ problem, currentUserId, user1Id, user2Id }) => {
  const isSolved = problem.solved_by !== null;
  const isSolvedByOpponent = isSolved && problem.solved_by !== currentUserId;
  const isSolvedByMe = isSolved && problem.solved_by === currentUserId;

  return (
    <div className={`problem-card ${isSolvedByMe ? 'solved' : ''} ${isSolvedByOpponent ? 'solved-by-opponent' : ''}`}>
      <div className="problem-header">
        <h3>
          Problem {problem.problem_index} - {problem.points} points
        </h3>
        {isSolved && (
          <span className={`solved-badge ${isSolvedByOpponent ? 'opponent' : ''}`}>
            {isSolvedByOpponent ? 'SOLVED BY OPPONENT' : 'SOLVED'}
          </span>
        )}
      </div>
      {problem.problem_url ? (
        <a
          href={problem.problem_url}
          target="_blank"
          rel="noopener noreferrer"
          className="problem-link"
        >
          Open on Codeforces
        </a>
      ) : (
        <p className="problem-code">{problem.problem_code}</p>
      )}
      {isSolved && problem.solved_at && (
        <p className={`solved-time ${isSolvedByOpponent ? 'opponent' : ''}`}>
          Solved at: {formatLocalDateTime(problem.solved_at)}
        </p>
      )}
    </div>
  );
};

export default ProblemCard;
