#!/usr/bin/env python3
"""
Main evaluation script: Run all checks on submitted repos
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Task, Repo, Result
from static_checks import (
    check_license, 
    check_readme_exists, 
    check_repo_created_after_task,
    check_no_secrets_in_history,
    get_file_content
)
from dynamic_checks import run_dynamic_checks, check_page_accessibility, check_page_performance
from llm_checks import evaluate_readme_quality, evaluate_code_quality, check_code_completeness


def evaluate_all_repos():
    """Evaluate all submitted repositories"""
    
    session = get_session()
    
    # Get all repos that haven't been fully evaluated
    repos = session.query(Repo).all()
    
    print(f"Evaluating {len(repos)} repositories...\n")
    
    for i, repo in enumerate(repos, 1):
        print(f"[{i}/{len(repos)}] Evaluating {repo.email} - {repo.task} (Round {repo.round})")
        print(f"  Repo: {repo.repo_url}")
        print(f"  Pages: {repo.pages_url}")
        
        # Check if already evaluated
        existing_results = session.query(Result).filter_by(
            email=repo.email,
            task=repo.task,
            round=repo.round,
            repo_url=repo.repo_url
        ).count()
        
        if existing_results > 5:  # If we have multiple results, skip
            print(f"  ⊘ Already evaluated\n")
            continue
        
        # Get the original task
        task = session.query(Task).filter_by(
            email=repo.email,
            task=repo.task,
            round=repo.round
        ).first()
        
        if not task:
            print(f"  ✗ Task not found\n")
            continue
        
        # Run all checks
        results = []
        
        # 1. Static Checks
        print("  → Running static checks...")
        
        # Check LICENSE
        score, reason, logs = check_license(repo.repo_url, repo.commit_sha)
        results.append({
            'check': 'license_mit',
            'score': score,
            'reason': reason,
            'logs': logs
        })
        print(f"    LICENSE: {score} - {reason}")
        
        # Check README exists
        score, reason, readme_content = check_readme_exists(repo.repo_url, repo.commit_sha)
        results.append({
            'check': 'readme_exists',
            'score': score,
            'reason': reason,
            'logs': readme_content[:500]
        })
        print(f"    README exists: {score} - {reason}")
        
        # Check repo creation time
        score, reason, logs = check_repo_created_after_task(repo.repo_url, task.timestamp)
        results.append({
            'check': 'repo_timing',
            'score': score,
            'reason': reason,
            'logs': logs
        })
        print(f"    Repo timing: {score} - {reason}")
        
        # Check for secrets
        score, reason, logs = check_no_secrets_in_history(repo.repo_url)
        results.append({
            'check': 'no_secrets',
            'score': score,
            'reason': reason,
            'logs': logs
        })
        print(f"    No secrets: {score} - {reason}")
        
        # 2. LLM-based Static Checks
        print("  → Running LLM checks...")
        
        # README quality
        if readme_content:
            score, reason, logs = evaluate_readme_quality(readme_content)
            results.append({
                'check': 'readme_quality',
                'score': score,
                'reason': reason,
                'logs': logs
            })
            print(f"    README quality: {score} - {reason}")
        
        # Code quality
        code_content = get_file_content(repo.repo_url, repo.commit_sha, 'index.html')
        if code_content:
            score, reason, logs = evaluate_code_quality(code_content, 'html')
            results.append({
                'check': 'code_quality',
                'score': score,
                'reason': reason,
                'logs': logs
            })
            print(f"    Code quality: {score} - {reason}")
            
            # Requirements completeness
            score, reason, logs = check_code_completeness(code_content, task.brief)
            results.append({
                'check': 'requirements_met',
                'score': score,
                'reason': reason,
                'logs': logs
            })
            print(f"    Requirements: {score} - {reason}")
        
        # 3. Dynamic Checks (Playwright)
        print("  → Running dynamic checks...")
        
        try:
            dynamic_results = run_dynamic_checks(repo.pages_url, task.checks)
            results.extend(dynamic_results)
            
            for dr in dynamic_results:
                print(f"    {dr['check']}: {dr['score']} - {dr['reason']}")
        except Exception as e:
            print(f"    ✗ Dynamic checks failed: {e}")
            results.append({
                'check': 'dynamic_error',
                'score': 0.0,
                'reason': f'Dynamic checks failed: {str(e)}',
                'logs': str(e)
            })
        
        # 4. Save results to database
        print("  → Saving results...")
        
        for result in results:
            db_result = Result(
                email=repo.email,
                task=repo.task,
                round=repo.round,
                repo_url=repo.repo_url,
                commit_sha=repo.commit_sha,
                pages_url=repo.pages_url,
                check=result['check'],
                score=result['score'],
                reason=result.get('reason', ''),
                logs=result.get('logs', '')
            )
            session.add(db_result)
        
        session.commit()
        
        # Calculate overall score
        total_score = sum(r['score'] for r in results) / len(results) if results else 0
        print(f"  ✓ Overall Score: {total_score:.2f}\n")
    
    print("=== Evaluation Complete ===")
    
    # Summary
    total_repos = session.query(Repo).count()
    evaluated_repos = session.query(Result).distinct(Result.repo_url).count()
    
    print(f"Total repositories: {total_repos}")
    print(f"Evaluated: {evaluated_repos}")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║  LLM Deployment Evaluation System                        ║
║  Running all checks...                                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    evaluate_all_repos()
