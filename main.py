# main.py
from fastapi import FastAPI
import asyncio
import os
from services.converter_logic import process_and_upload_csv
from config import CSV_FILE_PATH

app = FastAPI(
    title="CSV to DB Processor API",
    description="Converts CSV to nested JSON, uploads to PostgreSQL, and reports age distribution."
)

@app.get("/")
def home():
    return {"message": "CSV Processor API is running. Use /api/convert to trigger the process."}

@app.post("/api/convert")
async def run_csv_conversion():
    """
    Triggers the CSV file processing, database upload, and age distribution report generation.
    NOTE: The CSV file is read from the fixed location defined in the .env file.
    """
    
    # Run the synchronous function in a separate thread to prevent blocking the FastAPI event loop
    try:
        report = await asyncio.to_thread(process_and_upload_csv, CSV_FILE_PATH)
        
        # Log the report to the console as requested
        print("\n--- API-Triggered Age Distribution Report ---")
        for group, percent in report.items():
            print(f"{group:<10}\t{percent}")
        print("-------------------------------------------\n")

        return {
            "status": "success",
            "message": f"CSV processing complete and {len(report)} age groups reported.",
            "age_distribution": report
        }
        
    except FileNotFoundError as e:
        return {"status": "error", "message": f"File Not Found: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Processing failed: {str(e)}"}