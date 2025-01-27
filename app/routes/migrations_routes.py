from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN
from app.db.migration_runner import run_migrations
import os

router = APIRouter()

# Define a response model for the migration endpoint
class MigrationResponse(BaseModel):
    message: str

    class Config:
        schema_extra = {
            "example": {"message": "Migrations ran successfully."}
        }

@router.post(
    "/migrate",
    response_model=MigrationResponse,
    summary="Run database migrations",
    description=(
        "Trigger Alembic migrations to apply changes to the database schema. "
    ),
    tags=["Database Management"],
    responses={
        200: {"description": "Migrations ran successfully."},
        500: {"description": "Failed to run migrations."},
    },
)
async def trigger_migration():
    """
    Trigger database migrations via Alembic.
    """

    alembic_ini_path = "./alembic.ini"

    try:
        await run_migrations(alembic_ini_path)
        return {"message": "Migrations ran successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run migrations: {str(e)}"
        )
