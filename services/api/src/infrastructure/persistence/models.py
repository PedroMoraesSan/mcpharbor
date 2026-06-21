from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from shared.time import utc_now


class Base(DeclarativeBase):
    pass


class InstalledMCPModel(Base):
    __tablename__ = "installed_mcps"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    catalog_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str] = mapped_column(String(255), default="")
    version: Mapped[str] = mapped_column(String(100), default="latest")
    docker_image: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="stopped")
    container_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    container_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    installed_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    credentials: Mapped[list["CredentialModel"]] = relationship(back_populates="mcp")
    integrations: Mapped[list["IntegrationModel"]] = relationship(back_populates="mcp")


class CredentialModel(Base):
    __tablename__ = "credentials"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    mcp_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("installed_mcps.id"), nullable=False
    )
    key_name: Mapped[str] = mapped_column(String(255), nullable=False)
    keyring_ref: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    mcp: Mapped["InstalledMCPModel"] = relationship(back_populates="credentials")


class IntegrationModel(Base):
    __tablename__ = "integrations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    client: Mapped[str] = mapped_column(String(50), nullable=False)
    mcp_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("installed_mcps.id"), nullable=False
    )
    config_path: Mapped[str] = mapped_column(String(500), nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    mcp: Mapped["InstalledMCPModel"] = relationship(back_populates="integrations")
