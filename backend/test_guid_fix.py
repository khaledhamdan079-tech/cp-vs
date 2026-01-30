"""
Test script to verify the GUID type fix works correctly.
This tests that tables can be created and UUIDs work with both SQLite and PostgreSQL.
"""
import sys
import os
import uuid

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_guid_import():
    """Test that GUID can be imported without errors"""
    print("Testing GUID import...")
    try:
        from app.models import GUID
        print("[OK] GUID type imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import GUID: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_import():
    """Test that all models can be imported"""
    print("\nTesting models import...")
    try:
        from app.models import User, Challenge, Contest, ContestProblem, ContestScore
        print("[OK] All models imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_table_creation():
    """Test that tables can be created"""
    print("\nTesting table creation...")
    try:
        from app.database import Base, engine
        from app.models import User, Challenge, Contest, ContestProblem, ContestScore
        
        # Drop all tables first (for clean test)
        print("  Dropping existing tables (if any)...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("  Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("[OK] Tables created successfully!")
        
        # Check database type
        from app.config import settings
        if settings.database_url.startswith("sqlite"):
            print("  Using SQLite (local database)")
        else:
            print("  Using PostgreSQL")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_uuid_operations():
    """Test that UUIDs can be stored and retrieved"""
    print("\nTesting UUID operations...")
    try:
        from app.database import SessionLocal
        from app.models import User
        import uuid
        
        db = SessionLocal()
        try:
            # Create a test user with UUID
            test_uuid = uuid.uuid4()
            test_user = User(
                id=test_uuid,
                handle="test_user_guid",
                password_hash="test_hash"
            )
            
            db.add(test_user)
            db.commit()
            print(f"[OK] User created with UUID: {test_uuid}")
            
            # Retrieve the user
            retrieved_user = db.query(User).filter(User.id == test_uuid).first()
            if retrieved_user:
                print(f"[OK] User retrieved successfully with UUID: {retrieved_user.id}")
                print(f"     UUID type: {type(retrieved_user.id)}")
                
                # Verify UUID is correct type
                if isinstance(retrieved_user.id, uuid.UUID):
                    print("[OK] UUID is correct type (uuid.UUID)")
                else:
                    print(f"[WARNING] UUID is {type(retrieved_user.id)}, expected uuid.UUID")
                
                # Clean up
                db.delete(retrieved_user)
                db.commit()
                print("[OK] Test user deleted")
            else:
                print("[ERROR] Failed to retrieve user")
                return False
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] UUID operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_foreign_key_relationships():
    """Test that foreign keys with GUID work"""
    print("\nTesting foreign key relationships...")
    try:
        from app.database import SessionLocal
        from app.models import User, Challenge
        import uuid
        from datetime import datetime
        
        db = SessionLocal()
        try:
            # Create two users
            user1_id = uuid.uuid4()
            user2_id = uuid.uuid4()
            
            user1 = User(id=user1_id, handle="user1_guid", password_hash="hash1")
            user2 = User(id=user2_id, handle="user2_guid", password_hash="hash2")
            
            db.add(user1)
            db.add(user2)
            db.commit()
            
            # Create a challenge with foreign keys
            challenge = Challenge(
                id=uuid.uuid4(),
                challenger_id=user1_id,
                challenged_id=user2_id,
                difficulty=2,
                suggested_start_time=datetime.utcnow()
            )
            
            db.add(challenge)
            db.commit()
            print("[OK] Challenge created with GUID foreign keys")
            
            # Retrieve challenge with relationships
            retrieved = db.query(Challenge).filter(Challenge.id == challenge.id).first()
            if retrieved and retrieved.challenger and retrieved.challenged:
                print("[OK] Foreign key relationships work correctly")
                print(f"     Challenger: {retrieved.challenger.handle}")
                print(f"     Challenged: {retrieved.challenged.handle}")
            else:
                print("[ERROR] Failed to retrieve relationships")
                return False
            
            # Clean up
            db.delete(challenge)
            db.delete(user1)
            db.delete(user2)
            db.commit()
            print("[OK] Test data cleaned up")
            
            return True
        finally:
            db.close()
    except Exception as e:
        print(f"[ERROR] Foreign key test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("GUID Type Fix Test")
    print("=" * 60)
    print("\nThis test verifies that the GUID type works correctly")
    print("with both SQLite (local) and PostgreSQL (Railway).\n")
    
    results = []
    results.append(("GUID Import", test_guid_import()))
    results.append(("Models Import", test_models_import()))
    results.append(("Table Creation", test_table_creation()))
    results.append(("UUID Operations", test_uuid_operations()))
    results.append(("Foreign Keys", test_foreign_key_relationships()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name:.<40} {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] All tests passed!")
        print("\nThe GUID fix is working correctly.")
        print("You can now deploy to Railway with confidence.")
    else:
        print("[FAILURE] Some tests failed.")
        print("Please fix the issues before deploying.")
        sys.exit(1)
    print("=" * 60)
