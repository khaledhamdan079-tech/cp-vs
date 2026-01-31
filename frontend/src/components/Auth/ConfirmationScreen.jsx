import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../api/client';
import './Auth.css';
import './ConfirmationScreen.css';

const ConfirmationScreen = ({ registrationData }) => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [error, setError] = useState('');
  const [checking, setChecking] = useState(true);
  
  const problemLink = registrationData?.problem_link || 'https://codeforces.com/problemset/problem/4/A';
  const deadline = registrationData?.deadline ? new Date(registrationData.deadline) : null;

  useEffect(() => {
    if (!deadline) return;

    const checkStatus = async () => {
      try {
        const response = await apiClient.get('/api/auth/confirmation-status');
        const data = response.data;
        
        setIsConfirmed(data.is_confirmed);
        
        if (data.is_confirmed) {
          setChecking(false);
          setIsConfirmed(true);
          // Redirect to login with success message after showing success state
          setTimeout(() => {
            navigate('/login', { 
              state: { message: 'Account confirmed successfully! Please log in with your credentials.' } 
            });
          }, 3000);
          return;
        }

        if (data.time_remaining !== null) {
          setTimeRemaining(data.time_remaining);
        } else if (data.deadline) {
          const deadlineDate = new Date(data.deadline);
          const remaining = Math.max(0, Math.floor((deadlineDate - new Date()) / 1000));
          setTimeRemaining(remaining);
        }
      } catch (err) {
        console.error('Error checking confirmation status:', err);
        if (err.response?.status === 401) {
          // Token expired or invalid, redirect to login
          navigate('/login', { 
            state: { message: 'Please log in to check your confirmation status.' } 
          });
        }
      }
    };

    // Check immediately
    checkStatus();

    // Poll every 5 seconds
    const interval = setInterval(checkStatus, 5000);

    // Update countdown every second
    const countdownInterval = setInterval(() => {
      if (deadline && !isConfirmed) {
        const remaining = Math.max(0, Math.floor((deadline - new Date()) / 1000));
        setTimeRemaining(remaining);
        
        if (remaining === 0) {
          setError('Confirmation deadline has passed. Please try registering again.');
          setChecking(false);
        }
      }
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(countdownInterval);
    };
  }, [deadline, isConfirmed, navigate]);

  const formatTime = (seconds) => {
    if (seconds === null || seconds === undefined) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (isConfirmed) {
    return (
      <div className="auth-container">
        <div className="auth-card confirmation-card">
          <div className="success-message">
            <h2>✓ Account Confirmed!</h2>
            <p>Your account has been successfully confirmed. Redirecting to login...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card confirmation-card">
        <h2>Confirm Your Account</h2>
        <div className="confirmation-instructions">
          <p>
            To confirm your account ownership, please submit <strong>any solution</strong> to the 
            Watermelon problem (4A) on Codeforces.
          </p>
          <p className="time-limit">
            You have <strong>{formatTime(timeRemaining)}</strong> remaining to complete this step.
          </p>
        </div>

        <a
          href={problemLink}
          target="_blank"
          rel="noopener noreferrer"
          className="btn-problem-link"
        >
          Open Watermelon Problem on Codeforces
        </a>

        {checking && (
          <div className="checking-status">
            <p>Checking for your submission...</p>
            <div className="spinner"></div>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}

        <div className="confirmation-help">
          <p>After submitting, this page will automatically detect your submission and confirm your account.</p>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationScreen;
