# routes.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io
import logging

from app.etl.impl_weather_etl import WeatherETL
from app.etl.impl_crop_yield_etl import CropYieldETL
from app.db.database import get_db

router = APIRouter()

@router.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
):
    """
    Upload a file for ingestion.
    """
    logging.info(f"Received file upload: {file.filename}")

    # Read the file content as raw bytes
    content = await file.read()  # Read raw content here

    # Determine the file type based on the number of columns
    # For this example, we'll read a small portion to infer the type
    try:
        buffer = io.BytesIO(content)
        # Read the first few lines to determine the structure
        sample_df = pd.read_csv(
            buffer,
            sep="\t",
            header=None,
            nrows=5
        )
        num_columns = len(sample_df.columns)
    except Exception as e:
        logging.error(f"Error reading the uploaded file: {e}")
        raise HTTPException(status_code=400, detail="Invalid file format.")

    # Reset buffer position after reading
    buffer.seek(0)

    # Determine which ETL class to use based on the number of columns
    if num_columns == 4:
        etl_class = WeatherETL(session)
    elif num_columns == 2:
        etl_class = CropYieldETL(session)
    else:
        logging.error("Unknown file structure based on column count.")
        raise HTTPException(status_code=400, detail="Unknown file structure.")


        # Run the ETL process
    await etl_class.run_etl(content, file.filename)
    # except Exception as e:
    #     logging.error(f"ETL process failed: {e}")
    #     raise HTTPException(status_code=500, detail="Failed to process the file.")

    logging.info(f"File '{file.filename}' processed successfully.")
    return {"message": f"File '{file.filename}' processed successfully."}
