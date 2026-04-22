# Workout Tracking API

A Flask-based REST API for tracking workouts and exercises. Personal trainers can create workouts, add exercises, and track sets, reps, and duration for each exercise within a workout.

## Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd workout-api
   ```
3. Install dependencies:
   ```bash
   pipenv install
   ```
4. Activate the virtual environment:
   ```bash
   pipenv shell
   ```
5. Navigate to the server directory:
   ```bash
   cd server
   ```
6. Initialize and migrate the database:
   ```bash
   flask db init
   flask db migrate -m 'initial migration'
   flask db upgrade head
   ```
7. Seed the database:
   ```bash
   python seed.py
   ```

## Running the Application

```bash
cd server
flask run --port 5555
```

Or:

```bash
python app.py
```

The API will be available at `http://localhost:5555`

## API Endpoints

### Workouts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Get a single workout with associated exercises |
| POST | `/workouts` | Create a new workout |
| DELETE | `/workouts/<id>` | Delete a workout (cascades to workout_exercises) |

#### Create Workout Request Body
```json
{
  "date": "2026-04-22",
  "duration_minutes": 45,
  "notes": "Morning workout"
}
```

### Exercises

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Get a single exercise with associated workouts |
| POST | `/exercises` | Create a new exercise |
| DELETE | `/exercises/<id>` | Delete an exercise (cascades to workout_exercises) |

#### Create Exercise Request Body
```json
{
  "name": "Push-ups",
  "category": "strength",
  "equipment_needed": false
}
```

Valid categories: `strength`, `cardio`, `flexibility`, `balance`, `endurance`

### Workout Exercises

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout |

#### Add Exercise to Workout Request Body
```json
{
  "reps": 15,
  "sets": 3,
  "duration_seconds": null
}
```

## Models

### Exercise
- `id`: Integer, primary key
- `name`: String, required, unique
- `category`: String, required (strength, cardio, flexibility, balance, endurance)
- `equipment_needed`: Boolean, defaults to false

### Workout
- `id`: Integer, primary key
- `date`: Date, required
- `duration_minutes`: Integer, required, must be positive
- `notes`: Text, optional

### WorkoutExercise (Join Table)
- `id`: Integer, primary key
- `workout_id`: Foreign key to Workout
- `exercise_id`: Foreign key to Exercise
- `reps`: Integer, optional
- `sets`: Integer, optional
- `duration_seconds`: Integer, optional

## Validations

### Table Constraints
- Workout duration must be positive
- Reps, sets, and duration_seconds must be non-negative
- Exercise name must be unique

### Model Validations
- Exercise name cannot be empty (1-100 characters)
- Exercise category must be valid
- Workout duration must be between 1-600 minutes
- Workout date is required

### Schema Validations
- Name length validation (1-100 characters)
- Category must be one of the valid options
- Duration must be within range (1-600)
- Reps and sets must be non-negative

## Dependencies

- Flask 2.2.2
- Flask-Migrate 3.1.0
- Flask-SQLAlchemy 3.0.3
- Werkzeug 2.2.2
- Marshmallow 3.20.1
