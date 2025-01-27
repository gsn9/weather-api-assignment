from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_403_FORBIDDEN
from app.db.migration_runner import run_migrations
import os

router = APIRouter()

# Secure the endpoint with a secret key
@router.post("/migrate")
async def trigger_migration():
    """
    Trigger database migrations via Alembic.
    """
    MIGRATION_SECRET = os.getenv("MIGRATION_SECRET")

    # if secret != MIGRATION_SECRET:
    #     raise HTTPException(
    #         status_code=HTTP_403_FORBIDDEN, detail="Invalid secret key"
    #     )

    alembic_ini_path = "./alembic.ini"

    try:
        await run_migrations(alembic_ini_path)
        return {"message": "Migrations ran successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run migrations: {str(e)}"
        )
