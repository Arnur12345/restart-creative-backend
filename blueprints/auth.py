from flask import Blueprint, request, jsonify
from models import SessionLocal, User
import jwt
import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        if session.query(User).filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        user = User(
            username=data['username'],
            password_hash=data['password'],
            is_admin=data.get('is_admin', False)
        )
        
        session.add(user)
        session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    finally:
        session.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    if 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
        
    if 'password' not in data:
        return jsonify({'error': 'Password is required'}), 400
        
    session = SessionLocal()
    
    try:
        user = session.query(User).filter_by(username=data['username']).first()
        
        if not user or user.password_hash != data['password']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            Config.SECRET_KEY,
            algorithm="HS256"
        )
        
        return jsonify({
            'token': token,
            'username': user.username,
            'is_admin': user.is_admin
        }), 200
    finally:
        session.close()

@auth_bp.route('/me', methods=['GET'])
def me():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return jsonify({
            'user_id': data['user_id'],
            'username': data['username'],
            'is_admin': data['is_admin']
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401