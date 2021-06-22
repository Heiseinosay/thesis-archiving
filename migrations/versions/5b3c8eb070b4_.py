"""empty message

Revision ID: 5b3c8eb070b4
Revises: 3e56758c3859
Create Date: 2021-06-19 22:24:02.029850

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5b3c8eb070b4'
down_revision = '3e56758c3859'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('log', 'description',
               existing_type=mysql.VARCHAR(length=120),
               type_=sa.String(length=60),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('log', 'description',
               existing_type=sa.String(length=60),
               type_=mysql.VARCHAR(length=120),
               existing_nullable=False)
    # ### end Alembic commands ###