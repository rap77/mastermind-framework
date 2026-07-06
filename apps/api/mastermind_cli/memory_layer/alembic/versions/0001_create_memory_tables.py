"""Create the canonical memory-layer tables.

Revision ID: 0001_create_memory_tables
Revises:
Create Date: 2026-06-29 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_create_memory_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the first-party memory tables and supporting indexes."""
    op.create_table(
        "mm_memory_items",
        sa.Column("memory_id", sa.String(length=255), primary_key=True),
        sa.Column("memory_type", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("project_id", sa.String(length=255), nullable=True),
        sa.Column("brain_id", sa.String(length=255), nullable=True),
        sa.Column("niche", sa.String(length=128), nullable=True),
        sa.Column("visibility", sa.String(length=64), nullable=False),
        sa.Column("source_kind", sa.String(length=128), nullable=True),
        sa.Column("source_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_items_memory_type",
        "mm_memory_items",
        ["memory_type"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_items_project_id",
        "mm_memory_items",
        ["project_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_items_brain_id",
        "mm_memory_items",
        ["brain_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_items_niche",
        "mm_memory_items",
        ["niche"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_items_created_at",
        "mm_memory_items",
        ["created_at"],
        if_not_exists=True,
    )

    op.create_table(
        "mm_memory_preferences",
        sa.Column("preference_id", sa.String(length=255), primary_key=True),
        sa.Column("project_id", sa.String(length=255), nullable=True),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column(
            "value",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_preferences_project_id",
        "mm_memory_preferences",
        ["project_id"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_preferences_scope",
        "mm_memory_preferences",
        ["scope"],
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_preferences_key",
        "mm_memory_preferences",
        ["key"],
        if_not_exists=True,
    )

    op.create_table(
        "mm_memory_sessions",
        sa.Column("session_id", sa.String(length=255), primary_key=True),
        sa.Column("project_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        if_not_exists=True,
    )
    op.create_index(
        "idx_mm_memory_sessions_project_id",
        "mm_memory_sessions",
        ["project_id"],
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove the canonical memory-layer tables."""
    op.drop_index(
        "idx_mm_memory_sessions_project_id",
        table_name="mm_memory_sessions",
        if_exists=True,
    )
    op.drop_table("mm_memory_sessions", if_exists=True)

    op.drop_index(
        "idx_mm_memory_preferences_key",
        table_name="mm_memory_preferences",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_preferences_scope",
        table_name="mm_memory_preferences",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_preferences_project_id",
        table_name="mm_memory_preferences",
        if_exists=True,
    )
    op.drop_table("mm_memory_preferences", if_exists=True)

    op.drop_index(
        "idx_mm_memory_items_created_at",
        table_name="mm_memory_items",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_items_niche",
        table_name="mm_memory_items",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_items_brain_id",
        table_name="mm_memory_items",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_items_project_id",
        table_name="mm_memory_items",
        if_exists=True,
    )
    op.drop_index(
        "idx_mm_memory_items_memory_type",
        table_name="mm_memory_items",
        if_exists=True,
    )
    op.drop_table("mm_memory_items", if_exists=True)
