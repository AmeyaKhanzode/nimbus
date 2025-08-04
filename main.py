from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import base64
import os

app = FastAPI()

# Create uploads directory on startup
UPLOADS_DIR = "/home/cloudbox/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
@app.post("/upload")
async def upload_files(file: UploadFile = File(...)):
    content = await file.read()
    try:
        with open(f"{UPLOADS_DIR}/{file.filename}", "wb") as f:
            f.write(content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"File upload fail: {str(e)}")
    return {
            "filename": file.filename,
            "status": "File uploaded successfully"
        }

@app.get("/download")
async def download_files(filename: str):
    file_path = f"{UPLOADS_DIR}/{filename}"
    print(f"Looking for file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename
    )

@app.get("/list_uploads")
async def list_uploads():
    files = os.listdir(UPLOADS_DIR)
    length = len(files)

    return {
        "files" : files,
        "count" : length,
        "message" : f"Found {length} uploaded files"
    }

@app.get("list_trash")
async def list_trash():
    files = os.listdir("/home/cloudbox/trash")
    length = len(files)

    return {
        "files" : files,
        "count" : length,
        "message" : f"Found {length} files in the trash"
    }