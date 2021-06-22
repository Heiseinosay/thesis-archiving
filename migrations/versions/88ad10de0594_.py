"""empty message

Revision ID: 88ad10de0594
Revises: 365e6c958241
Create Date: 2021-06-21 18:02:18.181642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88ad10de0594'
down_revision = '365e6c958241'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'thesis', ['number'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'thesis', type_='unique')
    # ### end Alembic commands ###