from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import managerRegistrationForm, EmployeeRegistrationForm, \
    TeacherRegistrationForm, AdminRegistrationForm, LoginForm, \
    ResetPasswordForm, RequestPasswordResetForm, VerifyForm,\
    EmailForm, EditEmailForm, EditPhoneForm, EditUsernameForm, FlaskChapter2QuizForm,\
    FlaskChapter3QuizForm, FlaskChapter4QuizForm
from app.models import User, manager, Employee, Teacher, Admin,\
    Newsletter_Subscriber, Email, Chapter2Quiz, Chapter3Quiz, Chapter4Quiz
from app.email import send_subscriber_private_email, send_login_details, \
    send_user_private_email
from app.email import send_password_reset_email, thank_you_client, \
    request_account_deletion
from werkzeug.urls import url_parse
from app.twilio_verify_api import request_email_verification_token, \
    check_email_verification_token
from app import app, db



# =========================================
# NEWSLETTER HOME PAGE
# =========================================


# Client signs up for the newsletter

@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Display the home page
    Seen by anonymous users
    """
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    # Newsletter form
    if request.method == "POST":
        newsletter_client = request.form["email"]
        # Send email owner a verification token in their inbox
        request_email_verification_token(newsletter_client)
        # Save user email in session
        # User not saved in database just yet
        session["email"] = newsletter_client
        flash("Please check your email inbox for a verification code")
        # Email owner redirected to confirm token received
        return redirect(url_for('verify_email_token'))
    return render_template("home.html", title="Home")



# Subscriber verifies email ownership

@app.route("/verify-email-token", methods=["GET", "POST"])
def verify_email_token():
    """
    Subscriber verifies their email address by
    providing token sent to their inbox
    """
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    form = VerifyForm()
    if form.validate_on_submit():
        email = session["email"]
        if check_email_verification_token(email, form.token.data):
            # Get the subscriber's username
            # It will be used to send a personalized thank you note for signing up
            client_email = session['email']
            client_username = client_email.split("@")[0].capitalize()

            # Add subscriber to the database
            client = Newsletter_Subscriber(email=session["email"])
            client.num_newsletter = 0 # determines what newsletter to be sent
            db.session.add(client)
            db.session.commit()
            # Remove the subscriber from the session since they are now added to the database
            del session["email"]

            # Send subscriber a thank you email
            thank_you_client(client, client_username)

            flash("Thank you for subscribing to our newsletter. Please check you inbox.")
            return redirect(url_for("home"))
        form.token.errors.append("Invalid token.")
    return render_template(
        "auth/register_anonymous_user.html",
        title="Verify Your Email",
        form=form)



# Subscriber can unsubscribe from the email newsletter

@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    """Client can stop receiving newsletters"""
    if current_user.is_authenticated:
        flash('You need to logout first to unsubscribe from our newsletters.')
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    if request.method == 'POST':
        client = Newsletter_Subscriber.query.filter_by(email=request.form["email"]).first()
        if client is None:
            flash("Please enter the email used during subscription.")
            return redirect(url_for("unsubscribe"))
        if client.is_active():
            client.active = False
            db.session.commit()
            flash("You have successfully unsubscribed from our newsletters.")
            return redirect(url_for("home"))
        if client.active is False:
            flash("You are already unsubscribed from our newsletters")
            return redirect(url_for('home'))
    return render_template(
        "auth/unsubscribe.html",
        title="Unsubscribe From Our Newsletters")

# =========================================
# END OF NEWSLETTER HOME PAGE
# =========================================



# =========================================
# USER AUTHENTICATION
# =========================================


@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))



# Login

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login logic"""
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("dashboard")
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome {user.username}.')
        return redirect(next_page)
    return render_template(
        "auth/login.html",
        title="Login",
        form=form)



# Logout

@app.route('/logout')
@login_required
def logout():
    """Logged in user can log out"""
    logout_user()
    return redirect(url_for('login'))


# Request password reset

@app.route("/request-password-reset", methods=["GET", "POST"])
def request_password_reset():
    """
    Registerd user can request for a password reset
    If not registered, the application will not tell the anonymous user why not
    """
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Send user an email
            send_password_reset_email(user)
        # Conceal database information by giving general information
        flash("Check your email for the instructions to reset your password")
        return redirect(url_for("login"))
    return render_template(
        "auth/register_anonymous_user.html",
        title="Request Password Reset",
        form=form)



# Reset password

@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Time-bound link to reset password requested by an active user sent to their inbox
    """
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("login"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. Login to continue")
        return redirect(url_for("login"))
    return render_template(
        "auth/register_anonymous_user.html",
        title="Reset Password",
        form=form)



# manager registration

@app.route("/register/Manager", methods=["GET", "POST"])
def register_manager():
    """manager registration logic"""
    if current_user.is_authenticated:
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    form = managerRegistrationForm()
    if form.validate_on_submit():
        manager = manager(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            current_residence=form.current_residence.data)

        # Show actual Employee password in registration email
        session['password'] = form.password.data
        user_password = session['password']

        # Update database
        manager.set_password(form.password.data)
        db.session.add(manager)
        db.session.commit()

        # Send manager and email with login credentials
        send_login_details(manager, user_password)

        # Delete Employee password session
        del session['password']

        flash(f"Successfully registered as {manager.username}! "
              "Check your email for further guidance.")
        return redirect(url_for('home'))
    return render_template(
        "auth/register_anonymous_user.html",
        title="Register As A Manager",
        form=form)


# Employee registration

@app.route("/register/Employee", methods=["GET", "POST"])
@login_required
def register_Employee():
    """Employee registration logic"""
    if current_user.type == "manager":
        form = EmployeeRegistrationForm()
        if form.validate_on_submit():
            Employee = Employee(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                age=form.age.data,
                school=form.school.data,
                coding_experience=form.coding_experience.data,
                program=form.program.data,
                program_schedule=form.program_schedule.data,
                cohort=form.cohort.data,
                manager=current_user)

            # Show actual teacher password in registration email
            session['password'] = form.password.data
            user_password = session['password']

            # Update database
            Employee.set_password(form.password.data)
            db.session.add(Employee)
            db.session.commit()

            # Send Employee an email with login credentials
            send_login_details(Employee,user_password)

            # Delete Employee password session
            del session['password']

            flash(f"Successfully registered your child as {Employee.username}! "
                "An email has been sent to them on the next steps to take.")
            return redirect(url_for('manager_profile'))
    else:
        flash("You do not have access to this page!")
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "admin":
            return redirect(url_for("admin_profile"))
    return render_template(
        "auth/register_current_user.html",
        title="Register Your Child",
        form=form)



# Teacher registration

@app.route("/register/teacher", methods=["GET", "POST"])
@login_required
def register_teacher():
    """Teacher registration logic"""
    if current_user.type == "admin":
        form = TeacherRegistrationForm()
        if form.validate_on_submit():
            teacher = Teacher(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                course=form.course.data,
                current_residence=form.current_residence.data)

            # Show actual teacher password in registration email
            session['password'] = form.password.data
            user_password = session['password']

            teacher.set_password(form.password.data)
            db.session.add(teacher)
            db.session.commit()

            # Send teacher an email with login credentials
            send_login_details(teacher, user_password)

            # Delete teacher password session
            del session['password']

            flash(f"Successfully registered your teacher {teacher.username}! "
                "An email has been sent to the teacher on the next steps.")
            return redirect(url_for('all_teachers'))
    else:
        flash("You do not have access to this page!")
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
    return render_template(
        "auth/register_current_user.html",
        title="Register A Teacher",
        form=form)


# Admin registration

@app.route("/register/admin", methods=["GET", "POST"])
@login_required
def register_admin():
    """Admin registration logic"""
    if current_user.type == "admin":
        form = AdminRegistrationForm()
        if form.validate_on_submit():
            admin = Admin(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                current_residence=form.current_residence.data,
                department=form.department.data)

            # Show actual admin password in registration email
            session['password'] = form.password.data
            user_password = session['password']

            # Update the database
            admin.set_password(form.password.data)
            db.session.add(admin)
            db.session.commit()

            # Send admin an email with login credentials
            send_login_details(admin, user_password)

            # Delete Employee password session
            del session['password']

            flash(f"Successfully registered your teacher {admin.username}! "
                "An email has been sent to the teacher on the next steps.")
            return redirect(url_for('all_admins'))
    else:
        flash("You do not have access to this page!")
        if current_user.type == "Employee":
            return redirect(url_for("Employee_profile"))
        if current_user.type == "teacher":
            return redirect(url_for("teacher_profile"))
        if current_user.type == "manager":
            return redirect(url_for("manager_profile"))
    return render_template(
        "auth/register_current_user.html",
        title="Register An Admin",
        form=form)


# =========================================
# END OF USER AUTHENTICATION
# =========================================




# =========================================
# AUTHENTICATED USERS
# =========================================

# ==========
# DASHBOARD
# ==========


# --------------------------------------
# Teacher profile
# --------------------------------------


@app.route("/dashboard/teacher/profile")
@login_required
def teacher_profile():
    return render_template(
        "teacher/profile.html",
        title="Teacher Profile"
    )


# Deactivate own account

@app.route('/teacher/deactivate-account')
@login_required
def teacher_deactivate_account():
    # Get current user
    teacher = Teacher.query.filter_by(username=current_user.username).first()

   # Send email to all admins about the request to delete account
    admins = Admin.query.all()
    for admin in admins:
        request_account_deletion(admin, teacher)

    flash('Your request has been sent to the admins.'
          ' You will receive an email notification if approved')
    return redirect(url_for('teacher_profile'))




# Compose direct email to teacher

@app.route(
    '/dashboard/compose-direct-email/<email>',
    methods=['GET', 'POST'])
@login_required
def compose_direct_email_to_teacher(email):
    """Write email to individual teacher"""
    # Get the teacher
    teacher = Teacher.query.filter_by(email=email).first()
    teacher_username = teacher.email.split('@')[0].capitalize()
    session['teacher_email'] = teacher.email
    session['teacher_first_name'] = teacher.first_name

    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email = Email(
            subject=form.subject.data,
            body=form.body.data,
            closing=form.closing.data,
            signature=form.signature.data,
            bulk='Teacher Email',
            author=current_user)
        db.session.add(email)
        db.session.commit()
        flash(f'Sample private email to {teacher_username} saved')
        return redirect(url_for('emails_to_individual_teachers'))
    return render_template(
        'admin/email_teacher.html',
        title='Compose Private Email',
        form=form,
        teacher=teacher)


# List of emails sent out to individual teachers

@app.route('/dashboard/emails-to-individual-teachers')
@login_required
def emails_to_individual_teachers():
    """Emails sent out to individual teachers"""
    emails_sent_to_individual_teachers = Email.query.filter_by(
        bulk='Teacher Email').all()
    emails = len(emails_sent_to_individual_teachers)
    return render_template(
        'admin/individual_teacher_email.html',
        title='Emails Sent To Individual Teachers',
        emails_sent_to_individual_teachers=emails_sent_to_individual_teachers,
        emails=emails)


# List of all teachers

@app.route("/dashboard/all-teachers")
@login_required
def all_teachers():
    teachers = Teacher.query.all()
    all_registered_teachers = len(teachers)
    return render_template(
        "admin/all_teachers.html",
        title="All Teachers",
        teachers=teachers,
        all_registered_teachers=all_registered_teachers
    )


# Deactivate teacher

@app.route("/dashboard/deactivate-teacher/<username>")
@login_required
def deactivate_teacher(username):
    teacher = Teacher.query.filter_by(username=username).first_or_404()
    teacher.active = False
    db.session.add(teacher)
    db.session.commit()
    flash(f'{teacher.username} has been deactivated as a teacher')
    return redirect(url_for('all_teachers'))


# Reactivate admin

@app.route("/dashboard/reactivate-teacher/<username>")
@login_required
def reactivate_teacher(username):
    teacher = Teacher.query.filter_by(username=username).first_or_404()
    teacher.active = True
    db.session.add(teacher)
    db.session.commit()
    flash(f'{teacher.username} has been reactivated as a teacher')
    return redirect(url_for('all_teachers'))



# Delete teacher

@app.route("/dashboard/delete-teacher/<username>")
@login_required
def delete_teacher(username):
    teacher = Teacher.query.filter_by(username=username).first_or_404()
    db.session.delete(teacher)
    db.session.commit()
    flash(f'{teacher.username} has been deleted as a teacher')
    return redirect(url_for('all_teachers'))


# Send email to individual teacher

@app.route('/send-email-to-teacher/<id>')
@login_required
def send_teacher_email(id):
    """Send email to teacher from the database"""
    email = Email.query.filter_by(id=id).first()
    teacher_email = session['teacher_email']
    teacher_first_name = session['teacher_first_name']

    # Update db so that the email is not sent again
    email.allow = True
    db.session.add(email)
    db.session.commit()

    # Send email to user
    send_user_private_email(email, teacher_email, teacher_first_name)

    # Notify user that email has been sent
    flash(f'Email successfully sent to the teacher {teacher_email}')
    del session['teacher_email']
    del session['teacher_first_name']
    return redirect(url_for('emails_to_individual_teachers'))


# Edit sample email

@app.route('/edit-teacher-email/<id>', methods=['GET', 'POST'])
@login_required
def edit_teacher_email(id):
    """Edit email to teacher from the database"""
    email = Email.query.filter_by(id=id).first()
    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email.subject = form.subject.data
        email.body = form.body.data
        email.closing = form.closing.data
        email.signature = form.signature.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('emails_to_individual_teachers'))
    if request.method == 'GET':
        form.subject.data = email.subject
        form.body.data = email.body
        form.signature.data = email.signature
    return render_template(
        'admin/edit_email.html', title='Edit Sample Email', form=form)


# Delete email from database

@app.route('/delete-email-sent-to-a-teacher/<id>')
@login_required
def delete_teacher_email(id):
    """Delete email to user from the database"""
    email = Email.query.filter_by(id=id).first()
    db.session.delete(email)
    db.session.commit()
    flash('Email successfully deleted')
    del session['teacher_email']
    del session['teacher_first_name']
    return redirect(url_for('emails_to_individual_teachers'))


# --------------------------------------
# End of teacher profile
# --------------------------------------


# --------------------------------------
# Admin profile
# --------------------------------------


@app.route("/admin/profile")
@login_required
def admin_profile():
    return render_template(
        "admin/profile.html",
        title="Admin Profile"
    )


# Compose direct email to admin

@app.route(
    '/dashboard/compose-direct-email-to-an-admin/<email>',
    methods=['GET', 'POST'])
@login_required
def compose_direct_email_to_admin(email):
    """Write email to individual admin"""
    # Get the teacher
    admin = Admin.query.filter_by(email=email).first()
    admin_username = admin.email.split('@')[0].capitalize()
    session['admin_email'] = admin.email
    session['admin_first_name'] = admin.first_name

    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email = Email(
            subject=form.subject.data,
            body=form.body.data,
            closing=form.closing.data,
            signature=form.signature.data,
            bulk='Admin Email',
            author=current_user)
        db.session.add(email)
        db.session.commit()
        flash(f'Sample private email to {admin_username} saved')
        return redirect(url_for('emails_to_individual_admins'))
    return render_template(
        'admin/email_admin.html',
        title='Compose Private Email',
        form=form,
        admin=admin)


# List of emails sent out to individual admin

@app.route('/dashboard/emails-to-individual-admins')
@login_required
def emails_to_individual_admins():
    """Emails sent out to individual admins"""
    emails_sent_to_individual_admins = Email.query.filter_by(
        bulk='Admin Email').all()
    emails = len(emails_sent_to_individual_admins)
    return render_template(
        'admin/individual_admin_email.html',
        title='Emails Sent To Individual Admins',
        emails_sent_to_individual_admins=emails_sent_to_individual_admins,
        emails=emails)


# List all admins

@app.route("/dashboard/all-admins")
@login_required
def all_admins():
    admins = Admin.query.all()
    all_registered_admins = len(admins)
    return render_template(
        "admin/all_admins.html",
        title="All Admins",
        admins=admins,
        all_registered_admins=all_registered_admins
    )


# Deactivate admin

@app.route("/dashboard/deactivate-admin/<username>")
@login_required
def deactivate_admin(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    admin.active = False
    db.session.add(admin)
    db.session.commit()
    flash(f'{admin.username} has been deactivated as an admin')
    return redirect(url_for('all_admins'))


# Reactivate admin

@app.route("/dashboard/reactivate-admin/<username>")
@login_required
def reactivate_admin(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    admin.active = True
    db.session.add(admin)
    db.session.commit()
    flash(f'{admin.username} has been reactivated as an admin')
    return redirect(url_for('all_admins'))



# Delete admin

@app.route("/dashboard/delete-admin/<username>")
@login_required
def delete_admin(username):
    admin = Admin.query.filter_by(username=username).first_or_404()
    db.session.delete(admin)
    db.session.commit()
    flash(f'{admin.username} has been deleted as an admin')
    return redirect(url_for('all_admins'))


# Send email to individual admin

@app.route('/send-email-to-admin/<id>')
@login_required
def send_admin_email(id):
    """Send email to admin from the database"""
    email = Email.query.filter_by(id=id).first()
    admin_email = session['admin_email']
    admin_first_name = session['admin_first_name']

    # Update db so that the email is not sent again
    email.allow = True
    db.session.add(email)
    db.session.commit()

    # Send email to user
    send_user_private_email(email, admin_email, admin_first_name)

    # Notify user that email has been sent
    flash(f'Email successfully sent to the teacher {admin_email}')
    del session['admin_email']
    del session['admin_first_name']
    return redirect(url_for('emails_to_individual_admins'))


# Edit sample email

@app.route('/edit-admin-email/<id>', methods=['GET', 'POST'])
@login_required
def edit_admin_email(id):
    """Edit email to admin from the database"""
    email = Email.query.filter_by(id=id).first()
    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email.subject = form.subject.data
        email.body = form.body.data
        email.closing = form.closing.data
        email.signature = form.signature.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('emails_to_individual_admins'))
    if request.method == 'GET':
        form.subject.data = email.subject
        form.body.data = email.body
        form.signature.data = email.signature
    return render_template(
        'admin/edit_email.html', title='Edit Sample Email', form=form)


# Delete email from database

@app.route('/delete-email-sent-to-a-admin/<id>')
@login_required
def delete_admin_email(id):
    """Delete email to user from the database"""
    email = Email.query.filter_by(id=id).first()
    db.session.delete(email)
    db.session.commit()
    flash('Email successfully deleted')
    del session['admin_email']
    del session['admin_first_name']
    return redirect(url_for('emails_to_individual_admins'))


# --------------------------------------
# End of admin profile
# --------------------------------------


# --------------------------------------
# All managers
# --------------------------------------


# manager profile

@app.route("/manager/profile")
@login_required
def manager_profile():
    return render_template(
        "manager/profile.html",
        title="manager Profile"
    )


# Deactivate own account

@app.route('/manager/deactivate-account')
@login_required
def manager_deactivate_account():
    # Get current user
    manager = Teacher.query.filter_by(username=current_user.username).first()

   # Send email to all admins about the request to delete account
    admins = Admin.query.all()
    for admin in admins:
        request_account_deletion(admin, manager)

    flash('Your request has been sent to the admins.'
          ' You will receive an email notification if approved')
    return redirect(url_for('manager_profile'))




# Compose direct email to manager

@app.route(
    '/dashboard/compose-direct-email-to-a-manager/<email>',
    methods=['GET', 'POST'])
@login_required
def compose_direct_email_to_manager(email):
    """Write email to individual manager"""
    # Get the manager
    manager = manager.query.filter_by(email=email).first()
    manager_username = manager.email.split('@')[0].capitalize()
    session['manager_email'] = manager.email
    session['manager_first_name'] = manager.first_name

    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email = Email(
            subject=form.subject.data,
            body=form.body.data,
            closing=form.closing.data,
            signature=form.signature.data,
            bulk='manager Email',
            author=current_user)
        db.session.add(email)
        db.session.commit()
        flash(f'Sample private email to {manager_username} saved')
        return redirect(url_for('emails_to_individual_manager'))
    return render_template(
        'admin/email_manager.html',
        title='Compose Private Email',
        form=form,
        manager=manager)


# List of emails sent out to individual manager

@app.route('/dashboard/emails-to-individual-managers')
@login_required
def emails_to_individual_managers():
    """Emails sent out to individual managers"""
    emails_sent_to_individual_manager = Email.query.filter_by(
        bulk='manager Email').all()
    emails = len(emails_sent_to_individual_manager)
    return render_template(
        'admin/individual_manager_email.html',
        title='Emails Sent To Individual managers',
        emails_sent_to_individual_manager=emails_sent_to_individual_manager,
        emails=emails)


# List all managers

@app.route("/dashboard/all-managers")
@login_required
def all_managers():
    managers = manager.query.all()
    all_registered_managers = len(managers)
    return render_template(
        "admin/all_managers.html",
        title="All managers",
        managers=managers,
        all_registered_managers=all_registered_managers
    )


# Deactivate manager

@app.route("/dashboard/deactivate-manager/<username>")
@login_required
def deactivate_manager(username):
    manager = manager.query.filter_by(username=username).first_or_404()
    manager.active = False
    db.session.add(manager)
    db.session.commit()
    flash(f'{manager.username} has been deactivated as a manager')
    return redirect(url_for('all_managers'))


# Reactivate manager

@app.route("/dashboard/reactivate-manager/<username>")
@login_required
def reactivate_manager(username):
    manager = manager.query.filter_by(username=username).first_or_404()
    manager.active = True
    db.session.add(manager)
    db.session.commit()
    flash(f'{manager.username} has been reactivated as a manager')
    return redirect(url_for('all_managers'))



# Delete manager

@app.route("/dashboard/delete-manager/<username>")
@login_required
def delete_manager(username):
    manager = manager.query.filter_by(username=username).first_or_404()
    db.session.delete(manager)
    db.session.commit()
    flash(f'{manager.username} has been deleted as a manager')
    return redirect(url_for('all_managers'))


# Send email to individual manager

@app.route('/send-email-to-manager/<id>')
@login_required
def send_manager_email(id):
    """Send email to manager from the database"""
    email = Email.query.filter_by(id=id).first()
    manager_email = session['manager_email']
    manager_first_name = session['manager_first_name']

    # Update db so that the email is not sent again
    email.allow = True
    db.session.add(email)
    db.session.commit()

    # Send email to user
    send_user_private_email(email, manager_email, manager_first_name)

    # Notify user that email has been sent
    flash(f'Email successfully sent to the teacher {manager_email}')
    del session['manager_email']
    del session['manager_first_name']
    return redirect(url_for('emails_to_individual_managers'))


# Edit sample email

@app.route('/edit-manager-email/<id>', methods=['GET', 'POST'])
@login_required
def edit_manager_email(id):
    """Edit email to manager from the database"""
    email = Email.query.filter_by(id=id).first()
    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email.subject = form.subject.data
        email.body = form.body.data
        email.closing = form.closing.data
        email.signature = form.signature.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('emails_to_individual_managers'))
    if request.method == 'GET':
        form.subject.data = email.subject
        form.body.data = email.body
        form.signature.data = email.signature
    return render_template(
        'admin/edit_email.html', title='Edit Sample Email', form=form)


# Delete email from database

@app.route('/delete-email-sent-to-a-manager/<id>')
@login_required
def delete_manager_email(id):
    """Delete email to Manager from the database"""
    email = Email.query.filter_by(id=id).first()
    db.session.delete(email)
    db.session.commit()
    flash('Email successfully deleted')
    del session['manager_email']
    del session['manager_first_name']
    return redirect(url_for('emails_to_individual_managers'))


# --------------------------------------
# End of all managers
# --------------------------------------


# --------------------------------------
# All Employees
# --------------------------------------


# Employee profile

@app.route("/Employee/profile", methods=['GET', 'POST'])
@login_required
def Employee_profile():
    # Profile edits
    username_form = EditUsernameForm()
    email_form = EditEmailForm()
    phone_form = EditPhoneForm()

    if request.method == 'GET':
        username_form.username.data = current_user.username
        email_form.email.data = current_user.email
        phone_form.phone.data = current_user.phone_number
    if username_form.validate_on_submit() and username_form.username.data:
        current_user.username = username_form.username.data
        db.session.commit()
        flash('Username updated.')
        return redirect(url_for('Employee_profile'))
    if email_form.validate_on_submit() and email_form.email.data:
        current_user.email = email_form.email.data
        db.session.commit()
        flash('Email updated.')
        return redirect(url_for('Employee_profile'))
    if phone_form.validate_on_submit() and phone_form.phone.data:
        current_user.phone_number = phone_form.phone.data
        db.session.commit()
        flash('Phone number updated.')
        return redirect(url_for('Employee_profile'))
    return render_template(
        "Employee/profile.html",
        title="Employee Profile",
        username_form=username_form,
        email_form=email_form,
        phone_form=phone_form
    )


@app.route('/Employee/deactivate-account')
@login_required
def Employee_deactivate_account():
    # Get current user
    Employee = Employee.query.filter_by(username=current_user.username).first()

   # Send email to all admins about the request to delete account
    admins = Admin.query.all()
    for admin in admins:
        request_account_deletion(admin, Employee)

    flash('Your request has been sent to the admins.'
          ' You will receive an email notification if approved')
    return redirect(url_for('Employee_profile'))



# Compose direct email to Employee

@app.route(
    '/dashboard/compose-direct-email-to-a-Employee/<email>',
    methods=['GET', 'POST'])
@login_required
def compose_direct_email_to_Employee(email):
    """Write email to individual Employee"""
    # Get the manager
    Employee = Employee.query.filter_by(email=email).first()
    Employee_username = Employee.email.split('@')[0].capitalize()
    session['Employee_email'] = Employee.email
    session['Employee_first_name'] = Employee.first_name

    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email = Email(
            subject=form.subject.data,
            body=form.body.data,
            closing=form.closing.data,
            signature=form.signature.data,
            bulk='Employee Email',
            author=current_user)
        db.session.add(email)
        db.session.commit()
        flash(f'Sample private email to {Employee_username} saved')
        return redirect(url_for('emails_to_individual_Employee'))
    return render_template(
        'admin/email_Employee.html',
        title='Compose Private Email',
        form=form,
        Employee=Employee)


# List of emails sent out to individual Employee

@app.route('/dashboard/emails-to-individual-Employees')
@login_required
def emails_to_individual_Employees():
    """Emails sent out to individual Employee"""
    emails_sent_to_individual_Employee = Email.query.filter_by(
        bulk='Employee Email').all()
    emails = len(emails_sent_to_individual_Employee)
    return render_template(
        'admin/individual_Employee_email.html',
        title='Emails Sent To Individual Employees',
        emails_sent_to_individual_Employee=emails_sent_to_individual_Employee,
        emails=emails)



@app.route("/dashboard/all-Employees")
@login_required
def all_Employees():
    Employees = Employee.query.all()
    all_registered_Employees = len(Employees)
    return render_template(
        "admin/all_Employees.html",
        title="All Employees",
        Employees=Employees,
        all_registered_Employees=all_registered_Employees
    )


# Deactivate Employee

@app.route("/dashboard/deactivate-Employee/<username>")
@login_required
def deactivate_Employee(username):
    Employee = Employee.query.filter_by(username=username).first_or_404()
    Employee.active = False
    db.session.add(Employee)
    db.session.commit()
    flash(f'{Employee.username} has been deactivated as a Employee')
    return redirect(url_for('all_Employees'))


# Reactivate Employee

@app.route("/dashboard/reactivate-Employee/<username>")
@login_required
def reactivate_Employee(username):
    Employee = Employee.query.filter_by(username=username).first_or_404()
    Employee.active = True
    db.session.add(Employee)
    db.session.commit()
    flash(f'{Employee.username} has been reactivated as a Employee')
    return redirect(url_for('all_Employees'))



# Delete Employee

@app.route("/dashboard/delete-Employee/<username>")
@login_required
def delete_Employee(username):
    Employee = Employee.query.filter_by(username=username).first_or_404()
    db.session.delete(Employee)
    db.session.commit()
    flash(f'{Employee.username} has been deleted as a Employee')
    return redirect(url_for('all_Employees'))


# Send email to individual Employee

@app.route('/send-email-to-Employee/<id>')
@login_required
def send_Employee_email(id):
    """Send email to Employee from the database"""
    email = Email.query.filter_by(id=id).first()
    Employee_email = session['Employee_email']
    Employee_first_name = session['Employee_first_name']

    # Update db so that the email is not sent again
    email.allow = True
    db.session.add(email)
    db.session.commit()

    # Send email to user
    send_user_private_email(email, Employee_email, Employee_first_name)

    # Notify user that email has been sent
    flash(f'Email successfully sent to the teacher {Employee_email}')
    del session['Employee_email']
    del session['Employee_first_name']
    return redirect(url_for('emails_to_individual_Employees'))


# Edit sample email

@app.route('/edit-Employee-email/<id>', methods=['GET', 'POST'])
@login_required
def edit_Employee_email(id):
    """Edit email to Employee from the database"""
    email = Email.query.filter_by(id=id).first()
    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email.subject = form.subject.data
        email.body = form.body.data
        email.closing = form.closing.data
        email.signature = form.signature.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('emails_to_individual_Employees'))
    if request.method == 'GET':
        form.subject.data = email.subject
        form.body.data = email.body
        form.signature.data = email.signature
    return render_template(
        'admin/edit_email.html', title='Edit Sample Email', form=form)


# Delete email from database

@app.route('/delete-email-sent-to-a-Employee/<id>')
@login_required
def delete_Employee_email(id):
    """Delete email to Employee from the database"""
    email = Email.query.filter_by(id=id).first()
    db.session.delete(email)
    db.session.commit()
    flash('Email successfully deleted')
    del session['Employee_email']
    del session['Employee_first_name']
    return redirect(url_for('emails_to_individual_Employees'))


# --------------------------------------
# End of all Employees
# --------------------------------------


# --------------------------------------
# Bulk emails
# --------------------------------------


# Bulk emails to all teachers

@app.route("/dashboard/bulk-emails/teachers")
@login_required
def bulk_emails_teachers():
    bulk_emails_sent_to_all_teachers = Email.query.filter_by(
        bulk='manager Email').all()
    emails = len(bulk_emails_sent_to_all_teachers)
    return render_template(
        "admin/bulk_emails_teachers.html",
        title="Bulk Emails Sent To All Teachers",
        bulk_emails_sent_to_all_teachers=bulk_emails_sent_to_all_teachers,
        emails=emails
    )


# Bulk emails to all admins

@app.route("/dashboard/bulk-emails/admins")
@login_required
def bulk_emails_admins():
    bulk_emails_sent_to_all_admins = Email.query.filter_by(
        bulk='Admin Email').all()
    emails = len(bulk_emails_sent_to_all_admins)
    return render_template(
        "admin/bulk_emails_admins.html",
        title="Bulk Emails Sent To All Admins",
        bulk_emails_sent_to_all_admins=bulk_emails_sent_to_all_admins,
        emails=emails
    )


# Bulk emails to all managers

@app.route("/dashboard/bulk-emails/managers")
@login_required
def bulk_emails_managers():
    bulk_emails_sent_to_all_managers = Email.query.filter_by(
        bulk='manager Email').all()
    emails = len(bulk_emails_sent_to_all_managers)
    return render_template(
        "admin/bulk_emails_managers.html",
        title="Bulk Emails Sent To All managers",
        bulk_emails_sent_to_all_managers=bulk_emails_sent_to_all_managers,
        emails=emails
    )


# Bulk emails to all Employees

@app.route("/dashboard/bulk-emails/Employees")
@login_required
def bulk_emails_Employees():
    bulk_emails_sent_to_all_Employees = Email.query.filter_by(
        bulk='manager Email').all()
    emails = len(bulk_emails_sent_to_all_Employees)
    return render_template(
        "admin/bulk_emails_Employees.html",
        title="Bulk Emails Sent To All Employees",
        bulk_emails_sent_to_all_Employees=bulk_emails_sent_to_all_Employees,
        emails=emails
    )



# --------------------------------------
# End of bulk emails
# --------------------------------------


# ----------------------------------------
# Newsletter subscribers
# ----------------------------------------


@app.route("/dashboard/all-newsletter-subscribers")
@login_required
def newsletter_subscribers():
    subscribers = Newsletter_Subscriber.query.order_by(
        Newsletter_Subscriber.email_confirmed_at.desc()).all()
    num_subscribers = len(subscribers)
    return render_template(
        "admin/all_newsletter_subscribers.html",
        title="Newsletter Subscribers",
        subscribers=subscribers, 
        num_subscribers=num_subscribers
    )



# Resubscribe

@app.route('/newsletter/resubscription/<email>')
@login_required
def resubscribe_newsletter_subscriber(email):
    """Resubscribe the client to continue receiving newsletters"""
    subscriber = Newsletter_Subscriber.query.filter_by(email=email).first()
    subscriber.active = True
    db.session.commit()
    flash('The subscriber can now continue receiving newsletters')
    return redirect(url_for('email_newsletter_subscribers'))


# Delete subscriber

@app.route('/newsletter/delete/<email>')
@login_required
def delete_newsletter_subscriber(email):
    """Permanently delete client from the database"""
    subscriber = Newsletter_Subscriber.query.filter_by(email=email).first()
    db.session.delete(subscriber)
    db.session.commit()
    flash('The subscriber can now continue receiving newsletters')
    return redirect(url_for('email_newsletter_subscribers'))


# Compose direct email

@app.route(
    '/newsletter/compose-direct-email/<email>',
    methods=['GET', 'POST'])
@login_required
def newsletter_subscriber_compose_direct_email(email):
    """Write email to individual newsletter subscriber"""
    # Get the client (newsletter)
    subscriber = Newsletter_Subscriber.query.filter_by(email=email).first()
    session['subscriber'] = subscriber.email
    subscriber_username = subscriber.email.split('@')[0].capitalize()

    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email = Email(
            subject=form.subject.data,
            body=form.body.data,
            closing=form.closing.data,
            signature=form.signature.data,
            bulk='Newsletter Subscriber',
            author=current_user)
        db.session.add(email)
        db.session.commit()
        flash(f'Sample private email to {subscriber_username} saved')
        return redirect(url_for('newsletter_subscribers_email_sent_out'))
    return render_template(
        'admin/email_newsletter_subscriber.html',
        title='Compose Private Email',
        form=form,
        subscriber=subscriber)

# ----------------------------------------
# End of Newsletter subscribers
# ----------------------------------------


# ---------------------------------------
# SAMPLE EMAILS
# ---------------------------------------


# List of individual emails sent out

@app.route('/newsletter/individual-email-to-newsletter-subscriber')
@login_required
def newsletter_subscribers_email_sent_out():
    """Emails sent out to individual newsletter subscribers"""
    emails_sent_to_newsletter_subscribers = Email.query.filter_by(
        bulk='Newsletter Subscriber').all()
    emails = len(emails_sent_to_newsletter_subscribers)
    return render_template(
        'admin/individual_newsletter_subscribers_email.html',
        title='Individual Emails Sent To Newsletter Subscribers',
        emails_sent_to_newsletter_subscribers=emails_sent_to_newsletter_subscribers,
        emails=emails)


# Send email to individual subscriber

@app.route('/newsletter/send-email/<id>')
@login_required
def send_email(id):
    """Send email to subscriber from the database"""
    email = Email.query.filter_by(id=id).first()
    subscriber_email = session['subscriber']

    # Update db so that the email is not sent again
    email.allow = True
    db.session.add(email)
    db.session.commit()

    # Send email to subscriber
    subscriber_username = session['subscriber'].split('@')[0].capitalize()
    send_subscriber_private_email(email, subscriber_email, subscriber_username)

    # Notify user that email has been sent
    flash(f'Email successfully sent to {subscriber_email}')
    del session['subscriber']
    return redirect(url_for('newsletter_subscribers_email_sent_out'))


# Edit sample email

@app.route('/edit-email/<id>', methods=['GET', 'POST'])
@login_required
def edit_email(id):
    """Edit email to user from the database"""
    email = Email.query.filter_by(id=id).first()
    form = EmailForm()
    form.signature.choices = [
        (current_user.first_name.capitalize(), current_user.first_name.capitalize())]
    if form.validate_on_submit():
        email.subject = form.subject.data
        email.body = form.body.data
        email.closing = form.closing.data
        email.signature = form.signature.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('newsletter_subscribers_email_sent_out'))
    if request.method == 'GET':
        form.subject.data = email.subject
        form.body.data = email.body
        form.signature.data = email.signature
    return render_template(
        'admin/edit_email.html', title='Edit Sample Email', form=form)


# Delete email from database

@app.route('/delete-email/<id>')
@login_required
def delete_email(id):
    """Delete email to user from the database"""
    email = Email.query.filter_by(id=id).first()
    db.session.delete(email)
    db.session.commit()
    flash('Email successfully deleted')
    del session['subscriber']
    return redirect(url_for('newsletter_subscribers_email_sent_out'))


# ==========
# END OF DASHBOARD
# ==========




# =========================================
# END OF AUTHENTICATED USERS
# =========================================


# =========================================
# LESSONS
# =========================================

# ----------------
# Flask
# ----------------


@app.route('/dashboard/flask/chapter-1/install-configure-git')
@login_required
def flask_chapter1():
    return render_template(
        'admin/lessons/flask/1_install_configure_git.html',
        title='Install and Configure Git In Ubuntu'
    )



@app.route('/dashboard/flask/chapter-2/virtualenvwrapper', methods=['GET', 'POST'])
@login_required
def flask_chapter2():
    form = FlaskChapter2QuizForm()
    if form.validate_on_submit():

        # Frst, delete everything from the db to remove duplicate
        Chapter2Quiz.query.delete()
        db.session.commit()

        # Then, add new response
        quiz = Chapter2Quiz(
            question1=form.question1.data,
            question2=form.question2.data,
            question3=form.question3.data,
            question4=form.question4.data,
            author=current_user
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Your answers have been assessed successfully!')
        return redirect(url_for('flask_chapter2', _anchor='quiz'))

    # Get correct answer and present it to the Employee
    correct_answers = []
    answers = Chapter2Quiz.query.all()
    for answer in answers:
        if answer.question1 == '<a>':
            correct_answers.append(answer.question1)
        if answer.question2 == '<head>':
            correct_answers.append(answer.question2)
        if answer.question3 == 'p{color: orange;}':
            correct_answers.append(answer.question3)
        if answer.question4 == 'a{text-decoration: none;}':
            correct_answers.append(answer.question3)
    score = len(correct_answers)
    return render_template(
        'admin/lessons/flask/2_virtualenvwrapper.html',
        title='Work With Virtualenvwrapper',
        form=form,
        score=score
    )



@app.route('/dashboard/flask/chapter-3/start-flas-server', methods=['GET', 'POST'])
@login_required
def flask_chapter3():

    # Frst, delete everything from the db to remove duplicate
    Chapter2Quiz.query.delete()
    db.session.commit()

    form = FlaskChapter3QuizForm()
    if form.validate_on_submit():
        quiz = Chapter3Quiz(
            question1=form.question1.data,
            question2=form.question2.data,
            question3=form.question3.data,
            question4=form.question4.data,
            author=current_user
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Your answers have been assessed successfully!')

    # Get correct answer and present it to the Employee
    correct_answers = []
    answers = Chapter3Quiz.query.all()
    for answer in answers:
        if answer.question1 == 'Git':
            correct_answers.append(answer.question1)
        if answer.question2 == 'git status':
            correct_answers.append(answer.question2)
        if answer.question3 == 'git add <you-filename.ext>':
            correct_answers.append(answer.question3)
        if answer.question4 == 'git init':
            correct_answers.append(answer.question3)
    score = len(correct_answers)
    return render_template(
        'admin/lessons/flask/3_start_flask_server.html',
        title='Start Flask Server',
        form=form,
        score=score
    )



@app.route('/dashboard/flask/chapter-4/connect-to-github', methods=['GET', 'POST'])
@login_required
def flask_chapter4():

    # Frst, delete everything from the db to remove duplicate
    Chapter2Quiz.query.delete()
    db.session.commit()

    form = FlaskChapter4QuizForm()
    if form.validate_on_submit():
        quiz = Chapter4Quiz(
            question1=form.question1.data,
            question2=form.question2.data,
            question3=form.question3.data,
            question4=form.question4.data,
            author=current_user
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Your answers have been assessed successfully!')

    # Get correct answer and present it to the Employee
    correct_answers = []
    answers = Chapter4Quiz.query.all()
    for answer in answers:
        if answer.question1 == 'Python':
            correct_answers.append(answer.question1)
        if answer.question2 == 'python3 -m venv venv':
            correct_answers.append(answer.question2)
        if answer.question3 == '.gitignore':
            correct_answers.append(answer.question3)
        if answer.question4 == 'git init':
            correct_answers.append(answer.question3)
    score = len(correct_answers)
    return render_template(
        'admin/lessons/flask/4_connect_to_github.html',
        title='Connect To GitHub',
        form=form,
        score=score
    )


# ----------------
# End of Flask
# ----------------


# ----------------
# React
# ----------------


@app.route('/dashboard/react/chapter-1/lorem-ipsum')
@login_required
def react_chapter1():
    return render_template(
        'admin/lessons/react/1_lorem_ipsum.html',
        title='Chapter 1 React'
    )



@app.route('/dashboard/react/chapter-2/lorem-ipsum')
@login_required
def react_chapter2():
    return render_template(
        'admin/lessons/react/2_lorem_ipsum.html',
        title='Chapter 2 React'
    )


# ----------------
# End of React
# ----------------



# =========================================
# END OF LESSONS
# =========================================
