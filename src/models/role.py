import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.postgres import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String(500), nullable=True)

    users = relationship(
        "User",
        secondary="user_roles",
        primaryjoin="Role.id == UserRole.role_id",
        secondaryjoin="UserRole.user_id == User.id",
        back_populates="roles",
        lazy="selectin",
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True),
                     ForeignKey("users.id"),
                     nullable=False)
    role_id = Column(UUID(as_uuid=True),
                     ForeignKey("roles.id"),
                     nullable=False)
