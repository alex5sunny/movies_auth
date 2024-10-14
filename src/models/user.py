# models/user.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base
from models.role import user_roles_table


class User(Base):

    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_superuser = Column(Boolean, default=False)
    created_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    roles = relationship(
        'Role', secondary=user_roles_table, back_populates='users'
    )
    user_logins = relationship('UserLogin', back_populates='user')

    def __init__(
            self, login: str, password: str, first_name: str, last_name: str,
            is_superuser: bool = False
    ) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_superuser = is_superuser

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class UserLogin(Base):

    __tablename__ = 'users_logins'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    signin_data = Column(String(255))
    login_at = Column(
        DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None)
    )
    user = relationship('User', back_populates='user_logins')

    def __init__(
            self, user_id: uuid.UUID, signin_data = ''
    ) -> None:
        self.user_id = user_id
        self.signin_data = signin_data

    def __repr__(self) -> str:
        return (f'<user:{self.user.login} login:{self.login_at} '
                f'user data:{self.signin_data}>')
