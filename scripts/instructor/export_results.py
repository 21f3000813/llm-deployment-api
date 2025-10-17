#!/usr/bin/env python3
"""
Export evaluation results to CSV
"""

import sys
import os
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Result, Repo


def export_results(output_file='results.csv'):
    """Export all results to CSV"""
    
    session = get_session()
    
    # Get all results
    results = session.query(Result).order_by(Result.timestamp).all()
    
    if not results:
        print("No results found to export")
        return
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'timestamp',
            'email',
            'task',
            'round',
            'repo_url',
            'commit_sha',
            'pages_url',
            'check',
            'score',
            'reason',
            'logs'
        ])
        
        # Data
        for result in results:
            writer.writerow([
                result.timestamp.isoformat(),
                result.email,
                result.task,
                result.round,
                result.repo_url,
                result.commit_sha,
                result.pages_url,
                result.check,
                result.score,
                result.reason,
                result.logs[:500] if result.logs else ''
            ])
    
    print(f"✓ Exported {len(results)} results to {output_file}")
    
    # Generate summary
    export_summary(session, 'summary.csv')


def export_summary(session, output_file='summary.csv'):
    """Export summary with average scores per student"""
    
    # Get unique students
    repos = session.query(Repo).all()
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'email',
            'task',
            'round',
            'repo_url',
            'pages_url',
            'total_checks',
            'average_score',
            'passed_checks',
            'failed_checks'
        ])
        
        # Data
        for repo in repos:
            results = session.query(Result).filter_by(
                email=repo.email,
                task=repo.task,
                round=repo.round
            ).all()
            
            if not results:
                continue
            
            total_checks = len(results)
            avg_score = sum(r.score for r in results) / total_checks
            passed = sum(1 for r in results if r.score >= 0.7)
            failed = total_checks - passed
            
            writer.writerow([
                repo.email,
                repo.task,
                repo.round,
                repo.repo_url,
                repo.pages_url,
                total_checks,
                f"{avg_score:.2f}",
                passed,
                failed
            ])
    
    print(f"✓ Exported summary to {output_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Export evaluation results')
    parser.add_argument('--output', default='results.csv', help='Output CSV file')
    
    args = parser.parse_args()
    
    export_results(args.output)
