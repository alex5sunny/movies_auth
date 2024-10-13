import uuid
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.postgres import Base


user_roles_table = Table(
    'user_roles', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)


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
        'User', secondary=user_roles_table, back_populates='roles'
    )

