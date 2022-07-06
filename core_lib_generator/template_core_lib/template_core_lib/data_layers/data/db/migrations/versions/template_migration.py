"""create_db

Revision ID: 1
Revises:
Create Date: 2022-04-07 19:14:03.203923

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

revision = '1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # template_upgrade


def downgrade():
    # template_downgrade
