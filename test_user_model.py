"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import IntegrityError


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_repr_method(self):

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        expected = f"<User #{u.id}: {u.username}, {u.email}>"
        actual = u.__repr__();

        self.assertEqual(expected, actual)
    
    def test_follows(self):
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        follow = Follows(user_being_followed_id=u2.id, user_following_id=u.id)

        db.session.add(follow)
        db.session.commit()

        self.assertTrue(u.is_following(u2))
        self.assertTrue(u2.is_followed_by(u))
        self.assertFalse(u2.is_following(u))
        self.assertFalse(u.is_followed_by(u2))
    
    def test_user_signup(self):
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        u2 = User.signup(
                username="testuser2",
                password="HASHED_PASSWORD",
                email="test@test2.com",
                image_url=User.image_url.default.arg
            )
        db.session.commit()

        dupe_username_test = False

        try:
            u3 = User.signup(
                    username="testuser2",
                    password="HASHED_PASSWORD",
                    email="test@test2.com",
                    image_url=User.image_url.default.arg
                )
            db.session.commit()
        except IntegrityError:
            dupe_username_test = True
            db.session.rollback()
        
        null_username_test = False

        try:
            u4 = User.signup(
                    username=None,
                    password="HASHED_PASSWORD",
                    email="test@test4.com",
                    image_url=User.image_url.default.arg
                )
            db.session.commit()
        except IntegrityError:
            null_username_test = True
            db.session.rollback()

        null_password_test = False

        try:
            u5 = User.signup(
                    username="testuser5",
                    password=None,
                    email="test@test5.com",
                    image_url=User.image_url.default.arg
                )
            db.session.commit()
        except ValueError:
            null_password_test = True
            db.session.rollback()
        
        dupe_email_test = False

        try:
            u6 = User.signup(
                    username="testuser6",
                    password="HASHED_PASSWORD",
                    email="test@test.com",
                    image_url=User.image_url.default.arg
                )
            db.session.commit()
        except IntegrityError:
            dupe_email_test = True
            db.session.rollback()
        
        null_email_test = False

        try:
            u7 = User.signup(
                    username="testuser7",
                    password="HASHED_PASSWORD",
                    email=None,
                    image_url=User.image_url.default.arg
                )
            db.session.commit()
        except IntegrityError:
            null_email_test = True
            db.session.rollback()



        self.assertEqual(u2.id, u.id + 1)
        self.assertTrue(dupe_username_test)
        self.assertTrue(null_username_test)
        self.assertTrue(null_password_test)
        self.assertTrue(dupe_email_test)
        self.assertTrue(null_email_test)
    
    def test_user_authenticate(self):
        u = User.signup(
                username="testuser",
                password="HASHED_PASSWORD",
                email="test@test.com",
                image_url=User.image_url.default.arg
            )
        db.session.commit()

        user_authenticate_success = User.authenticate("testuser", "HASHED_PASSWORD")
        user_authenticate_fail_username = User.authenticate("testuser2", "HASHED_PASSWORD")
        user_authenticate_fail_password = User.authenticate("testuser", "WRONG_PASSWORD")

        self.assertEqual(u.id, user_authenticate_success.id)
        self.assertFalse(user_authenticate_fail_username)
        self.assertFalse(user_authenticate_fail_password)
