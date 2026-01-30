import { useState, useEffect, useRef, useCallback } from 'react';
import apiClient from '../../api/client';
import './UserSearch.css';

const UserSearch = ({ onSelect, selectedUser }) => {
  const [query, setQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [error, setError] = useState('');
  const dropdownRef = useRef(null);

  const searchUsers = useCallback(async (searchQuery) => {
    if (searchQuery.length < 1) {
      setUsers([]);
      setShowDropdown(false);
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await apiClient.get('/api/users/search', {
        params: { q: searchQuery },
      });
      setUsers(response.data || []);
      setShowDropdown(true);
    } catch (err) {
      console.error('Error searching users:', err);
      setError(err.response?.data?.detail || 'Failed to search users');
      setUsers([]);
      setShowDropdown(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchUsers(query);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, searchUsers]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (user) => {
    setQuery(user.handle);
    setShowDropdown(false);
    onSelect(user);
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    if (selectedUser) {
      onSelect(null);
    }
    if (value.length >= 1) {
      // Don't hide dropdown immediately, let the search handle it
    } else {
      setShowDropdown(false);
      setUsers([]);
    }
  };

  const handleInputFocus = () => {
    if (users.length > 0 && query.length >= 1) {
      setShowDropdown(true);
    }
  };

  return (
    <div className="user-search" ref={dropdownRef}>
      <input
        type="text"
        value={selectedUser ? selectedUser.handle : query}
        onChange={handleInputChange}
        onFocus={handleInputFocus}
        placeholder="Type to search for a user by handle..."
        className="user-search-input"
        autoComplete="off"
      />
      {error && <div className="search-error">{error}</div>}
      {loading && (
        <div className="search-loading">Searching...</div>
      )}
      {showDropdown && !loading && (
        <div className="user-dropdown">
          {users.length === 0 ? (
            <div className="dropdown-item no-results">
              {query.length >= 1 ? 'No users found' : 'Start typing to search...'}
            </div>
          ) : (
            users.map((user) => (
              <div
                key={user.id}
                className="dropdown-item"
                onClick={() => handleSelect(user)}
                onMouseDown={(e) => e.preventDefault()} // Prevent input blur
              >
                {user.handle}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default UserSearch;
