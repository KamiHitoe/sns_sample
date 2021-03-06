"""add messages

Revision ID: 9ff925066f71
Revises: fc035a05cebf
Create Date: 2021-06-18 01:54:08.306168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ff925066f71'
down_revision = 'fc035a05cebf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_user_id', sa.Integer(), nullable=True),
    sa.Column('to_user_id', sa.Integer(), nullable=True),
    sa.Column('is_read', sa.Boolean(), nullable=True),
    sa.Column('is_checked', sa.Boolean(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['to_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_from_user_id'), 'messages', ['from_user_id'], unique=False)
    op.create_index(op.f('ix_messages_to_user_id'), 'messages', ['to_user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_to_user_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_from_user_id'), table_name='messages')
    op.drop_table('messages')
    # ### end Alembic commands ###
