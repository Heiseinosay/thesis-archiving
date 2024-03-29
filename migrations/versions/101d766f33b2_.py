"""empty message

Revision ID: 101d766f33b2
Revises: ae44d4d75295
Create Date: 2021-08-07 21:41:24.705773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '101d766f33b2'
down_revision = 'ae44d4d75295'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('thesis', sa.Column('date_defense', sa.DateTime(), nullable=True))
    op.add_column('thesis', sa.Column('qualitative_rating', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('thesis', 'qualitative_rating')
    op.drop_column('thesis', 'date_defense')
    # ### end Alembic commands ###
