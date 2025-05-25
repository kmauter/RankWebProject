"""Make owner nullable

Revision ID: 629557ae9a6e
Revises: 6507b0e3aadf
Create Date: 2025-05-25 16:55:01.569831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '629557ae9a6e'
down_revision = '6507b0e3aadf'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('Game') as batch_op:
        batch_op.add_column(sa.Column('owner', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_game_owner_user_id', 'User', ['owner'], ['id'])

    # Set all existing games to owner id 1 (make sure user with id=1 exists!)
    op.execute('UPDATE "Game" SET owner = 1')

    # Now make the column non-nullable
    with op.batch_alter_table('Game') as batch_op:
        batch_op.alter_column('owner', nullable=False)

def downgrade():
    with op.batch_alter_table('Game') as batch_op:
        batch_op.drop_constraint('fk_game_owner_user_id', type_='foreignkey')
        batch_op.drop_column('owner')
