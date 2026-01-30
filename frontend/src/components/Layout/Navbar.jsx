import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  useEffect(() => {
    if (user) {
      fetchPendingCount();
      // Poll every 30 seconds for updates
      const interval = setInterval(fetchPendingCount, 30000);
      return () => clearInterval(interval);
    } else {
      setPendingCount(0);
    }
  }, [user]);

  const fetchPendingCount = async () => {
    if (!user) return;
    try {
      const response = await apiClient.get('/api/challenges/pending-count');
      setPendingCount(response.data.count || 0);
    } catch (error) {
      console.error('Error fetching pending challenges count:', error);
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand" onClick={closeMobileMenu}>
          CP VS
        </Link>
        <button 
          className={`mobile-menu-toggle ${mobileMenuOpen ? 'active' : ''}`}
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <div className={`navbar-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link to="/" onClick={closeMobileMenu}>Home</Link>
          <Link to="/leaderboard" onClick={closeMobileMenu}>Leaderboard</Link>
          {user ? (
            <>
              <Link to="/dashboard" onClick={closeMobileMenu} className="navbar-link-with-badge">
                Dashboard
                {pendingCount > 0 && (
                  <span className="pending-badge">{pendingCount}</span>
                )}
              </Link>
              <Link to="/challenges/create" onClick={closeMobileMenu}>Create Challenge</Link>
              <Link to={`/users/${user.handle}`} className="navbar-profile-link" onClick={closeMobileMenu}>
                My Profile
              </Link>
              <span className="navbar-user">Hello, {user.handle}</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={closeMobileMenu}>Login</Link>
              <Link to="/register" onClick={closeMobileMenu}>Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
