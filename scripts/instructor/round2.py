#!/usr/bin/env python3
"""
Round 2: Send revision tasks to students who completed Round 1
"""

import sys
import os
import requests
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Task, Repo
from task_generator import TaskGenerator
from dotenv import load_dotenv

load_dotenv()


def send_round2_tasks(templates_path: str):
    """Send Round 2 tasks to students who submitted Round 1"""
    
    session = get_session()
    generator = TaskGenerator(templates_path)
    evaluation_url = os.getenv('EVALUATION_URL', 'http://localhost:8000/api/notify')
    
    # Get all Round 1 repos
    repos = session.query(Repo).filter_by(round=1).all()
    
    print(f"Processing {len(repos)} Round 1 submissions for Round 2...\n")
    
    for i, repo in enumerate(repos, 1):
        email = repo.email
        print(f"[{i}/{len(repos)}] Processing {email}")
        
        # Check if Round 2 already sent
        existing = session.query(Task).filter_by(
            email=email,
            round=2
        ).first()
        
        if existing:
            print(f"  ⊘ Skipping - Round 2 already sent")
            continue
        
        try:
            # Get original Round 1 task
            round1_task = session.query(Task).filter_by(
                email=email,
                task=repo.task,
                round=1
            ).first()
            
            if not round1_task:
                print(f"  ✗ Round 1 task not found")
                continue
            
            # Extract template ID from task
            template_id = repo.task.split('-')[0] + '-' + repo.task.split('-')[1] + '-' + repo.task.split('-')[2]
            # Simple extraction: take first part before version hash
            template_parts = repo.task.split('-')
            if len(template_parts) >= 2:
                # Reconstruct template ID (e.g., "sum-of-sales" from "sum-of-sales-a1b2c")
                template_id = '-'.join(template_parts[:-1])
            else:
                template_id = template_parts[0]
            
            print(f"  → Template: {template_id}")
            
            # Generate Round 2 task
            task_data = generator.generate_task(template_id, email, round_num=2)
            nonce = str(uuid.uuid4())
            
            # Build request payload
            payload = {
                'email': email,
                'secret': round1_task.secret,
                'task': task_data['task_id'],
                'round': 2,
                'nonce': nonce,
                'brief': task_data['brief'],
                'checks': task_data['checks'],
                'evaluation_url': evaluation_url,
                'attachments': task_data['attachments']
            }
            
            print(f"  → Task: {task_data['task_id']}")
            print(f"  → Endpoint: {round1_task.endpoint}")
            
            # Send POST request
            response = requests.post(
                round1_task.endpoint,
                json=payload,
                timeout=30
            )
            
            status_code = response.status_code
            print(f"  ✓ Response: HTTP {status_code}")
            
            # Log to database
            task = Task(
                email=email,
                task=task_data['task_id'],
                round=2,
                nonce=nonce,
                brief=task_data['brief'],
                attachments=task_data['attachments'],
                checks=task_data['checks'],
                evaluation_url=evaluation_url,
                endpoint=round1_task.endpoint,
                statuscode=status_code,
                secret=round1_task.secret
            )
            session.add(task)
            session.commit()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n=== Round 2 Complete ===")
    
    # Summary
    total = session.query(Task).filter_by(round=2).count()
    successful = session.query(Task).filter_by(round=2).filter(Task.statuscode == 200).count()
    failed = total - successful
    
    print(f"Total sent: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Send Round 2 tasks to students')
    parser.add_argument('--templates', default='../../config/task_templates.json',
                       help='Path to task templates JSON file')
    
    args = parser.parse_args()
    
    templates_path = os.path.join(os.path.dirname(__file__), args.templates)
    if not os.path.exists(templates_path):
        print(f"Error: Templates file not found: {templates_path}")
        sys.exit(1)
    
    send_round2_tasks(templates_path)
