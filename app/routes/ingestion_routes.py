from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import pandas as pd
import io
import logging

from app.etl.impl_weather_etl import WeatherETL
from app.etl.impl_crop_yield_etl import CropYieldETL
from app.db.database import get_db

router = APIRouter()

# Define a reusable response model for file upload
class FileUploadResponse(BaseModel):
    message: str
    details: dict

    class Config:
        schema_extra = {
            "example": {
                "message": "File 'USC00110072.txt' processed successfully.",
                "details": {
                    "ingested_records": 1000,
                    "duplicate_records_skipped": 50,
                    "total_time_seconds": 5.2,
                },
            }
        }

@router.post(
    "/upload_file",
    response_model=FileUploadResponse,
    summary="Upload a file for data ingestion",
    description=(
        "Upload a file containing weather or crop yield data for ingestion into "
        "the database. The system detects the file type dynamically based on the structure "
        "and processes it accordingly."
    ),
    tags=["Data Ingestion"],
    responses={
        200: {
            "description": "File processed successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "File 'USC00110072.txt' processed successfully.",
                        "details": {
                            "ingested_records": 1000,
                            "duplicate_records_skipped": 50,
                            "total_time_seconds": 5.2,
                        },
                    }
                }
            },
        },
        400: {"description": "Invalid file format or unknown file structure."},
        500: {"description": "Failed to process the file."},
    },
)
async def upload_file(
    file: UploadFile = File(..., description="The file to be uploaded."),
    session: AsyncSession = Depends(get_db),
):
    """
    Upload a file for ingestion into the database.
    """
    logging.info(f"Received file upload: {file.filename}")

    # Read the file content as raw bytes
    content = await file.read()

    # Determine the file type based on the number of columns
    try:
        buffer = io.BytesIO(content)
        sample_df = pd.read_csv(buffer, sep="\t", header=None, nrows=5)
        num_columns = len(sample_df.columns)
    except Exception as e:
        logging.error(f"Error reading the uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Invalid file format.")

    # Reset buffer position
    buffer.seek(0)

    # Determine which ETL class to use based on the number of columns
    if num_columns == 4:
        etl_class = WeatherETL(session)
    elif num_columns == 2:
        etl_class = CropYieldETL(session)
    else:
        logging.error("Unknown file structure based on column count.")
        raise HTTPException(status_code=400, detail="Unknown file structure.")

    # Run the ETL process and capture the feedback
    try:
        feedback = await etl_class.run_etl(content, file.filename)
    except Exception as e:
        logging.error(f"ETL process failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the file.")

    logging.info(f"File '{file.filename}' processed successfully.")

    # Return feedback to the user
    return {
        "message": f"File '{file.filename}' processed successfully.",
        "details": feedback,
    }
