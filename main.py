from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import base64
import os

app = FastAPI()
@app.post("/upload")
async def upload_files(file: UploadFile = File(...)):
    content = await file.read()
    try:
        os.makedirs("static", exist_ok=True)
        with open(f"static/{file.filename}", "wb") as f:
            f.write(content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"File upload fail: {str(e)}")
    return {
            "filename": file.filename,
            "status": "File uploaded successfully"
        }

@app.get("/download")
async def download_files(filename: str):
    file_path = f"static/{filename}"
    print(f"Looking for file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=filename
    )