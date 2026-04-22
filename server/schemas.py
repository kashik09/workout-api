from marshmallow import Schema, fields, validate, validates, ValidationError


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=80, error='Username must be between 1 and 80 characters')
    )
    password = fields.Str(load_only=True, required=True)

    @validates('username')
    def validate_username(self, value):
        if not value or len(value.strip()) == 0:
            raise ValidationError('Username cannot be empty')


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(validate=validate.Range(min=0), allow_none=True)
    sets = fields.Int(validate=validate.Range(min=0), allow_none=True)
    duration_seconds = fields.Int(validate=validate.Range(min=0), allow_none=True)

    exercise = fields.Nested('ExerciseSchema', only=('id', 'name', 'category'), dump_only=True)
    workout = fields.Nested('WorkoutSchema', only=('id', 'date'), dump_only=True)

    @validates('reps')
    def validate_reps(self, value):
        if value is not None and value < 0:
            raise ValidationError('Reps must be non-negative')

    @validates('sets')
    def validate_sets(self, value):
        if value is not None and value < 0:
            raise ValidationError('Sets must be non-negative')


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error='Name must be between 1 and 100 characters')
        ]
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['strength', 'cardio', 'flexibility', 'balance', 'endurance'],
            error='Category must be one of: strength, cardio, flexibility, balance, endurance'
        )
    )
    equipment_needed = fields.Bool(load_default=False)

    workouts = fields.Nested('WorkoutSchema', many=True, only=('id', 'date', 'duration_minutes'), dump_only=True)
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, only=('id', 'reps', 'sets', 'duration_seconds', 'workout'), dump_only=True)

    @validates('name')
    def validate_name(self, value):
        if not value or len(value.strip()) == 0:
            raise ValidationError('Name cannot be empty or whitespace only')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=600, error='Duration must be between 1 and 600 minutes')
    )
    notes = fields.Str(allow_none=True)
    user_id = fields.Int(dump_only=True)

    exercises = fields.Nested(ExerciseSchema, many=True, only=('id', 'name', 'category', 'equipment_needed'), dump_only=True)
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, only=('id', 'reps', 'sets', 'duration_seconds', 'exercise'), dump_only=True)

    @validates('date')
    def validate_date(self, value):
        if value is None:
            raise ValidationError('Date is required')

    @validates('duration_minutes')
    def validate_duration(self, value):
        if value is None:
            raise ValidationError('Duration is required')
        if value <= 0:
            raise ValidationError('Duration must be positive')


user_schema = UserSchema()

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workouts', 'workout_exercises'))
exercise_detail_schema = ExerciseSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('exercises', 'workout_exercises'))
workout_detail_schema = WorkoutSchema()

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
