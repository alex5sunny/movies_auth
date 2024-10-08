import uuid
import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    token = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    expires_at = Column(DateTime, nullable=False)

    def __init__(self, token: str, user_id: uuid.UUID, expires_at: datetime):
        self.token = token
        self.user_id = user_id
        self.expires_at = expires_at

    def __repr__(self) -> str:
        return f'<Refresh Token {self.id}>'
