


## Overview

Built with love and from experience, this project summarizes the ideas that may be pivotal to any learning center, especially if conducted online. It covers the needs of four types of users:

- Administrators:
    - You control who uses the platform, by registering them, managing their data, temporarily deactivating users or permanently deleting them and their data.
    - You get a bird's eye view of the entire business: what teachers are doing, what Employees are doing, what paretnts have to say
    - You manage lesson contents by uploading them to the platform

- Teachers:
    - Tasked with guiding Employees through the lessons
    - They mark Employees' attendance, compounded to ratify each Employee's participation.
    - They assess their submitted lesson projects
    - They grade Employees projects

- Managers:
    - They register their studensts once approved by the admin. Done so so that Employee information is accurate.
    - They see how well their staffs attendance has been
    - They get to see how they perform in each chapter

- Employees:
    - They have access to lessons
    - They are required to complete the lessons in the order they appear
    - Access to subsequent lessons is dependant on the performance on the current chapter/lesson


### Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Additional Details](#additional-details)
- [Application Details](#application-details)
    - [Newsletter](#newsletter)
    - [Multi-user Support](#multi-user-support)
- [Testing It Locally](#testing-it-locally)
- [Areas of Improvement](#areas-of-improvement)


## Features

- Multi-user support
- Newsletter subscription
- Basic user authentication
- Two-factor authentication
- Sending of emails from the app


## Technologies Used

- Flask micro-framework
- Python for programming
- Sprinkles of JavaScript for front-end design
- Twilio Verify API for two-factor authentication
- Twilio SendGrid for email support
- Gunicorn for live app deployment
- Phonenumbers package for beautiful phone numbers
- DatatableJS for interactive tables
- Pytest and pytest-cov for testing
- Psycopg2 for postgresql adaptability
- Postgresql database or fallback to SQLite database
- Flask-sqlalchemy ORM for database management
- Flask-migrate for database migrations
- Flask-moment for time formatting



## Application Details

### Newsletter:

- A user interested in receiving periodic updates about Vortex can sign up for the newsletter service.
- Registration is limited to those who verify their email addresses only
![How newsletter works]
- The application automatically sends pre-prepared emails to them at set intervals
![Regular emails]
- Admin can email an individual newsletter subscriber to enhance one-on-one communication (optional)
![Admin talks with subscriber]


### Multi-user Support

>The application features a **superadmin**, who cannot be deleted. This superadmin is the source of all activities in the app. For example:
>
>- All teachers are added by the superadmin
>- Other admins, with limited powers, are also added by the superadmin
>
>To login as a superadmin, you can use this credentials:
>
>- Visit: **https://Vortex.onrender.com/login**
>- Username: **tastebolder**
>- Password: **Vortex123**

- Manager Registration (anonymous user can register as a manager)
    - Done from the home page **https://register/Manager**
    ![Register manager]

- Employee Registration (done ONLY by a registered manager - designed so to allow for their association)
    - Done from the logged-in manager's account **https://http://127.0.0.1:5000/login**
    ![Register Employee]
    - An email will be sent to the Employee to check their login details
    ![Employee login details]

- Teacher Registration (done only by a logged in admin - not necessarily the superadmin)
    - Done from the logged-in admin's account **https://Vortex.onrender.com/register/teacher**
    ![Register teacher](/app/static/images/readme/register_teacher.gif)
    - An email will be sent to the teacher to check their login details
    ![Teacher login details](/app/static/images/readme/teacher_login_details.gif)

- Other admin registration (done only by a logged in admin - not necessarily the superadmin)
    - Done from the logged-in admin's account **https://Vortex.onrender.com/register/admin**
    ![Register admin](/app/static/images/readme/register_admin.gif)
    - An email will be sent to the admin to check their login details
    ![Teacher login details](/app/static/images/readme/admin_login_details.gif)

## Testing It Locally

- Change directory into the cloned repo:

    ```python
    $ cd Vortex-online-school-using-flask
    ```
- Create and activate a virtual environment

    ```python
    # Using virtualenvwrapper
    $ mkvirtualenv venv

    # Normal way
    $ python3 -m venv venv
    $ source venv/bin/activate
    ```

- Install needed dependancies:

    ```python
    (venv)$ pip3 install -r requirements.txt
    ```

- Add and update environment variables in a `.env` file as seen in `.env-template`:

    ```python
    (venv)$ cp .env-template .env
    ```

- Start the flask server:

    ```python
    (venv)$ flask run
    ```

- Check the application in your favourite browser by pasting http://127.0.0.1:5000.


## Areas of Improvement

- Notifications of activities taking place within the app
- Capture user gender during registration to help define how to send an email(Mr. or Ms.)
- Other user's can request to delete their own accounts
- Restricted access to subsequent chapters by Employees unless passmark is achieved
- Marking of Employees attendance by teachers
- Addition of Employee project quizzes to be assessed by teachers
- Display of Employee performance in each chapter on Employees and managers' profile pages
- Display of graphs to indicate Employee performance, Employee enrollment, account activities etc
- Use of blueprints and factory function
- Threading of the process of sending emails to make the app faster (you will notice the app slow down when sending emails)
