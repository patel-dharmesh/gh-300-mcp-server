from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest

from fastapi import HTTPException

from src import app as activities_app


class ActivityApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_path = activities_app.database_path
        activities_app.database_path = Path(self.temp_dir.name) / "activities.sqlite"
        activities_app.initialize_database()

    def tearDown(self):
        activities_app.database_path = self.original_database_path
        self.temp_dir.cleanup()

    def set_activity_capacity(self, capacity):
        with activities_app.database_connection() as connection:
            connection.execute(
                "UPDATE activities SET max_participants = ? WHERE name = ?",
                (capacity, "Chess Club"),
            )

    def test_signup_persists_after_database_reinitialization(self):
        email = "new-student@mergington.edu"

        activities_app.signup_for_activity("Chess Club", email)
        activities_app.initialize_database()

        participants = activities_app.get_activities()["Chess Club"]["participants"]
        self.assertIn(email, participants)

    def test_signup_rejects_full_activity_and_duplicate_student(self):
        self.set_activity_capacity(2)

        with self.assertRaises(HTTPException) as full_error:
            activities_app.signup_for_activity(
                "Chess Club", "new-student@mergington.edu"
            )
        self.assertEqual(full_error.exception.status_code, 400)
        self.assertEqual(full_error.exception.detail, "Activity is full")

        with self.assertRaises(HTTPException) as duplicate_error:
            activities_app.signup_for_activity(
                "Chess Club", "michael@mergington.edu"
            )
        self.assertEqual(
            duplicate_error.exception.detail,
            "Student is already signed up",
        )

    def test_concurrent_signups_do_not_exceed_capacity(self):
        self.set_activity_capacity(3)
        emails = [f"student-{index}@mergington.edu" for index in range(8)]

        def signup(email):
            try:
                activities_app.signup_for_activity("Chess Club", email)
                return "signed up"
            except HTTPException as error:
                return error.detail

        with ThreadPoolExecutor(max_workers=len(emails)) as executor:
            outcomes = list(executor.map(signup, emails))

        self.assertEqual(outcomes.count("signed up"), 1)
        self.assertEqual(outcomes.count("Activity is full"), len(emails) - 1)
        self.assertEqual(
            len(activities_app.get_activities()["Chess Club"]["participants"]),
            3,
        )

    def test_unregister_removes_persisted_participant(self):
        email = "michael@mergington.edu"

        activities_app.unregister_from_activity("Chess Club", email)

        participants = activities_app.get_activities()["Chess Club"]["participants"]
        self.assertNotIn(email, participants)


if __name__ == "__main__":
    unittest.main()
