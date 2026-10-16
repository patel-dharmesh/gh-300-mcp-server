# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Prevent signups after an activity reaches capacity
- Preserve activities and participants across server restarts using SQLite

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity |

## Data Storage

Activity and participant data is stored in `src/activities.sqlite`, which is
created and seeded with the initial activities on first run. The database file
is local and ignored by Git. Set `ACTIVITIES_DATABASE_PATH` to use a different
database location.

Signups are serialized through a SQLite write transaction, so simultaneous
requests cannot enroll more students than an activity's maximum capacity.
When full, the API returns HTTP 400 with the detail `Activity is full`.
