"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes
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

class MessageModelTestCase(TestCase):
    """Test message model"""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_message_model(self):
        """Does the basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(user_id=u.id, text="test message")

        db.session.add(m)
        db.session.commit()

        expected_repr = f"<Message #{m.id}: {m.user_id}, {m.text}>"
        actual_repr = m.__repr__()

        self.assertIsNotNone(m.id)
        self.assertIsNotNone(m.timestamp)
        self.assertEqual(len(u.messages), 1)
        self.assertEqual(m.text, "test message")
        self.assertEqual(u.id, m.user_id)
        self.assertEqual(expected_repr, actual_repr)
        
    def test_message_likes(self):

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test@test2.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )


        db.session.add(u)
        db.session.add(u2)
        db.session.commit()

        m = Message(user_id=u.id, text="test message")

        db.session.add(m)
        db.session.commit()

        l = Likes(user_id=u2.id, message_id=m.id)

        db.session.add(l)
        db.session.commit();

        self.assertEqual(len(m.liked_by), 1)
        self.assertEqual(len(u2.likes), 1)
        self.assertEqual(len(u.likes), 0)
