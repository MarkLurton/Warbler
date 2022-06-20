"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

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

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_view_follower_following_pages(self):
        
        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                id2 = self.testuser2.id
            
        own_followers_resp = c.get(f"/users/{self.testuser.id}/followers")
        own_following_resp = c.get(f"/users/{self.testuser.id}/following")
        others_followers_resp = c.get(f"/users/{id2}/followers")
        others_following_resp = c.get(f"/users/{id2}/following")

        self.assertEqual(own_followers_resp.status_code, 200)
        self.assertEqual(own_following_resp.status_code, 200)
        self.assertEqual(others_followers_resp.status_code, 200)
        self.assertEqual(others_following_resp.status_code, 200)


    def test_cannot_view_follower_following_pages_when_logged_out(self):
        c = self.client
        id2 = self.testuser2.id
        
        own_followers_resp = c.get(f"/users/{self.testuser.id}/followers")
        own_following_resp = c.get(f"/users/{self.testuser.id}/following")
        others_followers_resp = c.get(f"/users/{id2}/followers")
        others_following_resp = c.get(f"/users/{id2}/following")

        self.assertEqual(own_followers_resp.status_code, 302)
        self.assertEqual(own_following_resp.status_code, 302)
        self.assertEqual(others_followers_resp.status_code, 302)
        self.assertEqual(others_following_resp.status_code, 302)

    def test_add_message_when_logged_in(self):
        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post("/messages/new", data={"text" :"test message"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f"{self.testuser.username}", html)
    
    def test_add_message_fails_when_logged_out(self):
        c = self.client
             
        resp = c.post("/messages/new", data={"text" :"test message"}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized.", html)
    
    def test_delete_message_when_logged_in(self):
        m = Message(user_id=self.testuser.id, text="test message")
        
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                text = m.text
                id = m.id
            
            resp = c.post(f"/messages/{id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"{self.testuser.username}", html)
            self.assertNotIn(text, html)

    def test_delete_message_fails_when_logged_out(self):
        m = Message(user_id=self.testuser.id, text="test message")
        
        db.session.add(m)
        db.session.commit()

        c = self.client
            
        resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized.", html)

    def test_delete_message_fails_as_other_user_when_logged_in(self):
        m = Message(user_id=self.testuser2.id, text="test message")
        f = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser.id)

        db.session.add(f)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                text = m.text
                id = m.id
            
            resp = c.post(f"/messages/{id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn(text, html)
    

