from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import logging
from sqlalchemy.exc import IntegrityError
from models import db, Participant, init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)

# Инициализация базы данных
with app.app_context():
    init_db()


# API Endpoints

@app.route('/api/participants', methods=['GET'])
def get_participants():
    """Получить всех участников"""
    try:
        participants = Participant.query.all()
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при получении участников: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при загрузке данных'}), 500


def validate_dates(data):
    """Валидация дат"""
    errors = []
    
    # Проверка даты 2-го приглашения >= даты 1-го
    if data.get('inviteDate1') and data.get('inviteDate2'):
        if data['inviteDate2'] < data['inviteDate1']:
            errors.append('Дата 2-го приглашения должна быть не раньше даты 1-го приглашения')
    
    # Проверка даты убытия >= дате прибытия
    if data.get('arrivalDate') and data.get('departureDate'):
        if data['departureDate'] < data['arrivalDate']:
            errors.append('Дата отъезда должна быть не раньше даты приезда')
    
    # Проверка даты заявки >= даты 1-го приглашения
    if data.get('inviteDate1') and data.get('applicationDate'):
        if data['applicationDate'] < data['inviteDate1']:
            errors.append('Дата поступления заявки должна быть не раньше даты 1-го приглашения')
    
    return errors


@app.route('/api/participants', methods=['POST'])
def create_participant():
    """Создать нового участника"""
    try:
        data = request.json
        
        # Валидация обязательных полей
        required_fields = ['lastName', 'firstName', 'organization', 'position', 
                          'city', 'country', 'email', 'role', 'feeAmount', 'feeDate']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400
        
        # Проверка уникальности email
        existing = Participant.query.filter_by(email=data.get('email')).first()
        if existing:
            logger.warning(f'Попытка создать участника с существующим email: {data.get("email")}')
            return jsonify({'error': 'Участник с таким email уже существует'}), 400
        
        # Валидация дат
        date_errors = validate_dates(data)
        if date_errors:
            return jsonify({'error': '; '.join(date_errors)}), 400
        
        participant = Participant(
            lastName=data.get('lastName'),
            firstName=data.get('firstName'),
            patronymic=data.get('patronymic', ''),
            degree=data.get('degree', ''),
            title=data.get('title', ''),
            field=data.get('field', ''),
            organization=data.get('organization'),
            department=data.get('department', ''),
            position=data.get('position'),
            country=data.get('country'),
            city=data.get('city'),
            postal=data.get('postal', ''),
            address=data.get('address', ''),
            workPhone=data.get('workPhone', ''),
            homePhone=data.get('homePhone', ''),
            email=data.get('email'),
            role=data.get('role'),
            topic=data.get('topic', ''),
            inviteDate1=data.get('inviteDate1'),
            inviteDate2=data.get('inviteDate2', ''),
            applicationDate=data.get('applicationDate', ''),
            thesis=data.get('thesis', False),
            thesisText=data.get('thesisText', ''),
            feeAmount=float(data.get('feeAmount')),
            feeDate=data.get('feeDate'),
            arrivalDate=data.get('arrivalDate', ''),
            departureDate=data.get('departureDate', ''),
            needsHotel=data.get('needsHotel', False)
        )
        
        db.session.add(participant)
        db.session.commit()
        
        logger.info(f'Создан новый участник: {participant.email}')
        return jsonify(participant.to_dict()), 201
    
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f'Ошибка целостности данных при создании участника: {str(e)}', exc_info=True)
        if 'email' in str(e).lower() or 'unique' in str(e).lower():
            return jsonify({'error': 'Участник с таким email уже существует'}), 400
        return jsonify({'error': 'Ошибка при сохранении данных'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Ошибка при создании участника: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при создании участника'}), 500


@app.route('/api/participants/<int:participant_id>', methods=['GET'])
def get_participant(participant_id):
    """Получить участника по ID"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        return jsonify(participant.to_dict())
    except Exception as e:
        logger.error(f'Ошибка при получении участника {participant_id}: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при загрузке данных'}), 500


@app.route('/api/participants/<int:participant_id>', methods=['PUT'])
def update_participant(participant_id):
    """Обновить участника"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        data = request.json
        
        # Валидация обязательных полей
        required_fields = ['lastName', 'firstName', 'organization', 'position', 
                          'city', 'country', 'email', 'role', 'feeAmount', 'feeDate']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400
        
        # Проверка уникальности email (если изменился)
        if data.get('email') != participant.email:
            existing = Participant.query.filter_by(email=data.get('email')).first()
            if existing:
                logger.warning(f'Попытка обновить участника с существующим email: {data.get("email")}')
                return jsonify({'error': 'Участник с таким email уже существует'}), 400
        
        # Валидация дат
        date_errors = validate_dates(data)
        if date_errors:
            return jsonify({'error': '; '.join(date_errors)}), 400
        
        # Обновление полей
        participant.lastName = data.get('lastName')
        participant.firstName = data.get('firstName')
        participant.patronymic = data.get('patronymic', '')
        participant.degree = data.get('degree', '')
        participant.title = data.get('title', '')
        participant.field = data.get('field', '')
        participant.organization = data.get('organization')
        participant.department = data.get('department', '')
        participant.position = data.get('position')
        participant.country = data.get('country')
        participant.city = data.get('city')
        participant.postal = data.get('postal', '')
        participant.address = data.get('address', '')
        participant.workPhone = data.get('workPhone', '')
        participant.homePhone = data.get('homePhone', '')
        participant.email = data.get('email')
        participant.role = data.get('role')
        participant.topic = data.get('topic', '')
        participant.inviteDate1 = data.get('inviteDate1')
        participant.inviteDate2 = data.get('inviteDate2', '')
        participant.applicationDate = data.get('applicationDate', '')
        participant.thesis = data.get('thesis', False)
        participant.thesisText = data.get('thesisText', '')
        participant.feeAmount = float(data.get('feeAmount'))
        participant.feeDate = data.get('feeDate')
        participant.arrivalDate = data.get('arrivalDate', '')
        participant.departureDate = data.get('departureDate', '')
        participant.needsHotel = data.get('needsHotel', False)
        
        db.session.commit()
        
        logger.info(f'Обновлен участник: {participant.email} (ID: {participant_id})')
        return jsonify(participant.to_dict())
    
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f'Ошибка целостности данных при обновлении участника: {str(e)}', exc_info=True)
        if 'email' in str(e).lower() or 'unique' in str(e).lower():
            return jsonify({'error': 'Участник с таким email уже существует'}), 400
        return jsonify({'error': 'Ошибка при сохранении данных'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Ошибка при обновлении участника {participant_id}: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при обновлении участника'}), 500


@app.route('/api/participants/<int:participant_id>', methods=['DELETE'])
def delete_participant(participant_id):
    """Удалить участника"""
    try:
        participant = Participant.query.get_or_404(participant_id)
        email = participant.email
        
        db.session.delete(participant)
        db.session.commit()
        
        logger.info(f'Удален участник: {email} (ID: {participant_id})')
        return jsonify({'message': 'Участник успешно удален'}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Ошибка при удалении участника {participant_id}: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при удалении участника'}), 500


@app.route('/api/invitations/search', methods=['POST'])
def search_invitations():
    """Поиск приглашенных по дате"""
    try:
        data = request.json
        date = data.get('date')
        
        if not date:
            return jsonify({'error': 'Дата обязательна'}), 400
        
        participants = Participant.query.filter_by(inviteDate1=date).all()
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при поиске приглашенных: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при поиске'}), 500


@app.route('/api/fees', methods=['GET'])
def get_fees():
    """Получить всех участников с оргвзносами"""
    try:
        participants = Participant.query.filter(Participant.feeAmount > 0).all()
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при получении оргвзносов: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при загрузке данных'}), 500


@app.route('/api/fees/search', methods=['POST'])
def search_fees_by_period():
    """Поиск оргвзносов по периоду"""
    try:
        data = request.json
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if not start_date or not end_date:
            return jsonify({'error': 'Необходимо указать период'}), 400
        
        participants = Participant.query.filter(
            Participant.feeAmount > 0,
            Participant.feeDate >= start_date,
            Participant.feeDate <= end_date
        ).all()
        
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при поиске оргвзносов: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при поиске'}), 500


@app.route('/api/reports/thesis', methods=['POST'])
def get_thesis_report():
    """Отчет по тезисам по городам"""
    try:
        data = request.json
        city = data.get('city', '')
        
        query = Participant.query.filter(
            Participant.role == 'speaker',
            Participant.thesis == True,
            Participant.thesisText != '',
            Participant.thesisText.isnot(None)
        )
        
        if city:
            query = query.filter_by(city=city)
        
        participants = query.all()
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при генерации отчета по тезисам: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при генерации отчета'}), 500


@app.route('/api/reports/hotel', methods=['POST'])
def get_hotel_report():
    """Отчет по запросам на гостиницу"""
    try:
        data = request.json
        city = data.get('city', '')
        
        query = Participant.query.filter_by(needsHotel=True)
        
        if city:
            query = query.filter_by(city=city)
        
        participants = query.all()
        return jsonify([p.to_dict() for p in participants])
    except Exception as e:
        logger.error(f'Ошибка при генерации отчета по гостинице: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при генерации отчета'}), 500


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Получить список всех городов"""
    try:
        cities = db.session.query(Participant.city).distinct().all()
        cities_list = sorted([c[0] for c in cities if c[0]])
        return jsonify(cities_list)
    except Exception as e:
        logger.error(f'Ошибка при получении списка городов: {str(e)}', exc_info=True)
        return jsonify({'error': 'Ошибка при загрузке данных'}), 500


# Статические файлы (должны быть после API маршрутов)
@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Статические файлы (CSS, JS)"""
    # Исключаем API маршруты
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return send_from_directory('.', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

