"""initial_schema

Revision ID: e25761c04161
Revises: 
Create Date: 2025-05-09 00:13:23.833295

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'e25761c04161'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create colorants table
    op.create_table(
        'colorants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_colorants_id'), 'colorants', ['id'], unique=False)
    op.create_index(op.f('ix_colorants_name'), 'colorants', ['name'], unique=True)

    # Create formulations table
    op.create_table(
        'formulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('color_code', sa.String(length=50), nullable=False),
        sa.Column('colorant_type', sa.String(length=100), nullable=True),
        sa.Column('color_series', sa.String(length=100), nullable=True),
        sa.Column('color_card', sa.String(length=100), nullable=True),
        sa.Column('paint_type', sa.String(length=100), nullable=True),
        sa.Column('base_paint', sa.String(length=100), nullable=True),
        sa.Column('packaging_spec', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('color_code', 'paint_type', 'base_paint', name='uq_formulation_key')
    )
    op.create_index(op.f('ix_formulations_id'), 'formulations', ['id'], unique=False)
    op.create_index(op.f('ix_formulations_color_code'), 'formulations', ['color_code'], unique=False)
    op.create_index(op.f('ix_formulations_paint_type'), 'formulations', ['paint_type'], unique=False)
    op.create_index(op.f('ix_formulations_base_paint'), 'formulations', ['base_paint'], unique=False)

    # Create colorant_details table
    op.create_table(
        'colorant_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('formulation_id', sa.Integer(), nullable=False),
        sa.Column('colorant_name', sa.String(length=100), nullable=False),
        sa.Column('weight_g', sa.Numeric(precision=12, scale=7), nullable=True),
        sa.Column('volume_ml', sa.Numeric(precision=12, scale=7), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['formulation_id'], ['formulations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('formulation_id', 'colorant_name', name='colorant_details_formulation_id_colorant_name_key')
    )
    op.create_index(op.f('ix_colorant_details_id'), 'colorant_details', ['id'], unique=False)
    op.create_index(op.f('ix_colorant_details_formulation_id'), 'colorant_details', ['formulation_id'], unique=False)
    op.create_index('idx_colorant_details_formulation_id', 'colorant_details', ['formulation_id'], unique=False)

    # Create color_rgb_values table
    op.create_table(
        'color_rgb_values',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('color_code', sa.String(length=50), nullable=False),
        sa.Column('color_card', sa.String(length=50), nullable=False),
        sa.Column('red', sa.Integer(), nullable=False),
        sa.Column('green', sa.Integer(), nullable=False),
        sa.Column('blue', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('color_code', 'color_card', name='color_rgb_values_color_code_card_key')
    )
    op.create_index(op.f('ix_color_rgb_values_id'), 'color_rgb_values', ['id'], unique=False)
    op.create_index('idx_color_rgb_values_code_card', 'color_rgb_values', ['color_code', 'color_card'], unique=False)


def downgrade():
    # Drop tables in reverse order of creation to respect foreign key constraints
    op.drop_table('color_rgb_values')
    op.drop_table('colorant_details')
    op.drop_table('formulations')
    op.drop_table('colorants')
