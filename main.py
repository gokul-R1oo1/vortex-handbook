from app import app, db
from app import cli
from app.models import User, manager, Employee, Teacher, Admin, Newsletter_Subscriber,\
    Email, Chapter2Quiz, Chapter3Quiz, Chapter4Quiz


cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Admin=Admin,
        Teacher=Teacher,
        manager=manager,
        Employee=Employee,
        Newsletter_Subscriber=Newsletter_Subscriber,
        Email=Email,
        Chapter2Quiz=Chapter2Quiz,
        Chapter3Quiz=Chapter3Quiz,
        Chapter4Quiz=Chapter4Quiz
        )
