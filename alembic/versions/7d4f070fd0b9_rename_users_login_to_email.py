"""rename users login to email

Revision ID: 7d4f070fd0b9
Revises: 2dec33ec6d09
Create Date: 2026-10-31 19:33:42.377814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d4f070fd0b9'
down_revision: Union[str, None] = '2dec33ec6d09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(), nullable=False))
    op.drop_constraint('users_login_key', 'users', type_='unique')       # stare (login)
    op.create_unique_constraint('users_email_key', 'users', ['email'])   # nowe (email)
    op.drop_column('users', 'login')


def downgrade() -> None:
    op.add_column('users', sa.Column('login', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint('users_email_key', 'users', type_='unique')       # to, co tworzył upgrade
    op.create_unique_constraint('users_login_key', 'users', ['login'])
    op.drop_column('users', 'email')
