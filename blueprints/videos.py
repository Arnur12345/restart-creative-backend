from flask import Blueprint, request, jsonify
from models import SessionLocal, Video, Vote
import jwt
from config import Config
from functools import wraps
from datetime import datetime

videos_bp = Blueprint('videos', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
                
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated

@videos_bp.route('/', methods=['GET'])
def get_videos():
    session = SessionLocal()
    
    try:
        theme_week_id = request.args.get('theme_week_id')
        query = session.query(Video)
        
        if theme_week_id:
            query = query.filter_by(theme_week_id=theme_week_id)
        
        videos = query.all()
        return jsonify([{
            'id': video.id,
            'title': video.title,
            'youtube_url': video.youtube_url,
            'description': video.description,
            'author': video.author.username,
            'theme_week_id': video.theme_week_id,
            'votes_count': len(video.votes),
            'created_at': video.created_at.isoformat()
        } for video in videos]), 200
    finally:
        session.close()

@videos_bp.route('/', methods=['POST'])
@token_required
def create_video():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        video = Video(
            title=data['title'],
            youtube_url=data['youtube_url'],
            description=data.get('description'),
            user_id=request.user_id,
            theme_week_id=data['theme_week_id']
        )
        
        session.add(video)
        session.commit()
        return jsonify({'message': 'Video created successfully'}), 201
    finally:
        session.close()

@videos_bp.route('/<video_id>/vote', methods=['POST'])
@token_required
def vote_video(video_id):
    session = SessionLocal()
    
    try:
        # Проверяем, не голосовал ли уже пользователь
        existing_vote = session.query(Vote).filter_by(
            user_id=request.user_id,
            video_id=video_id
        ).first()
        
        if existing_vote:
            return jsonify({'error': 'You have already voted for this video'}), 400
        
        vote = Vote(
            user_id=request.user_id,
            video_id=video_id
        )
        
        session.add(vote)
        session.commit()
        return jsonify({'message': 'Vote recorded successfully'}), 201
    finally:
        session.close() 