"""Create bookings table with no-overlap rule

Revision ID: a1c3e5f7b9d2
Revises: 
Create Date: 2026-10-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1c3e5f7b9d2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('bkg_bookings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('resource_id', sa.Uuid(), nullable=False),
    sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('cancellation_reason', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('end_at > start_at', name='bkg_bookings_valid_slot'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bkg_bookings_resource_id'), 'bkg_bookings', ['resource_id'], unique=False)
    op.create_index(op.f('ix_bkg_bookings_status'), 'bkg_bookings', ['status'], unique=False)
    op.create_index(op.f('ix_bkg_bookings_user_id'), 'bkg_bookings', ['user_id'], unique=False)

    # Regla clave repetida en la base de datos: dos reservas activas (PENDING o
    # CONFIRMED) del mismo recurso no pueden solaparse. Cubre las carreras entre
    # peticiones concurrentes que la validación del caso de uso no puede ver.
    if op.get_context().dialect.name == 'postgresql':
        op.execute('CREATE EXTENSION IF NOT EXISTS btree_gist')
        op.execute(
            """
            ALTER TABLE bkg_bookings
            ADD CONSTRAINT bkg_bookings_no_overlap
            EXCLUDE USING gist (
                resource_id WITH =,
                tstzrange(start_at, end_at, '[)') WITH &&
            )
            WHERE (status IN ('PENDING', 'CONFIRMED'))
            """
        )


def downgrade() -> None:
    """Downgrade schema."""
    if op.get_context().dialect.name == 'postgresql':
        op.execute('ALTER TABLE bkg_bookings DROP CONSTRAINT IF EXISTS bkg_bookings_no_overlap')
    op.drop_index(op.f('ix_bkg_bookings_user_id'), table_name='bkg_bookings')
    op.drop_index(op.f('ix_bkg_bookings_status'), table_name='bkg_bookings')
    op.drop_index(op.f('ix_bkg_bookings_resource_id'), table_name='bkg_bookings')
    op.drop_table('bkg_bookings')
