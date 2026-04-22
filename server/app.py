#!/usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify, make_response, session
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, bcrypt, User, Exercise, Workout, WorkoutExercise
from schemas import (
    user_schema,
    exercise_schema, exercises_schema, exercise_detail_schema,
    workout_schema, workouts_schema, workout_detail_schema,
    workout_exercise_schema
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
bcrypt.init_app(app)


# ==================== AUTH ROUTES ====================

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(jsonify({'error': 'Username and password required'}), 400)

    if User.query.filter_by(username=username).first():
        return make_response(jsonify({'error': 'Username already exists'}), 422)

    try:
        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return make_response(user_schema.dump(user), 201)
    except ValueError as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(jsonify({'error': 'Username and password required'}), 400)

    user = User.query.filter_by(username=username).first()

    if user and user.authenticate(password):
        session['user_id'] = user.id
        return make_response(user_schema.dump(user), 200)

    return make_response(jsonify({'error': 'Invalid username or password'}), 401)


@app.route('/logout', methods=['DELETE'])
def logout():
    if 'user_id' in session:
        session.pop('user_id')
        return make_response('', 204)
    return make_response(jsonify({'error': 'Not logged in'}), 401)


@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            return make_response(user_schema.dump(user), 200)
    return make_response(jsonify({'error': 'Not logged in'}), 401)


# ==================== HELPER ====================

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None


# ==================== WORKOUT ROUTES ====================

@app.route('/workouts', methods=['GET'])
def get_workouts():
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    per_page = min(per_page, 100)

    query = Workout.query.filter_by(user_id=user.id)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Workout.date >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Workout.date <= end)
        except ValueError:
            pass

    pagination = query.order_by(Workout.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return make_response(jsonify({
        'workouts': workouts_schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

    if workout.user_id != user.id:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    return make_response(workout_detail_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    try:
        data = workout_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        workout = Workout(
            date=data['date'],
            duration_minutes=data['duration_minutes'],
            notes=data.get('notes'),
            user_id=user.id
        )
        db.session.add(workout)
        db.session.commit()
        return make_response(workout_schema.dump(workout), 201)
    except ValueError as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/workouts/<int:id>', methods=['PATCH'])
def update_workout(id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

    if workout.user_id != user.id:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    data = request.json
    if not data:
        return make_response(jsonify({'error': 'No data provided'}), 400)

    try:
        if 'date' in data:
            workout.date = data['date']
        if 'duration_minutes' in data:
            workout.duration_minutes = data['duration_minutes']
        if 'notes' in data:
            workout.notes = data['notes']

        db.session.commit()
        return make_response(workout_schema.dump(workout), 200)
    except (ValueError, ValidationError) as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

    if workout.user_id != user.id:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ==================== EXERCISE ROUTES ====================

@app.route('/exercises', methods=['GET'])
def get_exercises():
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)
    return make_response(exercise_detail_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    try:
        data = exercise_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        exercise = Exercise(
            name=data['name'],
            category=data['category'],
            equipment_needed=data.get('equipment_needed', False)
        )
        db.session.add(exercise)
        db.session.commit()
        return make_response(exercise_schema.dump(exercise), 201)
    except ValueError as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# ==================== WORKOUT EXERCISE ROUTES ====================

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    user = get_current_user()
    if not user:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    workout = db.session.get(Workout, workout_id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

    if workout.user_id != user.id:
        return make_response(jsonify({'error': 'Unauthorized'}), 401)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)

    data = request.json or {}
    data['workout_id'] = workout_id
    data['exercise_id'] = exercise_id

    try:
        validated_data = workout_exercise_schema.load(data)
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=validated_data.get('reps'),
            sets=validated_data.get('sets'),
            duration_seconds=validated_data.get('duration_seconds')
        )
        db.session.add(workout_exercise)
        db.session.commit()
        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    except ValueError as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/')
def index():
    return jsonify({'message': 'Workout Tracking API'})


if __name__ == '__main__':
    app.run(port=5555, debug=True)
