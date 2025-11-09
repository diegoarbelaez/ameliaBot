#!/usr/bin/env python3
"""
Script to create the first admin user for BotDO.
Run this script after setting up the database to create your first admin account.

Usage:
    python create_admin.py

The script will prompt for username, email, and password.
"""
import sys
import os
from getpass import getpass

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

# Load environment variables
load_dotenv()

from app.database import SessionLocal
from app.models import AdminUser
from app.auth import get_password_hash


def validate_email(email: str) -> bool:
    """Simple email validation"""
    return "@" in email and "." in email.split("@")[1]


def validate_username(username: str) -> bool:
    """Validate username (alphanumeric, min 3 chars)"""
    if len(username) < 3:
        return False
    return username.replace('_', '').replace('-', '').isalnum()


def validate_password(password: str) -> bool:
    """Validate password (min 8 chars)"""
    return len(password) >= 8


def create_admin():
    """Create an admin user interactively"""
    print("=" * 50)
    print("BotDO - Create Admin User")
    print("=" * 50)
    print()
    
    # Get username
    while True:
        username = input("Enter username (min 3 characters, alphanumeric): ").strip()
        if not username:
            print("❌ Username cannot be empty")
            continue
        if not validate_username(username):
            print("❌ Username must be at least 3 characters and alphanumeric (can include _ and -)")
            continue
        break
    
    # Get email
    while True:
        email = input("Enter email address: ").strip()
        if not email:
            print("❌ Email cannot be empty")
            continue
        if not validate_email(email):
            print("❌ Invalid email format")
            continue
        break
    
    # Get password
    while True:
        password = getpass("Enter password (min 8 characters): ")
        if not password:
            print("❌ Password cannot be empty")
            continue
        if not validate_password(password):
            print("❌ Password must be at least 8 characters")
            continue
        
        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Passwords do not match")
            continue
        break
    
    print()
    print("Creating admin user...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(AdminUser).filter(
            (AdminUser.username == username) | (AdminUser.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                print(f"❌ Error: Username '{username}' already exists")
            else:
                print(f"❌ Error: Email '{email}' already exists")
            return False
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create admin user
        admin_user = AdminUser(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print()
        print("✅ Admin user created successfully!")
        print()
        print(f"   Username: {admin_user.username}")
        print(f"   Email:    {admin_user.email}")
        print(f"   ID:       {admin_user.id}")
        print()
        print("You can now login at: POST /auth/login")
        print()
        
        return True
        
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Database error: {str(e)}")
        return False
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        db.close()


def list_admins():
    """List all admin users"""
    db = SessionLocal()
    
    try:
        admins = db.query(AdminUser).all()
        
        if not admins:
            print("No admin users found.")
            return
        
        print()
        print("=" * 80)
        print(f"{'Username':<20} {'Email':<30} {'Active':<10} {'ID'}")
        print("=" * 80)
        
        for admin in admins:
            status = "✓ Active" if admin.is_active else "✗ Inactive"
            print(f"{admin.username:<20} {admin.email:<30} {status:<10} {admin.id}")
        
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        db.close()


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_admins()
        return
    
    try:
        create_admin()
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

