#!/usr/bin/env python3

from datetime import date, timedelta
from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Deleting existing data...')
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()

    print('Creating exercises...')
    exercises = [
        Exercise(name='Push-ups', category='strength', equipment_needed=False),
        Exercise(name='Squats', category='strength', equipment_needed=False),
        Exercise(name='Deadlifts', category='strength', equipment_needed=True),
        Exercise(name='Running', category='cardio', equipment_needed=False),
        Exercise(name='Cycling', category='cardio', equipment_needed=True),
        Exercise(name='Yoga Stretch', category='flexibility', equipment_needed=False),
        Exercise(name='Plank', category='endurance', equipment_needed=False),
        Exercise(name='Single Leg Stand', category='balance', equipment_needed=False),
    ]
    db.session.add_all(exercises)
    db.session.commit()

    print('Creating workouts...')
    today = date.today()
    workouts = [
        Workout(date=today, duration_minutes=45, notes='Morning strength training'),
        Workout(date=today - timedelta(days=1), duration_minutes=30, notes='Quick cardio session'),
        Workout(date=today - timedelta(days=2), duration_minutes=60, notes='Full body workout'),
        Workout(date=today - timedelta(days=3), duration_minutes=20, notes='Recovery day - light stretching'),
    ]
    db.session.add_all(workouts)
    db.session.commit()

    print('Creating workout exercises...')
    workout_exercises = [
        WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[0].id, reps=15, sets=3),
        WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[1].id, reps=12, sets=4),
        WorkoutExercise(workout_id=workouts[0].id, exercise_id=exercises[6].id, duration_seconds=60, sets=3),

        WorkoutExercise(workout_id=workouts[1].id, exercise_id=exercises[3].id, duration_seconds=1200),
        WorkoutExercise(workout_id=workouts[1].id, exercise_id=exercises[4].id, duration_seconds=600),

        WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[0].id, reps=20, sets=4),
        WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[1].id, reps=15, sets=4),
        WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[2].id, reps=8, sets=3),
        WorkoutExercise(workout_id=workouts[2].id, exercise_id=exercises[6].id, duration_seconds=90, sets=2),

        WorkoutExercise(workout_id=workouts[3].id, exercise_id=exercises[5].id, duration_seconds=900),
        WorkoutExercise(workout_id=workouts[3].id, exercise_id=exercises[7].id, duration_seconds=120, sets=2),
    ]
    db.session.add_all(workout_exercises)
    db.session.commit()

    print('Seeding complete!')
    print(f'Created {len(exercises)} exercises')
    print(f'Created {len(workouts)} workouts')
    print(f'Created {len(workout_exercises)} workout exercises')
