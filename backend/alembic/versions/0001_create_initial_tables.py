"""create initial tables

Revision ID: 0001_create_initial_tables
Revises: 
Create Date: 2026-05-19 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
    )
    op.create_table(
        'movies',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('year', sa.Integer),
        sa.Column('description', sa.Text),
        sa.Column('avg_rating', sa.Float, nullable=False, server_default='0')
    )
    op.create_table(
        'movie_category',
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id'), primary_key=True),
        sa.Column('category_id', sa.Integer, sa.ForeignKey('categories.id'), primary_key=True),
    )
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('movie_id', sa.Integer, sa.ForeignKey('movies.id'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('text', sa.Text),
        sa.Column('created_at', sa.DateTime)
    )


def downgrade():
    op.drop_table('reviews')
    op.drop_table('movie_category')
    op.drop_table('movies')
    op.drop_table('categories')
