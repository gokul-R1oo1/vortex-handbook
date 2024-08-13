"""all tables

Revision ID: 68f9f61e83af
Revises: 
Create Date: 2023-03-04 23:34:15.102578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '68f9f61e83af'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('num_newsletter', sa.Integer(), nullable=False),
    sa.Column('email_confirmed_at', sa.DateTime(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_client_email'), ['email'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('verification_phone', sa.String(length=20), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('delete_account', sa.Boolean(), nullable=True),
    sa.Column('registered_at', sa.DateTime(), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_first_name'), ['first_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_last_name'), ['last_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('admin',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('current_residence', sa.String(length=64), nullable=True),
    sa.Column('department', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('manager',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('current_residence', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teacher',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course', sa.String(length=64), nullable=True),
    sa.Column('current_residence', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Employee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('school', sa.String(length=64), nullable=True),
    sa.Column('coding_experience', sa.String(length=64), nullable=True),
    sa.Column('program', sa.String(length=64), nullable=True),
    sa.Column('program_schedule', sa.String(length=64), nullable=True),
    sa.Column('cohort', sa.Integer(), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['manager_id'], ['manager.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Employee_attendance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Employee_first_name', sa.String(length=64), nullable=False),
    sa.Column('program', sa.String(length=64), nullable=True),
    sa.Column('cohort', sa.String(length=64), nullable=True),
    sa.Column('program_schedule', sa.String(length=64), nullable=True),
    sa.Column('lesson_number', sa.Integer(), nullable=True),
    sa.Column('hours', sa.Integer(), nullable=True),
    sa.Column('lesson_date', sa.DateTime(), nullable=False),
    sa.Column('teacher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['teacher_id'], ['teacher.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('Employee_attendance', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_Employee_attendance_Employee_first_name'), ['Employee_first_name'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Employee_attendance', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_Employee_attendance_Employee_first_name'))

    op.drop_table('Employee_attendance')
    op.drop_table('Employee')
    op.drop_table('teacher')
    op.drop_table('manager')
    op.drop_table('admin')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_last_name'))
        batch_op.drop_index(batch_op.f('ix_user_first_name'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_client_email'))

    op.drop_table('client')
    # ### end Alembic commands ###
