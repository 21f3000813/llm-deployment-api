#!/usr/bin/env python3
"""
View database statistics
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Task, Repo, Result
from sqlalchemy import func


def show_stats():
    """Display database statistics"""
    
    session = get_session()
    
    print("\n" + "="*60)
    print("LLM DEPLOYMENT SYSTEM - DATABASE STATISTICS")
    print("="*60 + "\n")
    
    # Tasks
    print("📋 TASKS")
    print("-" * 60)
    total_tasks = session.query(Task).count()
    round1_tasks = session.query(Task).filter_by(round=1).count()
    round2_tasks = session.query(Task).filter_by(round=2).count()
    successful_tasks = session.query(Task).filter(Task.statuscode == 200).count()
    
    print(f"  Total tasks sent: {total_tasks}")
    print(f"  Round 1: {round1_tasks}")
    print(f"  Round 2: {round2_tasks}")
    print(f"  Successful (HTTP 200): {successful_tasks}")
    print(f"  Failed: {total_tasks - successful_tasks}\n")
    
    # Repos
    print("📦 REPOSITORIES")
    print("-" * 60)
    total_repos = session.query(Repo).count()
    round1_repos = session.query(Repo).filter_by(round=1).count()
    round2_repos = session.query(Repo).filter_by(round=2).count()
    unique_students = session.query(Repo.email).distinct().count()
    
    print(f"  Total submissions: {total_repos}")
    print(f"  Round 1: {round1_repos}")
    print(f"  Round 2: {round2_repos}")
    print(f"  Unique students: {unique_students}\n")
    
    # Results
    print("✅ EVALUATION RESULTS")
    print("-" * 60)
    total_results = session.query(Result).count()
    avg_score = session.query(func.avg(Result.score)).scalar()
    passed = session.query(Result).filter(Result.score >= 0.7).count()
    failed = session.query(Result).filter(Result.score < 0.7).count()
    
    print(f"  Total checks run: {total_results}")
    print(f"  Average score: {avg_score:.2f}" if avg_score else "  Average score: N/A")
    print(f"  Passed (≥0.7): {passed}")
    print(f"  Failed (<0.7): {failed}\n")
    
    # Top checks
    print("🏆 CHECK PERFORMANCE")
    print("-" * 60)
    check_stats = session.query(
        Result.check,
        func.count(Result.id).label('count'),
        func.avg(Result.score).label('avg_score')
    ).group_by(Result.check).order_by(func.avg(Result.score).desc()).limit(10).all()
    
    for check, count, avg in check_stats:
        print(f"  {check:25s} {count:3d} runs, avg: {avg:.2f}")
    
    print("\n" + "="*60 + "\n")
    
    # Recent submissions
    print("📅 RECENT SUBMISSIONS (Last 5)")
    print("-" * 60)
    recent = session.query(Repo).order_by(Repo.timestamp.desc()).limit(5).all()
    
    for repo in recent:
        print(f"  {repo.timestamp.strftime('%Y-%m-%d %H:%M')} | {repo.email:30s} | {repo.task}")
    
    print("\n")


if __name__ == '__main__':
    show_stats()
