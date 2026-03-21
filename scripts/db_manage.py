# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

"""Database initialization and management script."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, init_db
from app.models.database import User, Goal, Task, MoodEntry, Session, FinanceAccount, Transaction, PushToken, Subscription
import uuid
import hashlib
from datetime import datetime, timedelta


def create_tables():
    """Create all database tables."""
    print("📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def create_demo_admin():
    """Create demo admin user."""
    from sqlalchemy.orm import Session as DbSession
    from app.database import SessionLocal
    from app.models.database import User, UserRole, SubscriptionTier
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@busybee.app").first()
        if admin:
            print("ℹ️  Admin user already exists")
            return admin
        
        # Create admin
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@busybee.app",
            full_name="Admin",
            password_hash=hashlib.sha256("admin123".encode()).hexdigest(),
            role=UserRole.ADMIN,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"✅ Admin user created: {admin.email}")
        print(f"   Password: admin123")
        return admin
    finally:
        db.close()


def create_demo_user():
    """Create demo regular user."""
    from sqlalchemy.orm import Session as DbSession
    from app.database import SessionLocal
    from app.models.database import User, UserRole, SubscriptionTier
    
    db = SessionLocal()
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == "demo@busybee.app").first()
        if user:
            print("ℹ️  Demo user already exists")
            return user
        
        # Create demo user
        user = User(
            id=str(uuid.uuid4()),
            email="demo@busybee.app",
            full_name="Demo User",
            password_hash=hashlib.sha256("demo123".encode()).hexdigest(),
            role=UserRole.USER,
            subscription_tier=SubscriptionTier.PRO,
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create demo goals
        goals = [
            Goal(id=str(uuid.uuid4()), user_id=user.id, title="Learn Python", description="Master Python programming", progress=65, status="active", category="career"),
            Goal(id=str(uuid.uuid4()), user_id=user.id, title="Save $10,000", description="Build emergency fund", progress=40, status="active", category="finance"),
            Goal(id=str(uuid.uuid4()), user_id=user.id, title="Exercise 3x/week", description="Stay fit and healthy", progress=80, status="active", category="health"),
        ]
        for goal in goals:
            db.add(goal)
        
        # Create demo tasks
        tasks = [
            Task(id=str(uuid.uuid4()), user_id=user.id, title="Review project documentation", priority="high", is_completed=False),
            Task(id=str(uuid.uuid4()), user_id=user.id, title="Call with team", priority="medium", is_completed=True),
            Task(id=str(uuid.uuid4()), user_id=user.id, title="Send weekly report", priority="low", is_completed=False),
        ]
        for task in tasks:
            db.add(task)
        
        # Create demo mood entries
        moods = [
            MoodEntry(id=str(uuid.uuid4()), user_id=user.id, mood="good", note="Great day!", created_at=datetime.utcnow()),
            MoodEntry(id=str(uuid.uuid4()), user_id=user.id, mood="great", note="Finished big project!", created_at=datetime.utcnow() - timedelta(days=1)),
        ]
        for mood in moods:
            db.add(mood)
        
        db.commit()
        print(f"✅ Demo user created: {user.email}")
        print(f"   Password: demo123")
        return user
    finally:
        db.close()


def list_users():
    """List all users in database."""
    from app.database import SessionLocal
    from app.models.database import User
    
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"\n👥 Users in database: {len(users)}")
        for user in users:
            print(f"   - {user.email} ({user.role.value})")
    finally:
        db.close()


def reset_database():
    """Drop and recreate all tables."""
    print("⚠️  Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Database reset complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management")
    parser.add_argument("command", choices=["init", "create-admin", "create-demo", "list", "reset"])
    args = parser.parse_args()
    
    if args.command == "init":
        create_tables()
    elif args.command == "create-admin":
        create_tables()
        create_demo_admin()
    elif args.command == "create-demo":
        create_tables()
        create_demo_user()
    elif args.command == "list":
        list_users()
    elif args.command == "reset":
        reset_database()
