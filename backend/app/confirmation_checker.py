from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal
from .models import User
from .codeforces_api import cf_api


async def check_user_confirmation(user_id: str, handle: str, registration_timestamp: datetime) -> bool:
    """
    Check if user has submitted to watermelon problem (4A) since registration.
    Returns True if submission found, False otherwise.
    """
    try:
        # Convert datetime to timestamp
        since_timestamp = int(registration_timestamp.timestamp())
        
        # Check for any submission to problem 4A (watermelon)
        submission = await cf_api.check_any_submission(handle, "4A", since_timestamp)
        
        return submission is not None
    except Exception as e:
        print(f"Error checking confirmation for user {handle}: {e}")
        return False


async def check_pending_confirmations():
    """Check all unconfirmed users for watermelon submissions and confirm them if found"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Get all unconfirmed users with active deadline
        unconfirmed_users = db.query(User).filter(
            User.is_confirmed == False,
            User.confirmation_deadline > now
        ).all()
        
        for user in unconfirmed_users:
            # Check if user has submitted to watermelon problem since registration
            has_submitted = await check_user_confirmation(
                str(user.id),
                user.handle,
                user.created_at
            )
            
            if has_submitted:
                # Confirm the user
                user.is_confirmed = True
                user.confirmation_deadline = None
                db.commit()
                print(f"User {user.handle} confirmed successfully")
        
        # Handle expired confirmations (deadline passed)
        expired_users = db.query(User).filter(
            User.is_confirmed == False,
            User.confirmation_deadline <= now
        ).all()
        
        # Optionally handle expired users (for now, we'll just leave them unconfirmed)
        # They can try to register again or we could add a retry mechanism
        
    except Exception as e:
        print(f"Error checking pending confirmations: {e}")
        db.rollback()
    finally:
        db.close()
