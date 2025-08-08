from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import hashlib
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import secrets
from jose import jwt, JWTError
from pydantic import BaseModel
import json

SECRET_KEY = secrets.token_hex(32)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # used to securely hash passwords

fake_user = {
    "username": "ameya",
    "hashed_password": pwd_context.hash("password123")  # You can change the password
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # this is a token extractor, tells fastapi that user must provide a jwt to access protected endpoints
"""
FastAPI, please expect users to send their login form to /token, 
and once they get a token, they'll use it in the Authorization: Bearer <token> header when calling protected routes.
"""
app = FastAPI()

class User(BaseModel):
    username : str
    password : str

@app.post("/register")
async def register_user(user: User):
    try:
        with open("user_data.json", "w") as f:
            json.dump(
                {
                    "username" : user.username,
                    "password" : pwd_context.hash(user.password)
                }, f)
        return {"status" : "success", "message" : f"User {user.username} registered successfully"}
    except:
        return {"status" : "fail", "message" : "Could not register user"}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = None):
    with open("user_data.json", "r") as f:
        data = json.load(f)
    username = data["username"]
    hashed_password = data["password"]

    if form_data is None:
        raise HTTPException(status_code=400, detail="No username or password provided")
    elif form_data.username != username or not verify_password(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    else:
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}

@app.get("/user_exists")
async def user_exists():
    user_file = "user_data.json"
    if not os.path.exists(user_file):
        return {"user_exists": False}
    try:
        with open(user_file, "r") as f:
            data = json.load(f)
        # Basic check if username and password keys exist
        if "username" in data and "password" in data:
            return {"user_exists": True}
        else:
            return {"user_exists": False}
    except Exception:
        return {"user_exists": False}
    

# Create uploads directory on startup
UPLOADS_DIR = "/home/ameya/cloudbox/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
@app.post("/upload")
async def upload_files(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = hashlib.sha256(content)

    try:
        with open(f"{UPLOADS_DIR}/{file.filename}", "wb") as f:
            f.write(content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"File upload fail: {str(e)}")
    return {
            "filename": file.filename,
            "status": "File uploaded successfully"
        }
'''
we can store hashes of the content inside the file in the metadata db and then check for the hashes when the file is uploaded
and if its already present in the cloud then we dont upload it
'''
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

@app.get("/list_trash")
async def list_trash():
    files = os.listdir("/home/ameya/cloudbox/trash")
    length = len(files)

    return {
        "files" : files,
        "count" : length,
        "message" : f"Found {length} files in the trash"
    }