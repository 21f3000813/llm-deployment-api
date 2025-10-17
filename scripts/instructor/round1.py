#!/usr/bin/env python3
"""
Round 1: Send initial task requests to students
"""

import sys
import os
import csv
import requests
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Task
from task_generator import TaskGenerator
from dotenv import load_dotenv

load_dotenv()


def send_round1_tasks(submissions_csv: str, templates_path: str):
    """Send Round 1 tasks to all students"""
    
    session = get_session()
    generator = TaskGenerator(templates_path)
    evaluation_url = os.getenv('EVALUATION_URL', 'http://localhost:8000/api/notify')
    
    # Get available templates
    template_ids = generator.get_available_templates()
    print(f"Available templates: {', '.join(template_ids)}")
    
    # Read submissions
    with open(submissions_csv, 'r') as f:
        reader = csv.DictReader(f)
        submissions = list(reader)
    
    print(f"\nProcessing {len(submissions)} submissions...\n")
    
    for i, submission in enumerate(submissions, 1):
        email = submission['email']
        endpoint = submission['endpoint']
        secret = submission['secret']
        
        print(f"[{i}/{len(submissions)}] Processing {email}")
        
        # Check if already sent Round 1
        existing = session.query(Task).filter_by(
            email=email,
            round=1
        ).filter(Task.statuscode == 200).first()
        
        if existing:
            print(f"  ⊘ Skipping - Round 1 already sent successfully")
            continue
        
        try:
            # Pick a random template (or cycle through them)
            template_id = template_ids[i % len(template_ids)]
            
            # Generate task
            task_data = generator.generate_task(template_id, email, round_num=1)
            nonce = str(uuid.uuid4())
            
            # Build request payload
            payload = {
                'email': email,
                'secret': secret,
                'task': task_data['task_id'],
                'round': 1,
                'nonce': nonce,
                'brief': task_data['brief'],
                'checks': task_data['checks'],
                'evaluation_url': evaluation_url,
                'attachments': task_data['attachments']
            }
            
            print(f"  → Task: {task_data['task_id']}")
            print(f"  → Endpoint: {endpoint}")
            
            # Send POST request
            response = requests.post(
                endpoint,
                json=payload,
                timeout=30
            )
            
            status_code = response.status_code
            print(f"  ✓ Response: HTTP {status_code}")
            
            # Log to database
            task = Task(
                email=email,
                task=task_data['task_id'],
                round=1,
                nonce=nonce,
                brief=task_data['brief'],
                attachments=task_data['attachments'],
                checks=task_data['checks'],
                evaluation_url=evaluation_url,
                endpoint=endpoint,
                statuscode=status_code,
                secret=secret
            )
            session.add(task)
            session.commit()
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            
            # Log failed attempt
            task = Task(
                email=email,
                task=task_data.get('task_id', 'unknown'),
                round=1,
                nonce=nonce,
                brief=task_data.get('brief', ''),
                attachments=task_data.get('attachments', []),
                checks=task_data.get('checks', []),
                evaluation_url=evaluation_url,
                endpoint=endpoint,
                statuscode=0,
                secret=secret
            )
            session.add(task)
            session.commit()
    
    print("\n=== Round 1 Complete ===")
    
    # Summary
    total = session.query(Task).filter_by(round=1).count()
    successful = session.query(Task).filter_by(round=1).filter(Task.statuscode == 200).count()
    failed = total - successful
    
    print(f"Total sent: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Send Round 1 tasks to students')
    parser.add_argument('--submissions', default='submissions.csv',
                       help='Path to submissions CSV file')
    parser.add_argument('--templates', default='../../config/task_templates.json',
                       help='Path to task templates JSON file')
    
    args = parser.parse_args()
    
    # Check if files exist
    if not os.path.exists(args.submissions):
        print(f"Error: Submissions file not found: {args.submissions}")
        print("\nCreate a submissions.csv with format:")
        print("timestamp,email,endpoint,secret")
        sys.exit(1)
    
    templates_path = os.path.join(os.path.dirname(__file__), args.templates)
    if not os.path.exists(templates_path):
        print(f"Error: Templates file not found: {templates_path}")
        sys.exit(1)
    
    send_round1_tasks(args.submissions, templates_path)
