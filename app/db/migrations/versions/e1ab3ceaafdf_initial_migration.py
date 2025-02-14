"""Initial migration

Revision ID: e1ab3ceaafdf
Revises: 
Create Date: 2025-01-26 17:32:56.225780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1ab3ceaafdf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "crop_yield_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("station_id", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("yield_value", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "year", name="uq_cropyield_station_year"),
    )
    op.create_table(
        "weather_data",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("station_id", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("max_temp", sa.Float(), nullable=True),
        sa.Column("min_temp", sa.Float(), nullable=True),
        sa.Column("precipitation", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "date", name="uq_weather_station_date"),
    )
    op.create_table(
        "weather_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("station_id", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("avg_max_temp", sa.Float(), nullable=True),
        sa.Column("avg_min_temp", sa.Float(), nullable=True),
        sa.Column("total_precipitation", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("station_id", "year", name="uq_weatherstats_station_year"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("weather_stats")
    op.drop_table("weather_data")
    op.drop_table("crop_yield_data")
    # ### end Alembic commands ###
