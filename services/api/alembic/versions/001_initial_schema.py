"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "installed_mcps",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("catalog_id", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), default=""),
        sa.Column("author", sa.String(255), default=""),
        sa.Column("version", sa.String(100), default="latest"),
        sa.Column("docker_image", sa.String(500), nullable=False),
        sa.Column("status", sa.String(50), default="stopped"),
        sa.Column("container_id", sa.String(100), nullable=True),
        sa.Column("container_name", sa.String(255), nullable=True),
        sa.Column("installed_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "credentials",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "mcp_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("installed_mcps.id"),
            nullable=False,
        ),
        sa.Column("key_name", sa.String(255), nullable=False),
        sa.Column("keyring_ref", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "integrations",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("client", sa.String(50), nullable=False),
        sa.Column(
            "mcp_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("installed_mcps.id"),
            nullable=False,
        ),
        sa.Column("config_path", sa.String(500), nullable=False),
        sa.Column("connected_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("integrations")
    op.drop_table("credentials")
    op.drop_table("installed_mcps")
