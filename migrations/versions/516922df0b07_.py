"""empty message

Revision ID: 516922df0b07
Revises: 730375abcb03
Create Date: 2020-08-02 23:08:45.845998

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '516922df0b07'
down_revision = '730375abcb03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('firstName', sa.String(length=120), nullable=False))
    op.add_column('user', sa.Column('lastName', sa.String(length=120), nullable=False))
    op.create_unique_constraint(None, 'user', ['firstName'])
    op.create_unique_constraint(None, 'user', ['lastName'])
    op.drop_column('user', 'is_active')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'lastName')
    op.drop_column('user', 'firstName')
    # ### end Alembic commands ###
