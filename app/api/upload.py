from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
import shutil
from pathlib import Path
from app.core.file_processor import FileProcessor
from app.core.ai_service import TunaAIService

router = APIRouter()


def get_unique_filename(directory: str, filename: str) -> str:
    """Generate a unique filename if the file already exists"""
    file_path = Path(directory) / filename

    if not file_path.exists():
        return filename

    # Split filename and extension
    name_part = file_path.stem
    extension = file_path.suffix

    counter = 1
    while True:
        new_filename = f"{name_part}_{counter}{extension}"
        new_file_path = Path(directory) / new_filename
        if not new_file_path.exists():
            return new_filename
        counter += 1


@router.post("/upload-lesson-material")
async def upload_and_process_lesson_material(
    file: UploadFile = File(...),
    filename: str = Query(...,
                          description="Desired filename for the uploaded file"),
    generate_summary: bool = Query(
        True, description="Whether to generate AI summary from file content")
):
    """Upload a lesson material file, extract text, and optionally generate summary"""

    # Validate file type - only PDF allowed
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported for lesson materials"
        )

    # Create public directory if it doesn't exist
    public_dir = Path("public")
    public_dir.mkdir(exist_ok=True)

    # Ensure filename has .pdf extension
    if not filename.lower().endswith('.pdf'):
        filename = f"{filename}.pdf"

    # Get unique filename to avoid conflicts
    unique_filename = get_unique_filename(str(public_dir), filename)
    file_path = public_dir / unique_filename

    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from the uploaded file
        extracted_text = None
        text_extraction_error = None

        try:
            extracted_text = FileProcessor.extract_text_from_file(
                str(file_path))
        except Exception as e:
            text_extraction_error = str(e)

        # Generate summary if requested and text was extracted successfully
        summary = None
        summary_error = None

        if generate_summary and extracted_text and not extracted_text.startswith("Error") and not extracted_text.startswith("PDF uploaded successfully"):
            try:
                ai_service = TunaAIService()
                summary_response = await ai_service.summarize_text(extracted_text, summary_type="brief")
                summary = summary_response.get("summary")
            except Exception as e:
                summary_error = str(e)

        return {
            "message": "File uploaded and processed successfully",
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_size": file_path.stat().st_size,
            "text_extracted": extracted_text is not None and not extracted_text.startswith("Error"),
            "text_length": len(extracted_text) if extracted_text else 0,
            "summary": summary,
            "text_extraction_error": text_extraction_error,
            "summary_error": summary_error,
            "extracted_text_preview": extracted_text[:500] if extracted_text and len(extracted_text) > 500 else extracted_text
        }

    except Exception as e:
        # Clean up file if something went wrong
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing lesson material: {str(e)}"
        )
    finally:
        file.file.close()


@router.post("/upload-file")
async def upload_lesson_file(
    file: UploadFile = File(...),
    filename: str = Query(...,
                          description="Desired filename for the uploaded file")
):
    """Upload a lesson file to the public folder"""

    # Create public directory if it doesn't exist
    public_dir = Path("public")
    public_dir.mkdir(exist_ok=True)

    # Get file extension from uploaded file
    file_extension = Path(file.filename).suffix if file.filename else ""

    # If the provided filename doesn't have an extension, add the original file's extension
    if not Path(filename).suffix and file_extension:
        filename = f"{filename}{file_extension}"

    # Get unique filename to avoid conflicts
    unique_filename = get_unique_filename(str(public_dir), filename)

    # Full path where file will be saved
    file_path = public_dir / unique_filename

    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_size": file_path.stat().st_size
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )
    finally:
        file.file.close()


@router.get("/files/{filename}")
async def get_lesson_file(filename: str):
    """Download or serve a lesson file from the public folder"""

    public_dir = Path("public")
    file_path = public_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    # Determine media type based on file extension
    file_extension = file_path.suffix.lower()
    if file_extension == '.pdf':
        media_type = 'application/pdf'
    else:
        media_type = 'application/octet-stream'

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type=media_type,
        headers={
            "Content-Disposition": "inline; filename=" + filename if file_extension == '.pdf' else f"attachment; filename={filename}"
        }
    )


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file from the public folder"""

    public_dir = Path("public")
    file_path = public_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Invalid file")

    try:
        file_path.unlink()  # Delete the file
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )


@router.get("/files")
async def list_files():
    """List all files in the public folder"""

    public_dir = Path("public")

    if not public_dir.exists():
        return {"files": []}

    try:
        files = []
        for file_path in public_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created_at": file_path.stat().st_ctime,
                    "modified_at": file_path.stat().st_mtime
                })

        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing files: {str(e)}"
        )
