"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-15
"""

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('passport_number', sa.String(50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('passport_number')
    )
    op.create_index('ix_customers_id', 'customers', ['id'])

    op.create_table('rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(10), nullable=False),
        sa.Column('room_type', sa.String(20), nullable=False),
        sa.Column('price_per_night', sa.Float(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False),
        sa.Column('has_view', sa.Boolean(), default=False),
        sa.Column('has_wifi', sa.Boolean(), default=True),
        sa.Column('has_ac', sa.Boolean(), default=True),
        sa.Column('status', sa.String(20), default='available'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_number')
    )
    op.create_index('ix_rooms_id', 'rooms', ['id'])

    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('check_out_date', sa.Date(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.Date(), nullable=True),
        sa.Column('special_requests', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bookings_id', 'bookings', ['id'])

def downgrade():
    op.drop_table('bookings')
    op.drop_table('rooms')
    op.drop_table('customers')