"""
Testing all aspects of the application
"""
from flask_mail import Message

# Database configuration is imported first prior to
# all other configurations

import os
os.environ['DATABASE_URL'] = 'sqlite://' # Use in-memory db, denoted by two forward slashes
# Email Support
os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
os.environ['MAIL_USERNAME'] = 'testmanager@email.com'
os.environ['MAIL_PASSWORD'] = 'testmanager'
os.environ['ADMINS'] = 'testuser@email.com'

from app import app, db
from app.email import send_async_email, send_email
import unittest
from app.models import manager, Employee,Teacher, Admin, User, Email
from datetime import datetime, timedelta
from time import time
import jwt
from app import mail
from threading import Thread


class TestElearningApp(unittest.TestCase):

    def setUp(self):
        self.app = app

        # Disable csrf protection
        self.app.config['SECRET_KEY'] = 'testKEY'
        self.app.config['WTF_CSRF_ENABLED'] = False

        # Application context
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()                       # < --- create database during setup
        self.add_manager_to_db()               # < --- populate manager db
        self.client = self.app.test_client()  # < --- test client

    def tearDown(self):
        db.drop_all()                         # < --- discard database after each test
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def test_elearning_app(self):
        assert self.app is not None
        assert app == self.app

    def test_home_page_access(self):
        ''''''
        response = self.client.get('/')
        response_home = self.client.get('/home')
        assert response.status_code == 200
        assert response_home.status_code == 200

    # =====================
    # User
    # =====================

    def test_password_hashing(self):
        user = User(username='testuser')
        user.set_password('testuser2023')
        assert user.check_password('muthoni') == False
        assert user.check_password('testuser2023') == True

    def test_avatar(self):
        user = User(username='testuser', email='testuser@email.com')
        assert user.avatar(36) == ('https://www.gravatar.com/avatar/'
                                    '04678e8bacf37f21ebfbcdddefad9468'
                                    '?d=identicon&s=36')

    def test_reset_password_token(self):
        """Test generation of password reset token"""
        user = User(username='testuser', email='testuser@email.com')

        assert jwt.encode({'reset_password': user.email},'secret', algorithm='HS256') == \
            ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXNldF9wYXNzd29yZCI6InRlc'
             '3R1c2VyQGVtYWlsLmNvbSJ9.t__XarhVUwMSwekw_QsoipBREdvLjcl7kCwqwKlfnB8')

    def test_verify_password_reset_token(self, expires_in=600):
        """Verify the token generated"""
        user = User(username='testuser', email='testuser@email.com')

        token = jwt.encode(
                {'reset_password': user.email, 'exp': time() + expires_in},
                'secret',
                algorithm='HS256')
        token = jwt.encode({'reset_password': 'testuser@email.com'},'secret',algorithm='HS256')
        email = jwt.decode(token, 'secret', algorithms=['HS256'])['reset_password']
        assert email == 'testuser@email.com'

    # def sending_email_to_user(self, user):
    #     self.send_email(
    #         subject='Test Email',
    #         sender=app.config['MAIL_USERNAME'],
    #         recipients=[user.email],
    #         text_body='This is a test',
    #         html_body='<p>This is a test</p>')

    # =====================
    # End of user testing
    # =====================

    # =====================
    # manager
    # =====================

    def add_manager_to_db(self):
        manager = manager(
            first_name='Test',
            last_name='manager',
            username='testmanager',
            email='testmanager@email.com',
            phone_number='+254700111222',
            current_residence='Roselyn, Nairobi'
        )
        manager.set_password('testmanager2023')
        db.session.add(manager)
        db.session.commit()

    def manager_login(self):
        self.client.post('/login', data={
            'username': 'testmanager',
            'password': 'testmanager2023'
        })

    def test_manager_registration_form(self):
        response = self.client.get('/register')
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # All these fields must be included
        assert 'name="first_name"' in html
        assert 'name="last_name"' in html
        assert 'name="username"' in html
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert 'name="confirm_password"' in html
        assert 'name="phone_number"' in html
        assert 'name="residence"' in html
        assert 'name="register"' in html

    def test_mismatched_passwords_during_manager_registration(self):
        response = self.client.post('/register', data={
            'first_name': 'test',
            'last_name': 'manager',
            'username': 'testmanager',
            'email': 'testmanager@email.com',
            'password': 'testuser2023',
            'confirm_password': 'testuser2023',
            'phone_number': '+254700111222',
            'residence': 'Roselyn, Nairobi'
        })
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Field must be equal to confirm_password' in html

    def test_manager_registration(self):
        response = self.client.post('/register/manager', data={
            'first_name': 'test',
            'last_name': 'manager',
            'username': 'testmanager',
            'email': 'testmanager@email.com',
            'password': 'testmanager2023',
            'confirm_password': 'testmanager2023',
            'phone_number': '+254700111222',
            'current_residence': 'Nairobi',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/login'            # <--- redirected to the login page

    def test_manager_login(self):
        response = self.client.post('/login', data={
            'username': 'testmanager',
            'password': 'testmanager2023'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/manager/profile'
        html = response.get_data(as_text=True)
        assert 'Hi, testmanager!' in html

    def test_manager_register_child(self):
        self.manager_login()
        response = self.client.post('/register/Employee', data={
            'first_name': 'test',
            'last_name': 'Employee',
            'username': 'testEmployee',
            'email': 'testEmployee@email.com',
            'password': 'testEmployee2023',
            'confirm_password': 'testEmployee2023',
            'phone_number': '+254700111222',
            'school': 'Roselyn Academy',
            'age': 10,
            'coding_experience': 'None',
            'program': 'Introduction to Web Development',
            'cohort': 1,
            'program_schedule': 'Crash'
        }, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Employee successfully registered' in html
        assert response.request.path == '/manager/profile'

    def test_manager_payment(self):
        pass

    def test_manager_deactivate_account(self):
        manager = manager(username='testmanager', email='testmanager@email.com')
        response = self.client.get('/manager/deactivate-account', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/manager/profile'
        # self.sending_email_to_user(manager)

    def test_manager_writing_email_to_support(self):
        self.manager_login()
        response = self.client.post('/contact-support', data={
            'subject': 'Test Subject',
            'body': 'Test email'
        }, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Email saved' in html
        assert response.request.path == '/engagment-history'

        response = self.client.get('/email/send', data={
            'subject': 'I Need Help',
            'body': 'I am new on this platform'
        },follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'I Need Help' in html
        assert response.request.path == '/engagment-history'

    def test_manager_delete_written_email(self):
        self.manager_login()

        # Add email to db
        manager = manager(username='testmanager')
        email = Email(subject='I Need Help', body='I am new on this platform', author=manager)
        db.session.add(email)
        db.session.commit()

        # Deleting email from db
        response = self.client.get('email/delete', follow_redirects=True)
        email1 = Email.query.filter_by(subject='I Need Help').first_or_404()
        db.session.delete(email1)
        db.session.commit()

        assert response.status_code == 200
        assert email1 is None
        assert response.request.path == '/engagment-history'
        html = response.get_data(as_text=True)
        assert 'Email deleted' in html



    # =====================
    # End of manager testing
    # =====================

    # =====================
    # Employee
    # =====================


    # =====================
    # End of Employee testing
    # =====================

    # =====================
    # Teacher
    # =====================


    # =====================
    # End of teacher testing
    # =====================

    # =====================
    # Admin
    # =====================


    # =====================
    # End of admin testing
    # =====================
