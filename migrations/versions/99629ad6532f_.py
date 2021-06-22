"""empty message

Revision ID: 99629ad6532f
Revises: 5b3c8eb070b4
Create Date: 2021-06-21 16:27:51.861497

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '99629ad6532f'
down_revision = '5b3c8eb070b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('thesis',
    sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('title', sa.String(length=250), nullable=False),
    sa.Column('is_old', sa.BOOLEAN(), nullable=False),
    sa.Column('overview', sa.String(length=500), nullable=True),
    sa.Column('area', sa.String(length=120), nullable=True),
    sa.Column('keywords', sa.String(length=120), nullable=True),
    sa.Column('sy_start', sa.Integer(), nullable=True),
    sa.Column('semester', sa.Integer(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('date_deployed', sa.DateTime(), nullable=True),
    sa.Column('date_registered', sa.DateTime(), nullable=False),
    sa.Column('adviser_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('category_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('program_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.ForeignKeyConstraint(['adviser_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['program.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('proponents',
    sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
    sa.Column('thesis_id', mysql.INTEGER(unsigned=True), nullable=True),
    sa.ForeignKeyConstraint(['thesis_id'], ['thesis.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('proponents')
    op.drop_table('thesis')
    # ### end Alembic commands ###