from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse
from typing import Optional
import shutil
from pathlib import Path

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

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
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
