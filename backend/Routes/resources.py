from fastapi import APIRouter, Form, File, UploadFile, Depends, status, HTTPException
from backend.cqrs_eda_implementation import UploadResourceCommand, UploadResourceCommandHandler, ResourceRepository
from sqlalchemy.orm import Session
from backend.database import get_db

router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)

@router.get("/{resource_id}")
async def get_resource(resource_id: str):
    resource = await ResourceRepository.get_resource_by_id(resource_id)

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    return resource


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED
)
async def upload_resource(
    title: str = Form(...),
    description: str = Form(...),
    resource_type: str = Form(...),
    difficulty_level: str = Form(...),
    uploader_user_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Stream-safe size calculation
    file_size = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        file_size += len(chunk)

    await file.seek(0)

    command = UploadResourceCommand(
        title=title,
        description=description,
        resource_type=resource_type,
        difficulty_level=difficulty_level,
        uploader_user_id=uploader_user_id,
        filename=file.filename,
        file_size=file_size,
        content_type=file.content_type,
    )
    await UploadResourceCommandHandler.handle(command)

    return {
        "message": "Resource uploaded successfully",
        "filename": file.filename,
        "file_size": file_size
    }


@router.get("/{resource_id}/view")
async def view_resource(resource_id: int, db: Session = Depends(get_db)):
    return {"resource_id": resource_id}

@router.post("/{resource_id}/rate")
async def rate_resource(
    resource_id: int,
    rating: int = Form(...),
    db: Session = Depends(get_db)
):
    return {
        "resource_id": resource_id,
        "rating": rating
    }
