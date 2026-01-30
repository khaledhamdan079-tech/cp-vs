# Profile Page Debugging Guide

## Issue: Completely White Page

If the profile page is showing a completely white screen, follow these steps:

### Step 1: Check Browser Console

1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Look for:
   - `=== UserProfile component rendered ===` - Should appear when page loads
   - `Fetching profile for handle: ...` - Should appear when API call starts
   - `Profile data received: ...` - Should show the API response
   - Any red error messages

### Step 2: Check Network Tab

1. Go to **Network** tab in DevTools
2. Refresh the profile page
3. Look for:
   - Request to `/api/users/{handle}/profile`
   - Check the response status (200 = success, 404/500 = error)
   - Click on the request to see response data

### Step 3: Verify Route is Working

1. Check the URL - should be `/users/{handle}` (e.g., `/users/tourist`)
2. Try visiting: `http://localhost:5173/users/test` (or your Railway URL)
3. You should see console logs even if the page is white

### Step 4: Test with Simple Component

Temporarily replace the UserProfile component with a simple test:

```jsx
// In App.jsx, temporarily change:
import UserProfile from './components/Profile/UserProfile.test';

// This will show a simple test page to verify routing works
```

### Common Issues and Fixes

#### Issue: Component Not Rendering
**Symptoms**: No console logs, completely white
**Fix**: Check if route is correct in App.jsx

#### Issue: API Error
**Symptoms**: Console shows error, page shows error message
**Fix**: Check backend logs, verify endpoint exists

#### Issue: CSS Hiding Content
**Symptoms**: Console shows data, but page is white
**Fix**: Check if CSS has `display: none` or `opacity: 0`

#### Issue: JavaScript Error
**Symptoms**: Red error in console
**Fix**: Check error message and fix the issue

### Quick Test

Add this at the very top of UserProfile component:

```jsx
// Add this right after the component declaration
console.log('PROFILE COMPONENT LOADED');
alert('Profile component loaded!'); // Remove after testing
```

If you see the alert, the component is loading. If not, it's a routing issue.

### Next Steps

After checking console and network:
1. Share the console errors (if any)
2. Share the network request/response
3. Check if other pages work (homepage, leaderboard)
4. Verify the backend endpoint is working: `GET /api/users/{handle}/profile`
