from flask import Blueprint, request, jsonify, abort
from models import SessionLocal, ThemeWeek, User, Video, Material
import jwt
from config import Config
from functools import wraps
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

admin_bp = Blueprint('admin', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Токен отсутствует'}), 401
            
        try:
            # Удалить префикс 'Bearer ', если он есть
            if token.startswith('Bearer '):
                token = token[7:]
                
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            if not data['is_admin']:
                return jsonify({'error': 'Требуется доступ администратора'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Срок действия токена истек'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Недействительный токен'}), 401
            
        return f(*args, **kwargs)
    return decorated

# ============ USERS CRUD ============

@admin_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'is_admin': u.is_admin,
            'created_at': u.created_at.isoformat()
        } for u in users]), 200
    finally:
        session.close()

@admin_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        user = User(
            username=data['username'],
            password_hash=data['password'],
            is_admin=data.get('is_admin', False)
        )
        
        session.add(user)
        session.commit()
        return jsonify({'message': 'Пользователь успешно создан', 'id': user.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/users/<string:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
            
        return jsonify({
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        }), 200
    finally:
        session.close()

@admin_bp.route('/users/<string:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    session = SessionLocal()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
            
        data = request.get_json()
        
        user.username = data.get('username', user.username)
        user.is_admin = data.get('is_admin', user.is_admin)
        
        if 'password' in data:
            user.password_hash = data['password']
        
        session.commit()
        return jsonify({'message': 'Пользователь успешно обновлен'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/users/<string:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    session = SessionLocal()
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
            
        session.delete(user)
        session.commit()
        return jsonify({'message': 'Пользователь успешно удален'}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 400
    finally:
        session.close()

# ============ THEME WEEKS CRUD ============

@admin_bp.route('/theme-weeks', methods=['GET'])
@token_required
def get_theme_weeks():
    session = SessionLocal()
    try:
        weeks = session.query(ThemeWeek).all()
        return jsonify([{
            'id': w.id,
            'title': w.title,
            'description': w.description,
            'start_date': w.start_date.isoformat(),
            'end_date': w.end_date.isoformat(),
            'result_url': w.result_url,
            'image_url': w.image_url
        } for w in weeks]), 200
    finally:
        session.close()

@admin_bp.route('/theme-weeks', methods=['POST'])
@token_required
def create_theme_week():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        theme_week = ThemeWeek(
            title=data['title'],
            description=data.get('description'),
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            result_url=data.get('result_url', ''),
            image_url=data.get('image_url', '')
        )
        
        session.add(theme_week)
        session.commit()
        return jsonify({'message': 'Тематическая неделя успешно создана', 'id': theme_week.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/theme-weeks/<string:week_id>', methods=['GET'])
@token_required
def get_theme_week(week_id):
    session = SessionLocal()
    try:
        week = session.query(ThemeWeek).filter_by(id=week_id).first()
        if not week:
            return jsonify({'error': 'Тематическая неделя не найдена'}), 404
            
        return jsonify({
            'id': week.id,
            'title': week.title,
            'description': week.description,
            'start_date': week.start_date.isoformat(),
            'end_date': week.end_date.isoformat(),
            'result_url': week.result_url,
            'image_url': week.image_url
        }), 200
    finally:
        session.close()

@admin_bp.route('/theme-weeks/<string:week_id>', methods=['PUT'])
@token_required
def update_theme_week(week_id):
    session = SessionLocal()
    
    try:
        week = session.query(ThemeWeek).filter_by(id=week_id).first()
        if not week:
            return jsonify({'error': 'Тематическая неделя не найдена'}), 404
            
        data = request.get_json()
        
        week.title = data.get('title', week.title)
        week.description = data.get('description', week.description)
        week.start_date = datetime.fromisoformat(data['start_date']) if 'start_date' in data else week.start_date
        week.end_date = datetime.fromisoformat(data['end_date']) if 'end_date' in data else week.end_date
        week.result_url = data.get('result_url', week.result_url)
        week.image_url = data.get('image_url', week.image_url)
        
        session.commit()
        return jsonify({'message': 'Тематическая неделя успешно обновлена'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/theme-weeks/<string:week_id>', methods=['DELETE'])
@token_required
def delete_theme_week(week_id):
    session = SessionLocal()
    
    try:
        week = session.query(ThemeWeek).filter_by(id=week_id).first()
        if not week:
            return jsonify({'error': 'Тематическая неделя не найдена'}), 404
            
        session.delete(week)
        session.commit()
        return jsonify({'message': 'Тематическая неделя успешно удалена'}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 400
    finally:
        session.close()

# ============ VIDEOS CRUD ============

@admin_bp.route('/videos', methods=['GET'])
@token_required
def get_videos():
    session = SessionLocal()
    try:
        videos = session.query(Video).all()
        return jsonify([{
            'id': v.id,
            'title': v.title,
            'youtube_url': v.youtube_url,
            'description': v.description,
            'student_name': v.student_name,
            'theme_week_id': v.theme_week_id,
            'created_at': v.created_at.isoformat()
        } for v in videos]), 200
    finally:
        session.close()

@admin_bp.route('/videos', methods=['POST'])
@token_required
def create_video():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        video = Video(
            title=data['title'],
            youtube_url=data['youtube_url'],
            description=data.get('description'),
            student_name=data['student_name'],
            theme_week_id=data['theme_week_id']
        )
        
        session.add(video)
        session.commit()
        return jsonify({'message': 'Видео успешно создано', 'id': video.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/videos/<string:video_id>', methods=['GET'])
@token_required
def get_video(video_id):
    session = SessionLocal()
    try:
        video = session.query(Video).filter_by(id=video_id).first()
        if not video:
            return jsonify({'error': 'Видео не найдено'}), 404
            
        return jsonify({
            'id': video.id,
            'title': video.title,
            'youtube_url': video.youtube_url,
            'description': video.description,
            'student_name': video.student_name,
            'theme_week_id': video.theme_week_id,
            'created_at': video.created_at.isoformat()
        }), 200
    finally:
        session.close()

@admin_bp.route('/videos/<string:video_id>', methods=['PUT'])
@token_required
def update_video(video_id):
    session = SessionLocal()
    
    try:
        video = session.query(Video).filter_by(id=video_id).first()
        if not video:
            return jsonify({'error': 'Видео не найдено'}), 404
            
        data = request.get_json()
        
        video.title = data.get('title', video.title)
        video.youtube_url = data.get('youtube_url', video.youtube_url)
        video.description = data.get('description', video.description)
        video.student_name = data.get('student_name', video.student_name)
        video.theme_week_id = data.get('theme_week_id', video.theme_week_id)
        
        session.commit()
        return jsonify({'message': 'Видео успешно обновлено'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/videos/<string:video_id>', methods=['DELETE'])
@token_required
def delete_video(video_id):
    session = SessionLocal()
    
    try:
        video = session.query(Video).filter_by(id=video_id).first()
        if not video:
            return jsonify({'error': 'Видео не найдено'}), 404
            
        session.delete(video)
        session.commit()
        return jsonify({'message': 'Видео успешно удалено'}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 400
    finally:
        session.close()

# ============ MATERIALS CRUD ============

@admin_bp.route('/materials', methods=['GET'])
@token_required
def get_materials():
    session = SessionLocal()
    try:
        materials = session.query(Material).all()
        return jsonify([{
            'id': m.id,
            'title': m.title,
            'description': m.description,
            'student_name': m.student_name,
            'material_type': m.material_type,
            'url': m.url,
            'is_winner': m.is_winner,
            'theme_week_id': m.theme_week_id,
            'created_at': m.created_at.isoformat()
        } for m in materials]), 200
    finally:
        session.close()

@admin_bp.route('/materials', methods=['POST'])
@token_required
def create_material():
    data = request.get_json()
    session = SessionLocal()
    
    try:
        material = Material(
            title=data['title'],
            description=data.get('description'),
            student_name=data['student_name'],
            material_type=data['material_type'],
            url=data['url'],
            is_winner=data.get('is_winner', False),
            theme_week_id=data['theme_week_id']
        )
        
        session.add(material)
        session.commit()
        return jsonify({'message': 'Материал успешно создан', 'id': material.id}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/materials/<string:material_id>', methods=['GET'])
@token_required
def get_material(material_id):
    session = SessionLocal()
    try:
        material = session.query(Material).filter_by(id=material_id).first()
        if not material:
            return jsonify({'error': 'Материал не найден'}), 404
            
        return jsonify({
            'id': material.id,
            'title': material.title,
            'description': material.description,
            'student_name': material.student_name,
            'material_type': material.material_type,
            'url': material.url,
            'is_winner': material.is_winner,
            'theme_week_id': material.theme_week_id,
            'created_at': material.created_at.isoformat()
        }), 200
    finally:
        session.close()

@admin_bp.route('/materials/<string:material_id>', methods=['PUT'])
@token_required
def update_material(material_id):
    session = SessionLocal()
    
    try:
        material = session.query(Material).filter_by(id=material_id).first()
        if not material:
            return jsonify({'error': 'Материал не найден'}), 404
            
        data = request.get_json()
        
        material.title = data.get('title', material.title)
        material.description = data.get('description', material.description)
        material.student_name = data.get('student_name', material.student_name)
        material.material_type = data.get('material_type', material.material_type)
        material.url = data.get('url', material.url)
        material.is_winner = data.get('is_winner', material.is_winner)
        material.theme_week_id = data.get('theme_week_id', material.theme_week_id)
        
        session.commit()
        return jsonify({'message': 'Материал успешно обновлен'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        session.close()

@admin_bp.route('/materials/<string:material_id>', methods=['DELETE'])
@token_required
def delete_material(material_id):
    session = SessionLocal()
    
    try:
        material = session.query(Material).filter_by(id=material_id).first()
        if not material:
            return jsonify({'error': 'Материал не найден'}), 404
            
        session.delete(material)
        session.commit()
        return jsonify({'message': 'Материал успешно удален'}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': f'Ошибка при удалении: {str(e)}'}), 400
    finally:
        session.close()