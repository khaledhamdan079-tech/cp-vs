// Temporary test component to verify routing works
import { useParams } from 'react-router-dom';

const UserProfileTest = () => {
  const { handle } = useParams();
  
  return (
    <div style={{ padding: '2rem', backgroundColor: '#fff', minHeight: '400px' }}>
      <h1>Profile Test Page</h1>
      <p>Handle from URL: <strong>{handle || 'NOT FOUND'}</strong></p>
      <p>If you see this, routing is working!</p>
    </div>
  );
};

export default UserProfileTest;
