from uuid import uuid4
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from config import Config

# Create engine and Base for standalone use
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base = declarative_base()

# Session factory for standalone scripts (outside of Flask)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    votes = relationship('Vote', backref='voter', lazy=True)

class ThemeWeek(Base):
    __tablename__ = 'theme_weeks'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    result_url = Column(String(500), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    image_url = Column(String(500), nullable=False)
    
    videos = relationship('Video', backref='theme_week', lazy=True)

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    youtube_url = Column(String(500), nullable=False)
    description = Column(Text)
    student_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    theme_week_id = Column(String(36), ForeignKey('theme_weeks.id'), nullable=False)
    
    votes = relationship('Vote', backref='video', lazy=True)

class Vote(Base):
    __tablename__ = 'votes'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (UniqueConstraint('user_id', 'video_id', name='unique_vote'),)

class Material(Base):
    __tablename__ = 'materials'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    student_name = Column(String(100), nullable=False)
    material_type = Column(String(20), nullable=False)  # 'youtube', 'image', 'pdf', 'video', etc.
    url = Column(String(500), nullable=False)  # ссылка на Cloudinary или YouTube
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    theme_week_id = Column(String(36), ForeignKey('theme_weeks.id'), nullable=False)
    theme_week = relationship('ThemeWeek', backref='materials')

# Create all tables in the database
Base.metadata.create_all(engine) 