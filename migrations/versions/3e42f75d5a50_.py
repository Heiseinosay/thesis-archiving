"""empty message

Revision ID: 3e42f75d5a50
Revises: 669a0c404923
Create Date: 2021-08-07 20:43:26.432010

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3e42f75d5a50'
down_revision = '669a0c404923'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quantitative_rating',
    sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quantitative_criteria',
    sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('quantitative_rating_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.ForeignKeyConstraint(['quantitative_rating_id'], ['quantitative_rating.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quantitative_panelist_grade',
    sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('is_final', sa.BOOLEAN(), nullable=False),
    sa.Column('panelist_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('thesis_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.ForeignKeyConstraint(['panelist_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['thesis_id'], ['thesis.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quantitative_criteria_grade',
    sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('grade', sa.Integer(), nullable=True),
    sa.Column('quantitative_criteria_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.Column('quantitative_panelist_grade_id', mysql.INTEGER(unsigned=True), nullable=False),
    sa.ForeignKeyConstraint(['quantitative_criteria_id'], ['quantitative_criteria.id'], ),
    sa.ForeignKeyConstraint(['quantitative_panelist_grade_id'], ['quantitative_panelist_grade.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('thesis', sa.Column('quantitative_rating_id', mysql.INTEGER(unsigned=True), nullable=True))
    op.create_foreign_key(None, 'thesis', 'quantitative_rating', ['quantitative_rating_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'thesis', type_='foreignkey')
    op.drop_column('thesis', 'quantitative_rating_id')
    op.drop_table('quantitative_criteria_grade')
    op.drop_table('quantitative_panelist_grade')
    op.drop_table('quantitative_criteria')
    op.drop_table('quantitative_rating')
    # ### end Alembic commands ###
