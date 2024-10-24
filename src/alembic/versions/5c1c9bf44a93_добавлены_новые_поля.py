"""добавлены новые поля

Revision ID: 5c1c9bf44a93
Revises: cbd3ac9c85c7
Create Date: 2024-10-19 19:25:55.764389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c1c9bf44a93'
down_revision: Union[str, None] = 'cbd3ac9c85c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'roles', ['id'])
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'users_logins', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_logins', type_='unique')
    op.drop_column('users', 'is_superuser')
    op.drop_constraint(None, 'roles', type_='unique')
    # ### end Alembic commands ###
