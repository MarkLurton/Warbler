"""User views tests."""

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

from app import app, CURR_USER_KEY

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

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test@test2.com",
                                    password="testuser",
                                    image_url=None)
        
        db.session.commit()

    def test_can_see_own_user_details_page_when_logged_in(self):

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.testuser.username, html)

    def test_can_see_other_user_details_page_when_logged_in(self):
    
        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                id2 = self.testuser2.id
                username2 = self.testuser2.username

        resp = c.get(f'/users/{id2}')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(username2, html)
    
    def test_fail_to_see_user_details_page_when_logged_out(self):

        c = self.client

        resp = c.get(f'/users/{self.testuser.id}', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized.", html)
        self.assertNotIn(self.testuser.username, html)

    def test_edit_and_delete_buttons_visible_on_own_page(self):

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        resp = c.get(f'/users/{self.testuser.id}')
        html = resp.get_data(as_text=True)

        self.assertIn('Delete Profile', html)
        self.assertIn('Edit Profile', html)

    def test_edit_and_delete_buttons_not_visible_on_others_page(self):
    
        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                id2 = self.testuser2.id

        resp = c.get(f'/users/{id2}')
        html = resp.get_data(as_text=True)

        self.assertNotIn('Delete Profile', html)
        self.assertNotIn('Edit Profile', html)