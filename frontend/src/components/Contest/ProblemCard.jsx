import { formatLocalDateTime } from '../../utils/dateUtils';
import './ProblemCard.css';

const ProblemCard = ({ problem }) => {
  const isSolved = problem.solved_by !== null;

  return (
    <div className={`problem-card ${isSolved ? 'solved' : ''}`}>
      <div className="problem-header">
        <h3>
          Problem {problem.problem_index} - {problem.points} points
        </h3>
        {isSolved && <span className="solved-badge">SOLVED</span>}
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
        <p className="solved-time">
          Solved at: {formatLocalDateTime(problem.solved_at)}
        </p>
      )}
    </div>
  );
};

export default ProblemCard;
