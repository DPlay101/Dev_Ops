from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
from models import db, Participant, init_db

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
    participants = Participant.query.all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/participants', methods=['POST'])
def create_participant():
    """Создать нового участника"""
    data = request.json
    
    # Валидация обязательных полей
    required_fields = ['lastName', 'firstName', 'organization', 'position', 
                      'city', 'country', 'email', 'role', 'feeAmount', 'feeDate']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Поле {field} обязательно для заполнения'}), 400
    
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
        feeAmount=float(data.get('feeAmount')),
        feeDate=data.get('feeDate'),
        arrivalDate=data.get('arrivalDate', ''),
        departureDate=data.get('departureDate', ''),
        needsHotel=data.get('needsHotel', False)
    )
    
    db.session.add(participant)
    db.session.commit()
    
    return jsonify(participant.to_dict()), 201


@app.route('/api/participants/<int:participant_id>', methods=['GET'])
def get_participant(participant_id):
    """Получить участника по ID"""
    participant = Participant.query.get_or_404(participant_id)
    return jsonify(participant.to_dict())


@app.route('/api/invitations/search', methods=['POST'])
def search_invitations():
    """Поиск приглашенных по дате"""
    data = request.json
    date = data.get('date')
    
    if not date:
        return jsonify({'error': 'Дата обязательна'}), 400
    
    participants = Participant.query.filter_by(inviteDate1=date).all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/fees', methods=['GET'])
def get_fees():
    """Получить всех участников с оргвзносами"""
    participants = Participant.query.filter(Participant.feeAmount > 0).all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/fees/search', methods=['POST'])
def search_fees_by_period():
    """Поиск оргвзносов по периоду"""
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


@app.route('/api/reports/thesis', methods=['POST'])
def get_thesis_report():
    """Отчет по тезисам по городам"""
    data = request.json
    city = data.get('city', '')
    
    query = Participant.query.filter(
        Participant.role == 'speaker',
        Participant.topic != '',
        Participant.topic.isnot(None)
    )
    
    if city:
        query = query.filter_by(city=city)
    
    participants = query.all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/reports/hotel', methods=['POST'])
def get_hotel_report():
    """Отчет по запросам на гостиницу"""
    data = request.json
    city = data.get('city', '')
    
    query = Participant.query.filter_by(needsHotel=True)
    
    if city:
        query = query.filter_by(city=city)
    
    participants = query.all()
    return jsonify([p.to_dict() for p in participants])


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Получить список всех городов"""
    cities = db.session.query(Participant.city).distinct().all()
    cities_list = sorted([c[0] for c in cities if c[0]])
    return jsonify(cities_list)


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

