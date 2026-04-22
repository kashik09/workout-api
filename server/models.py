from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )
    workouts = db.relationship(
        'Workout',
        secondary='workout_exercises',
        back_populates='exercises',
        viewonly=True
    )

    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError('Exercise name cannot be empty')
        if len(name) > 100:
            raise ValueError('Exercise name must be 100 characters or less')
        return name.strip()

    @validates('category')
    def validate_category(self, key, category):
        valid_categories = ['strength', 'cardio', 'flexibility', 'balance', 'endurance']
        if not category:
            raise ValueError('Category is required')
        if category.lower() not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return category.lower()

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_positive_duration'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )
    exercises = db.relationship(
        'Exercise',
        secondary='workout_exercises',
        back_populates='workouts',
        viewonly=True
    )

    @validates('duration_minutes')
    def validate_duration(self, key, duration):
        if duration is None:
            raise ValueError('Duration is required')
        if duration <= 0:
            raise ValueError('Duration must be a positive number')
        if duration > 600:
            raise ValueError('Duration cannot exceed 600 minutes')
        return duration

    @validates('date')
    def validate_date(self, key, date):
        if not date:
            raise ValueError('Date is required')
        return date

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    __table_args__ = (
        CheckConstraint('reps >= 0 OR reps IS NULL', name='check_non_negative_reps'),
        CheckConstraint('sets >= 0 OR sets IS NULL', name='check_non_negative_sets'),
        CheckConstraint('duration_seconds >= 0 OR duration_seconds IS NULL', name='check_non_negative_duration'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps')
    def validate_reps(self, key, reps):
        if reps is not None and reps < 0:
            raise ValueError('Reps cannot be negative')
        return reps

    @validates('sets')
    def validate_sets(self, key, sets):
        if sets is not None and sets < 0:
            raise ValueError('Sets cannot be negative')
        return sets

    @validates('duration_seconds')
    def validate_duration_seconds(self, key, duration):
        if duration is not None and duration < 0:
            raise ValueError('Duration seconds cannot be negative')
        return duration

    def __repr__(self):
        return f'<WorkoutExercise {self.id}: Workout {self.workout_id} - Exercise {self.exercise_id}>'
