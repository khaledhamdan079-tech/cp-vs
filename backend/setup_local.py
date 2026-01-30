"""
Setup script for local development.
This script helps set up the local environment.
"""
import os
import sys

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"[OK] {env_file} already exists")
        return
    
    if not os.path.exists(env_example):
        print(f"[ERROR] {env_example} not found")
        return
    
    # Read example
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Update with local defaults
    content = content.replace(
        "DATABASE_URL=postgresql://user:password@localhost:5432/cpvs_db",
        "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cpvs_db"
    )
    content = content.replace(
        "JWT_SECRET_KEY=your-secret-key-change-this-in-production",
        "JWT_SECRET_KEY=dev-secret-key-change-in-production-" + os.urandom(16).hex()
    )
    
    # Write .env
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"[OK] Created {env_file} from {env_example}")
    print("  Please update DATABASE_URL with your PostgreSQL credentials")

if __name__ == "__main__":
    print("Setting up local development environment...")
    create_env_file()
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the server: uvicorn app.main:app --reload")
    print("3. Database will be created automatically (SQLite)")
    print("\nNote: For production/Railway, use PostgreSQL instead of SQLite")
