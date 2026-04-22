from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema, exercises_schema, exercise_detail_schema,
    workout_schema, workouts_schema, workout_detail_schema,
    workout_exercise_schema
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def index():
    return jsonify({'message': 'Workout API'})


# ==================== WORKOUT ROUTES ====================

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)
    return make_response(workout_detail_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    try:
        data = workout_schema.load(request.json)
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)

    try:
        workout = Workout(
            date=data['date'],
            duration_minutes=data['duration_minutes'],
            notes=data.get('notes')
        )
        db.session.add(workout)
        db.session.commit()
        return make_response(workout_schema.dump(workout), 201)
    except ValueError as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 400)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ==================== EXERCISE ROUTES ====================

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)
    return make_response(exercise_detail_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
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
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return make_response(jsonify({'error': 'Exercise not found'}), 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# ==================== WORKOUT EXERCISE ROUTES ====================

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return make_response(jsonify({'error': 'Workout not found'}), 404)

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


if __name__ == '__main__':
    app.run(port=5555, debug=True)
