#!/usr/bin/env python3
"""
Evaluation API: Accept student submissions
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import get_session, Task, Repo
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LLM Deployment Evaluation API")


class SubmissionRequest(BaseModel):
    email: str
    task: str
    round: int
    nonce: str
    repo_url: HttpUrl
    commit_sha: str
    pages_url: HttpUrl


@app.get("/")
async def root():
    return {
        "service": "LLM Deployment Evaluation API",
        "version": "1.0.0",
        "endpoints": ["/api/notify", "/health"]
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/notify")
async def notify_submission(submission: SubmissionRequest):
    """
    Accept student submission and queue for evaluation
    """
    session = get_session()
    
    try:
        # Validate submission against tasks table
        task = session.query(Task).filter_by(
            email=submission.email,
            task=submission.task,
            round=submission.round,
            nonce=submission.nonce
        ).first()
        
        if not task:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Invalid submission",
                    "reason": "No matching task found. Check email, task, round, and nonce."
                }
            )
        
        # Check if already submitted
        existing = session.query(Repo).filter_by(
            email=submission.email,
            task=submission.task,
            round=submission.round,
            nonce=submission.nonce
        ).first()
        
        if existing:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Duplicate submission",
                    "reason": "This task has already been submitted."
                }
            )
        
        # Store submission
        repo = Repo(
            email=submission.email,
            task=submission.task,
            round=submission.round,
            nonce=submission.nonce,
            repo_url=str(submission.repo_url),
            commit_sha=submission.commit_sha,
            pages_url=str(submission.pages_url)
        )
        
        session.add(repo)
        session.commit()
        
        print(f"✓ Submission received: {submission.email} - {submission.task} (Round {submission.round})")
        
        return {
            "status": "success",
            "message": "Submission queued for evaluation",
            "task": submission.task,
            "round": submission.round
        }
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error processing submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


@app.get("/api/stats")
async def get_stats():
    """Get submission statistics"""
    session = get_session()
    
    try:
        tasks_sent = session.query(Task).count()
        repos_submitted = session.query(Repo).count()
        
        round1_tasks = session.query(Task).filter_by(round=1).count()
        round2_tasks = session.query(Task).filter_by(round=2).count()
        
        round1_repos = session.query(Repo).filter_by(round=1).count()
        round2_repos = session.query(Repo).filter_by(round=2).count()
        
        return {
            "tasks_sent": tasks_sent,
            "repos_submitted": repos_submitted,
            "round1": {
                "tasks_sent": round1_tasks,
                "repos_submitted": round1_repos
            },
            "round2": {
                "tasks_sent": round2_tasks,
                "repos_submitted": round2_repos
            }
        }
    finally:
        session.close()


if __name__ == '__main__':
    port = int(os.getenv('EVALUATION_API_PORT', 8000))
    
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  LLM Deployment Evaluation API                           ║
║  Port: {port}                                             ║
║  Endpoint: http://localhost:{port}/api/notify             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=port)
