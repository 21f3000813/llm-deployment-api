#!/usr/bin/env python3
"""
Initialize the database for the LLM deployment evaluation system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_models import init_database

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("\nDatabase setup complete!")
    print("Tables created: tasks, repos, results")
