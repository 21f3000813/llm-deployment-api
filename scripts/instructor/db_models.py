from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Task(Base):
    """Tasks sent to students"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False)
    task = Column(String, nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String, nullable=False, unique=True)
    brief = Column(Text, nullable=False)
    attachments = Column(JSON)  # List of {name, url}
    checks = Column(JSON)  # List of check strings
    evaluation_url = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    statuscode = Column(Integer)
    secret = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Task {self.task} Round {self.round} - {self.email}>"


class Repo(Base):
    """Repositories submitted by students"""
    __tablename__ = 'repos'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False)
    task = Column(String, nullable=False)
    round = Column(Integer, nullable=False)
    nonce = Column(String, nullable=False)
    repo_url = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    pages_url = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Repo {self.repo_url} - {self.task}>"


class Result(Base):
    """Evaluation results"""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    email = Column(String, nullable=False)
    task = Column(String, nullable=False)
    round = Column(Integer, nullable=False)
    repo_url = Column(String, nullable=False)
    commit_sha = Column(String, nullable=False)
    pages_url = Column(String, nullable=False)
    check = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(Text)
    logs = Column(Text)
    
    def __repr__(self):
        return f"<Result {self.check} - {self.score} - {self.task}>"


# Database connection
def get_engine():
    database_url = os.getenv('DATABASE_URL', 'sqlite:///llm_deployment.db')
    return create_engine(database_url, echo=False)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✓ Database initialized successfully")


if __name__ == '__main__':
    init_database()
