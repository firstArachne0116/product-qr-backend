"""add Asset table

Revision ID: 7ee2448c3e8b
Revises: 818859c4f96b
Create Date: 2021-11-14 21:41:44.011167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ee2448c3e8b'
down_revision = '818859c4f96b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('asset',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_id'), 'asset', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_asset_id'), table_name='asset')
    op.drop_table('asset')
    # ### end Alembic commands ###