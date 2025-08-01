from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload fail: {str(e)}")
    return {
            "filename": file.filename,
            "status": "File uploaded successfully"
        }