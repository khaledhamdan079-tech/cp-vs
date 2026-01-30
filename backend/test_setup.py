"""
Quick test script to verify the setup is working.
Run this after setting up the environment.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from app.config import settings
        print("[OK] Config imported")
        
        from app.database import engine, Base
        print("[OK] Database imported")
        
        from app.models import User, Challenge, Contest
        print("[OK] Models imported")
        
        from app.auth import verify_password, get_password_hash
        print("[OK] Auth imported")
        
        from app.codeforces_api import cf_api
        print("[OK] Codeforces API imported")
        
        from app.routers import auth, users, challenges, contests
        print("[OK] Routers imported")
        
        print("\n[OK] All imports successful!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Import error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[OK] Database connection successful!")
            
            # Check database type
            from app.config import settings
            if settings.database_url.startswith("sqlite"):
                print("  Using SQLite (local database file)")
            else:
                print("  Using PostgreSQL")
            
            return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        db_url = ""
        try:
            from app.config import settings
            db_url = settings.database_url
        except:
            pass
        
        if db_url.startswith("sqlite"):
            print("  SQLite should work automatically. Check file permissions.")
        else:
            print("  Make sure PostgreSQL is running and DATABASE_URL is correct in .env")
        return False

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from app.config import settings
        
        if not settings.database_url:
            print("[ERROR] DATABASE_URL not set")
            return False
        
        if not settings.jwt_secret_key:
            print("[ERROR] JWT_SECRET_KEY not set")
            return False
        
        print("[OK] Configuration looks good!")
        return True
    except Exception as e:
        print(f"[ERROR] Configuration error: {e}")
        print("  Make sure .env file exists and has all required variables")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("CP VS Backend Setup Test")
    print("=" * 50)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database_connection()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n[OK] All tests passed! You're ready to run the server.")
        print("  Run: uvicorn app.main:app --reload")
    else:
        print("\n[ERROR] Some tests failed. Please fix the issues above.")
        sys.exit(1)
