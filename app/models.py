from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Participant(db.Model):
    """Модель участника конференции"""
    __tablename__ = 'participants'
    
    id = db.Column(db.Integer, primary_key=True)
    lastName = db.Column(db.String(100), nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100), default='')
    degree = db.Column(db.String(50), default='')
    title = db.Column(db.String(100), default='')
    field = db.Column(db.String(100), default='')
    organization = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(200), default='')
    position = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal = db.Column(db.String(20), default='')
    address = db.Column(db.String(300), default='')
    workPhone = db.Column(db.String(50), default='')
    homePhone = db.Column(db.String(50), default='')
    email = db.Column(db.String(200), nullable=False, unique=True)
    thesisText = db.Column(db.Text, default='')  # Текст тезисов
    role = db.Column(db.String(20), nullable=False)  # 'speaker' or 'participant'
    topic = db.Column(db.Text, default='')
    inviteDate1 = db.Column(db.String(10), default='')
    inviteDate2 = db.Column(db.String(10), default='')
    applicationDate = db.Column(db.String(10), default='')
    thesis = db.Column(db.Boolean, default=False)
    feeAmount = db.Column(db.Float, nullable=False)
    feeDate = db.Column(db.String(10), nullable=False)
    arrivalDate = db.Column(db.String(10), default='')
    departureDate = db.Column(db.String(10), default='')
    needsHotel = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'lastName': self.lastName,
            'firstName': self.firstName,
            'patronymic': self.patronymic,
            'degree': self.degree,
            'title': self.title,
            'field': self.field,
            'organization': self.organization,
            'department': self.department,
            'position': self.position,
            'country': self.country,
            'city': self.city,
            'postal': self.postal,
            'address': self.address,
            'workPhone': self.workPhone,
            'homePhone': self.homePhone,
            'email': self.email,
            'role': self.role,
            'topic': self.topic,
            'inviteDate1': self.inviteDate1,
            'inviteDate2': self.inviteDate2,
            'applicationDate': self.applicationDate,
            'thesis': self.thesis,
            'feeAmount': self.feeAmount,
            'feeDate': self.feeDate,
            'arrivalDate': self.arrivalDate,
            'departureDate': self.departureDate,
            'needsHotel': self.needsHotel,
            'thesisText': self.thesisText
        }


def init_db():
    """Инициализация базы данных с тестовыми данными"""
    # Проверяем, существует ли таблица и нужна ли миграция
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    # Если таблица существует, проверяем наличие новых колонок
    tables = inspector.get_table_names()
    needs_migration = False
    
    if 'participants' in tables:
        columns = [col['name'] for col in inspector.get_columns('participants')]
        # Проверяем наличие новых полей
        if 'thesisText' not in columns:
            needs_migration = True
    
    # Если нужна миграция, пересоздаем таблицу
    if needs_migration:
        # Сохраняем существующие данные перед пересозданием
        existing_data = []
        try:
            # Используем прямой SQL запрос для чтения данных без модели
            from sqlalchemy import text
            result = db.session.execute(text("SELECT * FROM participants"))
            rows = result.fetchall()
            columns_old = [col['name'] for col in inspector.get_columns('participants')]
            
            for row in rows:
                data = {}
                for i, col_name in enumerate(columns_old):
                    data[col_name] = row[i]
                # Добавляем новое поле с пустым значением
                data['thesisText'] = ''
                existing_data.append(data)
        except Exception as e:
            # Если не удалось прочитать данные, просто пересоздадим таблицу
            print(f"Не удалось сохранить данные при миграции: {e}")
        
        # Пересоздаем таблицу
        db.drop_all()
        db.create_all()
        
        # Восстанавливаем данные
        if existing_data:
            for data in existing_data:
                # Преобразуем данные в формат модели
                participant_data = {
                    'lastName': data.get('lastName', ''),
                    'firstName': data.get('firstName', ''),
                    'patronymic': data.get('patronymic', ''),
                    'degree': data.get('degree', ''),
                    'title': data.get('title', ''),
                    'field': data.get('field', ''),
                    'organization': data.get('organization', ''),
                    'department': data.get('department', ''),
                    'position': data.get('position', ''),
                    'country': data.get('country', ''),
                    'city': data.get('city', ''),
                    'postal': data.get('postal', ''),
                    'address': data.get('address', ''),
                    'workPhone': data.get('workPhone', ''),
                    'homePhone': data.get('homePhone', ''),
                    'email': data.get('email', ''),
                    'role': data.get('role', ''),
                    'topic': data.get('topic', ''),
                    'inviteDate1': data.get('inviteDate1', ''),
                    'inviteDate2': data.get('inviteDate2', ''),
                    'applicationDate': data.get('applicationDate', ''),
                    'thesis': bool(data.get('thesis', False)),
                    'thesisText': data.get('thesisText', ''),
                    'feeAmount': float(data.get('feeAmount', 0)),
                    'feeDate': data.get('feeDate', ''),
                    'arrivalDate': data.get('arrivalDate', ''),
                    'departureDate': data.get('departureDate', ''),
                    'needsHotel': bool(data.get('needsHotel', False))
                }
                participant = Participant(**participant_data)
                db.session.add(participant)
            db.session.commit()
    else:
        # Таблицы не существует или миграция не нужна, создаем/обновляем её
        db.create_all()
    
    # Проверяем, есть ли уже данные
    try:
        count = Participant.query.count()
        if count == 0:
            # Добавляем тестовые данные
            participants = [
                Participant(
                    lastName='Иванов',
                firstName='Иван',
                patronymic='Иванович',
                degree='д.т.н.',
                title='профессор',
                field='Информатика',
                organization='МГУ',
                department='ИМ',
                position='профессор',
                country='Россия',
                city='Москва',
                postal='119234',
                address='Ленинские горы, 1',
                workPhone='+7-495-123-45-67',
                homePhone='+7-495-123-45-68',
                email='ivanov@msu.ru',
                role='speaker',
                topic='Искусственный интеллект в современной науке',
                inviteDate1='2024-01-15',
                applicationDate='2024-02-01',
                thesis=True,
                thesisText='Тезисы доклада об искусственном интеллекте в современной науке. Рассматриваются основные направления развития ИИ, методы машинного обучения и их применение в различных областях.',
                inviteDate2='2024-02-10',
                feeAmount=5000.0,
                feeDate='2024-02-15',
                arrivalDate='2024-03-01',
                departureDate='2024-03-03',
                needsHotel=True
                ),
                Participant(
                    lastName='Петров',
                firstName='Петр',
                patronymic='Петрович',
                degree='к.ф.-м.н.',
                title='доцент',
                field='Математика',
                organization='СПбГУ',
                department='ММ',
                position='доцент',
                country='Россия',
                city='Санкт-Петербург',
                postal='199034',
                address='Университетская наб., 7-9',
                workPhone='+7-812-123-45-67',
                homePhone='+7-812-123-45-68',
                email='petrov@spbu.ru',
                role='participant',
                topic='Методы численного анализа',
                inviteDate1='2024-01-15',
                applicationDate='2024-02-05',
                thesis=True,
                thesisText='Тезисы доклада о методах численного анализа. Представлены современные алгоритмы решения дифференциальных уравнений и их применение в вычислительной математике.',
                inviteDate2='2024-02-10',
                feeAmount=3000.0,
                feeDate='2024-02-20',
                arrivalDate='2024-03-01',
                departureDate='2024-03-02',
                needsHotel=False
                )
            ]
            
            for p in participants:
                db.session.add(p)
            
            db.session.commit()
    except Exception:
        # Если произошла ошибка при проверке количества, просто создаем таблицу
        db.create_all()
        if Participant.query.count() == 0:
            for p in [
                Participant(
                    lastName='Иванов',
                    firstName='Иван',
                    patronymic='Иванович',
                    degree='д.т.н.',
                    title='профессор',
                    field='Информатика',
                    organization='МГУ',
                    department='ИМ',
                    position='профессор',
                    country='Россия',
                    city='Москва',
                    postal='119234',
                    address='Ленинские горы, 1',
                    workPhone='+7-495-123-45-67',
                    homePhone='+7-495-123-45-68',
                    email='ivanov@msu.ru',
                    role='speaker',
                    topic='Искусственный интеллект в современной науке',
                    inviteDate1='2024-01-15',
                    applicationDate='2024-02-01',
                    thesis=True,
                    thesisText='Тезисы доклада об искусственном интеллекте в современной науке. Рассматриваются основные направления развития ИИ, методы машинного обучения и их применение в различных областях.',
                    inviteDate2='2024-02-10',
                    feeAmount=5000.0,
                    feeDate='2024-02-15',
                    arrivalDate='2024-03-01',
                    departureDate='2024-03-03',
                    needsHotel=True
                ),
                Participant(
                    lastName='Петров',
                    firstName='Петр',
                    patronymic='Петрович',
                    degree='к.ф.-м.н.',
                    title='доцент',
                    field='Математика',
                    organization='СПбГУ',
                    department='ММ',
                    position='доцент',
                    country='Россия',
                    city='Санкт-Петербург',
                    postal='199034',
                    address='Университетская наб., 7-9',
                    workPhone='+7-812-123-45-67',
                    homePhone='+7-812-123-45-68',
                    email='petrov@spbu.ru',
                    role='participant',
                    topic='Методы численного анализа',
                    inviteDate1='2024-01-15',
                    applicationDate='2024-02-05',
                    thesis=True,
                    thesisText='Тезисы доклада о методах численного анализа. Представлены современные алгоритмы решения дифференциальных уравнений и их применение в вычислительной математике.',
                    inviteDate2='2024-02-10',
                    feeAmount=3000.0,
                    feeDate='2024-02-20',
                    arrivalDate='2024-03-01',
                    departureDate='2024-03-02',
                    needsHotel=False
                )
            ]:
                db.session.add(p)
            db.session.commit()

