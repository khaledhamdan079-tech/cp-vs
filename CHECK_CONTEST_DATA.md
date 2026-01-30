# How to Check Contest Data Locally

There are several ways to check what's in your created contests:

## Method 1: Using the Python Script (Easiest)

I've created a script that shows all contest data:

```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"
.\venv\Scripts\Activate.ps1
python check_contests.py
```

This will show:
- All users in the database
- All contests with their details
- Problems assigned to each contest
- Scores for each contest
- Challenge information

## Method 2: Using the API Endpoints

### Via Browser/Postman

1. **Get all contests** (requires authentication):
   ```
   GET http://localhost:8000/api/contests/
   ```
   Add header: `Authorization: Bearer <your_token>`

2. **Get specific contest**:
   ```
   GET http://localhost:8000/api/contests/{contest_id}
   ```

3. **Get contest problems**:
   ```
   GET http://localhost:8000/api/contests/{contest_id}/problems
   ```

### Via FastAPI Docs (Easiest API method)

1. Start your backend server
2. Go to: http://localhost:8000/docs
3. Click "Authorize" button
4. Enter your JWT token: `Bearer <your_token>`
5. Use the `/api/contests/` endpoints to explore

## Method 3: Direct Database Access (SQLite)

### Using SQLite Command Line

```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"
sqlite3 cpvs.db
```

Then run SQL queries:

```sql
-- See all contests
SELECT * FROM contests;

-- See contest problems
SELECT * FROM contest_problems;

-- See contest scores
SELECT * FROM contest_scores;

-- See all users
SELECT id, handle, created_at FROM users;

-- Get contest with user handles
SELECT 
    c.id,
    u1.handle as user1,
    u2.handle as user2,
    c.difficulty,
    c.status,
    c.start_time
FROM contests c
JOIN users u1 ON c.user1_id = u1.id
JOIN users u2 ON c.user2_id = u2.id;

-- Get problems for a specific contest (replace CONTEST_ID)
SELECT 
    problem_index,
    problem_code,
    problem_url,
    points,
    solved_by
FROM contest_problems
WHERE contest_id = 'CONTEST_ID';

-- Exit SQLite
.quit
```

### Using a SQLite GUI Tool

You can use tools like:
- **DB Browser for SQLite** (free): https://sqlitebrowser.org/
- **SQLiteStudio** (free): https://sqlitestudio.pl/
- **VS Code Extension**: SQLite Viewer

Open the database file: `backend/cpvs.db`

## Method 4: Via Frontend

1. Log in to the application
2. Go to Dashboard
3. Click on "Contests" tab
4. Click "View Contest" on any contest
5. You'll see:
   - Contest details
   - Problems (if contest has started)
   - Leaderboard with scores

## Quick Check Script

Run this to see a summary:

```powershell
cd "C:\Users\khaled\Desktop\projects\CP VS\backend"
.\venv\Scripts\Activate.ps1
python check_contests.py
```

## Example Output

```
================================================================================
CP VS Database Checker
================================================================================

USERS:
================================================================================
Users in database: 2
================================================================================
  testuser1 (ID: abc123...) - Created: 2024-01-30 10:00:00
  testuser2 (ID: def456...) - Created: 2024-01-30 10:05:00

CONTESTS:
================================================================================
Found 1 contest(s)
================================================================================

Contest #1
--------------------------------------------------------------------------------
ID: xyz789...
Users: testuser1 vs testuser2
Difficulty: 2
Status: scheduled
Start Time: 2024-01-30 11:00:00
End Time: 2024-01-30 13:00:00
Created: 2024-01-30 10:10:00

Problems (6):
  A: 1234A - 100 pts
    URL: https://codeforces.com/problemset/problem/1234/A
    Status: Not solved yet
  B: 5678B - 200 pts
    URL: https://codeforces.com/problemset/problem/5678/B
    Status: Not solved yet
  ...

Scores:
  testuser1: 0 points
  testuser2: 0 points

Challenge Info:
  Challenger: testuser1
  Challenged: testuser2
  Challenge Status: accepted
```

## Troubleshooting

**Script doesn't work:**
- Make sure virtual environment is activated
- Make sure backend server has been started at least once (creates database)

**No contests shown:**
- Make sure you've created and accepted a challenge
- Check if the challenge was accepted (creates the contest)

**Database file not found:**
- The database is created automatically when you first start the backend
- Location: `backend/cpvs.db`
