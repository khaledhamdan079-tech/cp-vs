# Railway Deployment Checklist

Use this checklist to ensure everything is ready for deployment.

## Pre-Deployment

### Backend
- [ ] All code is committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` exists and is correct
- [ ] `runtime.txt` specifies Python version
- [ ] `.env.example` has all required variables
- [ ] CORS settings allow your frontend URL (or use `FRONTEND_URL` env var)
- [ ] Database migrations are handled (auto-created on startup)

### Frontend
- [ ] All code is committed to GitHub
- [ ] `package.json` has all dependencies
- [ ] `vite.config.js` is configured correctly
- [ ] `VITE_API_BASE_URL` will be set to backend URL
- [ ] Build command works locally: `npm run build`
- [ ] `serve` package is in dependencies (for Railway)

## Railway Setup

### Backend Service
- [ ] Created new Railway project
- [ ] Added GitHub repository
- [ ] Set root directory to `backend`
- [ ] Added PostgreSQL database
- [ ] Set environment variables:
  - [ ] `DATABASE_URL` (auto-set by Railway)
  - [ ] `JWT_SECRET_KEY` (strong random key)
  - [ ] `JWT_ALGORITHM=HS256`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
  - [ ] `CODEFORCES_API_URL=https://codeforces.com/api`
  - [ ] `FRONTEND_URL` (your frontend Railway URL)
- [ ] Generated domain for backend
- [ ] Verified backend is accessible
- [ ] Tested API docs at `/docs`

### Frontend Service
- [ ] Added frontend service to same project
- [ ] Set root directory to `frontend`
- [ ] Set environment variables:
  - [ ] `VITE_API_BASE_URL` (your backend Railway URL)
- [ ] Generated domain for frontend
- [ ] Verified frontend is accessible

## Post-Deployment Testing

### Backend Tests
- [ ] Health check: `GET /health`
- [ ] API docs: `GET /docs`
- [ ] Register user: `POST /api/auth/register`
- [ ] Login: `POST /api/auth/login`
- [ ] Get user: `GET /api/auth/me` (with token)
- [ ] Search users: `GET /api/users/search?q=test`

### Frontend Tests
- [ ] Page loads without errors
- [ ] Can register a user
- [ ] Can login
- [ ] Can search for users
- [ ] Can create challenge
- [ ] Can accept challenge
- [ ] Contest is created
- [ ] Problems are displayed correctly
- [ ] Times display in local timezone

### Integration Tests
- [ ] Frontend can communicate with backend
- [ ] CORS is working correctly
- [ ] Authentication works end-to-end
- [ ] Database operations work
- [ ] Codeforces API integration works

## Monitoring

- [ ] Check Railway logs for errors
- [ ] Monitor resource usage
- [ ] Set up alerts if needed
- [ ] Check database connections

## Security Checklist

- [ ] JWT secret key is strong and unique
- [ ] Database credentials are secure
- [ ] CORS is properly configured (not `*` in production)
- [ ] Environment variables are set (not hardcoded)
- [ ] `.env` files are in `.gitignore`

## Documentation

- [ ] Update README with production URLs
- [ ] Document environment variables
- [ ] Note any Railway-specific configurations

## Rollback Plan

If something goes wrong:
1. Check Railway logs
2. Verify environment variables
3. Check database connection
4. Test API endpoints individually
5. Rollback to previous deployment if needed

## Common Issues & Solutions

**Issue**: Backend won't start
- Check `Procfile` and start command
- Verify `$PORT` is used
- Check build logs for errors

**Issue**: Frontend can't connect to backend
- Verify `VITE_API_BASE_URL` is correct
- Check CORS settings
- Ensure backend is accessible

**Issue**: Database connection fails
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Verify database exists

**Issue**: Build fails
- Check build logs
- Verify all dependencies are listed
- Check for version conflicts
