from django.contrib.auth.models import User
from django.test import TestCase


class UserDatabaseTest(TestCase):
    """
    Class-based test for user database operations with automatic rollback.
    Django's TestCase automatically wraps each test in a transaction that
    gets rolled back after the test completes, protecting the existing database.
    """

    def test_user_can_be_created(self):
        """
        Test that a user can be created and retrieved from the database.
        """
        User.objects.create_user(username="testuser", password="password123")
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username="testuser")
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("password123"))
