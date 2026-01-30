# Database Migration Fix

## Problem
The error `column users.rating does not exist` occurs because the database was created before we added the `rating` field to the User model.

## Solution

### Automatic Migration (Recommended)
The migration will run automatically on the next deployment. The `migrations.py` script will:
1. Check if `rating` column exists in `users` table
2. Add it if missing (with default value 1000)
3. Create `rating_history` table if it doesn't exist

**Just redeploy** - the migration runs automatically on startup.

### Manual Migration (If Needed)

If automatic migration doesn't work, you can run it manually:

#### Option 1: Via Railway CLI (if installed)
```bash
railway run python backend/run_migration.py
```

#### Option 2: Via Railway Dashboard
1. Go to Railway → Backend service
2. Click "Deployments" → Latest deployment
3. Click "View Logs" → "Shell" (if available)
4. Run: `python backend/run_migration.py`

#### Option 3: Direct SQL (Quick Fix)
Go to Railway → PostgreSQL database → "Query" tab and run:

```sql
-- Add rating column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'rating'
    ) THEN
        ALTER TABLE users ADD COLUMN rating INTEGER NOT NULL DEFAULT 1000;
    END IF;
END $$;

-- Create rating_history table if it doesn't exist
CREATE TABLE IF NOT EXISTS rating_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id),
    contest_id VARCHAR(36) NOT NULL REFERENCES contests(id),
    rating_before INTEGER NOT NULL,
    rating_after INTEGER NOT NULL,
    rating_change INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Verification

After migration, verify it worked:

1. **Check backend logs** - Should see:
   ```
   ✓ Added 'rating' column with default value 1000
   ✓ Created 'rating_history' table
   ```

2. **Test login** - Should work without errors

3. **Check database** - Query users table:
   ```sql
   SELECT handle, rating FROM users LIMIT 5;
   ```
   All users should have `rating = 1000`

## Next Steps

1. **Commit and push the migration code**:
   ```bash
   git add backend/app/migrations.py backend/app/main.py backend/run_migration.py
   git commit -m "Add database migration for rating column"
   git push origin main
   ```

2. **Railway will redeploy** - Migration runs automatically

3. **Verify** - Check logs and test login

## Troubleshooting

### Migration still fails
- Check Railway logs for specific error
- Verify PostgreSQL connection is working
- Try manual SQL migration (Option 3 above)

### Users still don't have rating
- Check if column was added: `SELECT column_name FROM information_schema.columns WHERE table_name = 'users';`
- Update existing users: `UPDATE users SET rating = 1000 WHERE rating IS NULL;`

### Rating history table missing
- Check if table exists: `SELECT table_name FROM information_schema.tables WHERE table_name = 'rating_history';`
- Create manually using SQL from Option 3 above
