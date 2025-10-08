#!/usr/bin/env python3
"""
Quick seeder script to add sample data for testing.
Run this once to populate the database with sample assignments.
"""

from app.database.database import SessionLocal, init_db
from app.database.models import Assignment
from datetime import datetime, timedelta, timezone

def seed_sample_data():
    """Add sample assignments to the database for testing."""
    init_db()
    db = SessionLocal()
    
    try:
        # Add a few sample assignments
        sample_assignments = [
            Assignment(
                id=1001, 
                course_id=1, 
                course_name="AP Calculus", 
                title="Homework 1: Limits and Continuity",
                due_at_utc=datetime.now(timezone.utc) + timedelta(hours=12), 
                url="https://example.com/calc-hw1"
            ),
            Assignment(
                id=1002, 
                course_id=2, 
                course_name="AP Physics", 
                title="Lab Report: Projectile Motion",
                due_at_utc=datetime.now(timezone.utc) + timedelta(hours=36), 
                url="https://example.com/physics-lab1"
            ),
            Assignment(
                id=1003, 
                course_id=3, 
                course_name="English Literature", 
                title="Essay: Analysis of 'The Great Gatsby'",
                due_at_utc=datetime.now(timezone.utc) + timedelta(days=3), 
                url="https://example.com/english-essay1"
            ),
        ]
        
        for assignment in sample_assignments:
            db.add(assignment)
        
        db.commit()
        print(f"✅ Added {len(sample_assignments)} sample assignments to the database")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
