# Workout Tracking API

A Flask-based REST API for tracking workouts and exercises with full user authentication. Users can create workouts, add exercises, and track sets, reps, and duration. Each user can only access their own workouts.

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

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Create a new user account |
| POST | `/login` | Log in to an existing account |
| DELETE | `/logout` | Log out of the current session |
| GET | `/check_session` | Check if user is logged in |
| GET | `/me/stats` | Get current user's workout statistics |

#### Signup Request Body
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

#### Login Request Body
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

### Workouts (Protected - Requires Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workouts` | List all workouts for current user (paginated) |
| GET | `/workouts/<id>` | Get a single workout with exercises |
| POST | `/workouts` | Create a new workout |
| PATCH | `/workouts/<id>` | Update a workout |
| DELETE | `/workouts/<id>` | Delete a workout |

#### Query Parameters
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10, max: 100)
- `start_date`: Filter workouts on or after this date (YYYY-MM-DD)
- `end_date`: Filter workouts on or before this date (YYYY-MM-DD)

#### Create Workout Request Body
```json
{
  "date": "2026-04-22",
  "duration_minutes": 45,
  "notes": "Morning workout"
}
```

#### Update Workout Request Body
```json
{
  "duration_minutes": 60,
  "notes": "Extended morning workout"
}
```

### Exercises (Protected - Requires Authentication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Get a single exercise |
| POST | `/exercises` | Create a new exercise |
| DELETE | `/exercises/<id>` | Delete an exercise |

#### Create Exercise Request Body
```json
{
  "name": "Push-ups",
  "category": "strength",
  "equipment_needed": false
}
```

Valid categories: `strength`, `cardio`, `flexibility`, `balance`, `endurance`

### Workout Exercises (Protected - Requires Authentication)

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

### User
- `id`: Integer, primary key
- `username`: String, required, unique (max 80 chars)
- `password_hash`: String, hashed with bcrypt

### Exercise
- `id`: Integer, primary key
- `name`: String, required, unique (max 100 chars)
- `category`: String, required (strength, cardio, flexibility, balance, endurance)
- `equipment_needed`: Boolean, defaults to false

### Workout
- `id`: Integer, primary key
- `date`: Date, required
- `duration_minutes`: Integer, required, must be positive (1-600)
- `notes`: Text, optional
- `user_id`: Foreign key to User

### WorkoutExercise (Join Table)
- `id`: Integer, primary key
- `workout_id`: Foreign key to Workout
- `exercise_id`: Foreign key to Exercise
- `reps`: Integer, optional, non-negative
- `sets`: Integer, optional, non-negative
- `duration_seconds`: Integer, optional, non-negative

## Authentication

This API uses session-based authentication. After logging in, the session cookie maintains your authentication state.

- All workout routes are protected and require authentication
- Users can only view, update, and delete their own workouts
- Unauthorized requests return 401 status code

## Test Accounts

After seeding the database:
- Username: `john_doe` | Password: `password123`
- Username: `jane_smith` | Password: `password456`

## Dependencies

- Flask 2.2.2
- Flask-Migrate 3.1.0
- Flask-SQLAlchemy 3.0.3
- Flask-Bcrypt 1.0.1
- Werkzeug 2.2.2
- Marshmallow 3.20.1
