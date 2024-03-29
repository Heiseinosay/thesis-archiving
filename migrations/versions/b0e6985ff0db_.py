"""empty message

Revision ID: b0e6985ff0db
Revises: 54699bbef92e
Create Date: 2021-08-08 18:29:22.530097

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b0e6985ff0db'
down_revision = '54699bbef92e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('individual_rating', sa.Column('student_id', mysql.INTEGER(unsigned=True), nullable=False))
    op.add_column('individual_rating', sa.Column('panelist_id', mysql.INTEGER(unsigned=True), nullable=False))
    op.create_foreign_key(None, 'individual_rating', 'user', ['panelist_id'], ['id'])
    op.create_foreign_key(None, 'individual_rating', 'user', ['student_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'individual_rating', type_='foreignkey')
    op.drop_constraint(None, 'individual_rating', type_='foreignkey')
    op.drop_column('individual_rating', 'panelist_id')
    op.drop_column('individual_rating', 'student_id')
    # ### end Alembic commands ###
