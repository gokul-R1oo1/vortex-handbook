

Vortex provides an intuitive and robust platform for managing online learning experiences. It offers features that address the specific needs of administrators, teachers, managers, and employees, ensuring a seamless educational experience.

User Roles and Responsibilities
Administrators:

Control user access by registering, managing, deactivating, or deleting users.
Gain an overarching view of platform activities, including teacher performance and feedback from parents.
Manage and upload lesson content.
Teachers:

Guide employees through lessons.
Mark attendance and validate employee participation.
Assess and grade employee projects.
Managers:

Register employees after admin approval, ensuring accurate employee information.
Monitor employee attendance and performance.
Access detailed performance reports for each chapter.
Employees:

Access and complete lessons in the prescribed order.
Progress to subsequent lessons is dependent on performance in current lessons.
Features
Multi-user support with defined roles
Newsletter subscription for periodic updates
Basic user authentication
Two-factor authentication via Twilio
Email communication using Twilio SendGrid
Technologies Used
Backend: Flask micro-framework (Python)
Frontend: JavaScript, DatatableJS
Authentication: Twilio Verify API (Two-factor authentication)
Email: Twilio SendGrid
Deployment: Gunicorn
Database: PostgreSQL with fallback to SQLite
ORM: Flask-SQLAlchemy
Migrations: Flask-Migrate
Time Formatting: Flask-Moment
Testing: Pytest, pytest-cov
Phone Number Management: Phonenumbers package
Application Details
Newsletter
Users can subscribe to receive periodic updates.
Registration requires email verification.
Pre-scheduled emails are sent automatically to subscribers.
Admins can send personalized emails to individual subscribers for enhanced communication.
Multi-user Support
Superadmin: A unique role with comprehensive control, including adding other admins and teachers.
Manager Registration: Accessible from the homepage, allowing anonymous users to register as managers.
Employee Registration: Performed by registered managers, with login details sent via email.
Teacher Registration: Conducted by admins, with corresponding email notifications.
Admin Registration: Additional admins can be registered by logged-in admins, following the same process as teacher registration.
Testing Locally
To run the application locally:

Clone the repository:

bash
Copy code
$ git clone https://github.com/gokul-R1oo1/vortex-handbook.git
$ cd Vortex-handbook
Create and activate a virtual environment:

bash
Copy code
# Using virtualenvwrapper
$ mkvirtualenv venv

# Or using Python's venv module
$ python3 -m venv venv
$ source venv/bin/activate
Install dependencies:

bash
Copy code
(venv) $ pip install -r requirements.txt
Set up environment variables:

bash
Copy code
(venv) $ cp .env-template .env
Start the Flask server:

bash
Copy code
(venv) $ flask run
Access the application:
Open http://127.0.0.1:5000 in your browser.

Areas of Improvement
Notifications for in-app activities
Capture user gender during registration for personalized email salutations (Mr./Ms.)
Allow users to request account deletion
Restrict access to subsequent lessons until a pass mark is achieved
Enable teachers to mark employee attendance
Incorporate employee quizzes as part of the lesson assessments
Display employee performance metrics on profiles and dashboards
Use graphs to visualize employee performance, enrollment, and activity
Refactor the app using blueprints and factory functions
Implement threading for email-sending processes to improve app speed
