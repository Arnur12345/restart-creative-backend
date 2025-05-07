from flask import Blueprint, request, jsonify, abort
from models import SessionLocal, ThemeWeek, Material
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

theme_weeks_bp = Blueprint('theme_weeks', __name__)

@theme_weeks_bp.route('/', methods=['GET'])
def get_theme_weeks():
    session = SessionLocal()
    
    try:
        theme_weeks = session.query(ThemeWeek).all()
        return jsonify([{
            'id': week.id,
            'title': week.title,
            'description': week.description,
            'start_date': week.start_date.isoformat(),
            'end_date': week.end_date.isoformat(),
            'videos_count': len(week.videos),
            'result_url': week.result_url,
            'image_url': week.image_url
        } for week in theme_weeks]), 200
    finally:
        session.close()

@theme_weeks_bp.route('/<week_id>', methods=['GET'])
def get_theme_week(week_id):
    session = SessionLocal()
    
    try:
        week = session.query(ThemeWeek).filter(ThemeWeek.id == week_id).first()
        if not week:
            abort(404)
        return jsonify({
            'id': week.id,
            'title': week.title,
            'description': week.description,
            'start_date': week.start_date.isoformat(),
            'end_date': week.end_date.isoformat(),
            'result_url': week.result_url,
            'image_url': week.image_url,
            'videos': [{
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'youtube_url': video.youtube_url,
                'student_name': video.student_name,
                'theme_week_id': video.theme_week_id,
                'created_at': video.created_at.isoformat()
            } for video in week.videos]
        }), 200
    finally:
        session.close()

@theme_weeks_bp.route('/materials', methods=['GET'])
def get_all_materials():
    session = SessionLocal()
    try:
        materials = session.query(Material).all()
        return jsonify([
            {
                'id': m.id,
                'title': m.title,
                'description': m.description,
                'student_name': m.student_name,
                'material_type': m.material_type,
                'url': m.url,
                'is_winner': m.is_winner,
                'theme_week_id': m.theme_week_id,
                'created_at': m.created_at.isoformat()
            } for m in materials
        ]), 200
    finally:
        session.close() 