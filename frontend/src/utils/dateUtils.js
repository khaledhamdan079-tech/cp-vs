/**
 * Utility functions for date/time handling
 * Converts UTC times from backend to local time for display
 */

/**
 * Convert UTC date string to local Date object
 * @param {string} utcDateString - ISO date string from backend (UTC)
 * @returns {Date} - Local Date object
 */
export const utcToLocal = (utcDateString) => {
  if (!utcDateString) return null;
  // If the string doesn't have timezone info, assume it's UTC
  const dateStr = utcDateString.endsWith('Z') || utcDateString.includes('+') || utcDateString.includes('-', 10)
    ? utcDateString
    : utcDateString + 'Z';
  return new Date(dateStr);
};

/**
 * Format date to local string with timezone
 * @param {string} utcDateString - ISO date string from backend (UTC)
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted local time string
 */
export const formatLocalDateTime = (utcDateString, options = {}) => {
  if (!utcDateString) return 'N/A';
  const date = utcToLocal(utcDateString);
  if (!date || isNaN(date.getTime())) return 'Invalid Date';
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
    timeZoneName: 'short',
    ...options
  };
  
  return date.toLocaleString(undefined, defaultOptions);
};

/**
 * Format date to local string (date only)
 * @param {string} utcDateString - ISO date string from backend (UTC)
 * @returns {string} - Formatted local date string
 */
export const formatLocalDate = (utcDateString) => {
  return formatLocalDateTime(utcDateString, {
    hour: undefined,
    minute: undefined,
    hour12: undefined,
    timeZoneName: undefined
  });
};

/**
 * Format date to local string (time only)
 * @param {string} utcDateString - ISO date string from backend (UTC)
 * @returns {string} - Formatted local time string
 */
export const formatLocalTime = (utcDateString) => {
  return formatLocalDateTime(utcDateString, {
    year: undefined,
    month: undefined,
    day: undefined,
    timeZoneName: 'short'
  });
};

/**
 * Get time remaining between now and end time
 * @param {string} endTimeUtc - ISO date string for end time (UTC)
 * @returns {object} - Object with hours, minutes, seconds, and formatted string
 */
export const getTimeRemaining = (endTimeUtc) => {
  if (!endTimeUtc) return { hours: 0, minutes: 0, seconds: 0, formatted: '0s' };
  
  const endTime = utcToLocal(endTimeUtc);
  const now = new Date();
  const remainingMs = Math.max(0, endTime - now);
  
  const hours = Math.floor(remainingMs / (1000 * 60 * 60));
  const minutes = Math.floor((remainingMs % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((remainingMs % (1000 * 60)) / 1000);
  
  let formatted = '';
  if (hours > 0) {
    formatted = `${hours}h ${minutes}m ${seconds}s`;
  } else if (minutes > 0) {
    formatted = `${minutes}m ${seconds}s`;
  } else {
    formatted = `${seconds}s`;
  }
  
  return { hours, minutes, seconds, formatted, remainingMs };
};
