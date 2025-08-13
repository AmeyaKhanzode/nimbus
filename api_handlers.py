#!/usr/bin/env python

from importnb import Notebook
import os
import requests
import getpass
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

with Notebook():
    import db_utils

db_utils.init_db()
token_path = os.path.expanduser("~/Library/Application Support/myapp/")
if os.path.exists(os.path.join(token_path, "token.json")):
    with open(os.path.join(token_path, "token.json")) as f:
        data = json.load(f)

    token = data["access_token"]

    header = {"Authorization": f"Bearer {token}"}
else:
    print("Token file does not exist.")


def handle_encryption(filename):
    key = os.urandom(32)
    iv = os.urandom(16)

    cipher = Cipher(algorithm=algorithms.AES, mode=modes.GCM)
    encryptor = cipher.encryptor()

    with open(filename, "r") as fin:
        while chunk := fin.read(4096):
            pass  # for now


def list_files():
    response = requests.get("http://192.168.1.100:8000/list_uploads", headers=header)
    if response.status_code == 200:
        data = response.json()
        if (data["count"] == 0):
            print("Cloud is empty")
            return
        for i in range(data["count"]):
            print(data["files"][i])
    else:
        print("Error occurred while listing files")


def upload(filename):
    file_size = None
    is_dir = 0
    if os.path.isdir(filename):
        is_dir = 1
        import shutil
        import tempfile
        base_name = os.path.basename(filename.rstrip("/"))
        print(base_name)
        temp_zip_path = os.path.join(tempfile.gettempdir(), base_name)
        shutil.make_archive(temp_zip_path, 'zip', filename)
        filename = temp_zip_path + ".zip"
        print(f"Zipped directory to: {filename}")
    try:
        print("FILENAME: ", filename)
        with open(filename, "rb") as file:
            file_hash, file_size = db_utils.get_file_hash(file)
            print(f"file hash we made: {file_hash}")
            file_existance = db_utils.is_uploaded(filename, file_hash)
            print(f"file existance: {file_existance}")
            if (file_existance == "duplicate"):
                print("File already exists")
                return
            if is_dir == 1:
                files = {"file": (base_name + ".zip", file, "text/plain")}
            else:
                files = {"file": (filename, file, "text/plain")}
            response = requests.post("http://192.168.1.100:8000/upload", files=files, headers=header)
            print(json.dumps(response.json(), indent=4))

            if (response.status_code == 200):
                if (file_existance == "modified"):
                    print("File exists but is modified recently, Replacing old file...")
                    db_utils.update_entry(filename, file_size, file_hash)
                elif (file_existance == "new"):
                    print("File does not exist. Uploading...")
                    db_utils.add_entry(filename, file_size, file_hash)
                print()
                print(f"{filename} uploaded to cloud")
                print()
            else:
                print("Error: Upload API failed")

    except FileNotFoundError:
        print("File not found") 


def download(filename):
    params = {"filename": filename}
    response = requests.get("http://192.168.1.100:8000/download", params=params, headers=header)
    download_dir = os.path.expanduser("~/cloudbox_downloads")
    os.makedirs(download_dir, exist_ok=True)
    if response.status_code == 200:
        os.makedirs(f"/{download_dir}", exist_ok=True)
        with open(f"/{download_dir}/{filename}", "wb") as f:
            f.write(response.content)
    print(f"{filename} downloaded from cloud and saved to cloudbox_downloads")


def auth():
    password = getpass.getpass("Enter password: ")
    username = getpass.getuser()
    try:
        login_data = {
            "username" : username,
            "password" : password,
            "grant_type" : "password"
        }
        login_response = requests.post("http://192.168.1.100:8000/token", data = login_data)
        if login_response.status_code == 200:
            token_path = os.path.expanduser("~/Library/Application Support/myapp/")
            os.makedirs(token_path, exist_ok=True)
            with open(os.path.join(token_path,"token.json"), "w") as f:
                json.dump(login_response.json(), f)
            return True
        else:
            print("Authentication failed. Error: ", login_response.text)
            return False
    except Exception as e:
        print("Error in authentication: ", e)
        return False


def register_user():
    print("Register yourself first\n")
    username = getpass.getuser()
    password = input("Enter password: ")

    try:
        # call /register here
        data = {
            "username" : username,
            "password" : password
        }
        try:
            response = requests.post("http://192.168.1.100:8000/register", json=data)
            print(response.text)
        except Exception as e:
            print(e)
        if response.status_code == 200:
            print("Registered successfully")
        else:
            print("Registration failed")
            return False

        # call /token immediately
        login_data = {
            "username" : username,
            "password" : password,
            "grant_type" : "password"
        }
        login_response = requests.post("http://192.168.1.100:8000/token", data = login_data)
        if login_response.status_code == 200:
            token_path = os.path.expanduser("~/Library/Application Support/myapp/")
            os.makedirs(token_path, exist_ok=True)
            with open(os.path.join(token_path,"token.json"), "w") as f:
                json.dump(login_response.json(), f)
            print("Authentication Successful")
            return True
        else:
            print("Authentication failed. Error: ", login_response.text)
            return False
    except Exception as e:
        print("Error during registration: ", e)
        return False


def check_user_exists():
    try:
        response = requests.get(f"http://192.168.1.100:8000/user_exists", timeout=3)
        if response.status_code == 200:
            data = response.json()
            return (data.get("user_exists"), 0)
        else:
            print(f"User does not exist")
            return (False, 0)
    except requests.exceptions.ConnectionError:
        print("Server is down or unreachable")
        return (False, 1)
    except requests.exceptions.Timeout:
        print("Server did not respond. Try again")
        return (False, 1)
    except Exception as e:
        print(f"Error checking if user exists: {e}")
        return (False, 1)


def move_to_trash(filename):
    print("level 3 deep")
    params = {"filename": filename}
    print(filename)
    try:
        response = requests.delete(f"http://192.168.1.100:8000/delete", params=params, headers=header)
        print(response.status_code, response.text) 
        if response.status_code == 200:
            db_utils.move_to_trash(filename)
            print("File moved to trash, use `nimbus restore <filename>` to restore")
        else:
            print("Error: Could not move file to trash.")
    except Exception as e:
        print(str(e))


def restore(filename):
    params = {"filename": filename}
    try:
        response = requests.delete(f"http://192.168.1.100:8000/restore", params=params, header=header)
        if response.status_code == 200:
            db_utils.restore(filename)
            print(f"Restored {filename} from trash")
    except Exception as e:
        print(str(e))


def hard_delete(filename):
    params = {"filename": filename}
    warning_input = input("⚠️ File in trash. Warning this action is permanent and file cannot be restored. Do you want to proceed? (y/n): ")
    if warning_input.upper() == 'Y':
        try:
            response = requests.delete(f"http://192.168.1.100:8000/hard_delete", params=params, headers=header)
            if response.status_code == 200:
                db_utils.hard_delete(filename)
                print("File deleted permanently from cloud")
        except Exception as e:
            print(str(e))
    else:
        return


def handle_delete(filename):
    print("level 2 deep")
    in_trash = db_utils.is_in_trash(filename)
    print(f"in trash {in_trash}")
    if in_trash is None:
        print("File not found")
    elif in_trash:
        print("when in trash is true")
        hard_delete(filename)
    else:
        print("when in trash is false")
        move_to_trash(filename)


def list_trash():
    response = requests.get("http://192.168.1.100:8000/list_trash", headers=header)
    if response.status_code == 200:
        data = response.json()
        if (data["count"] == 0):
            print("Trash is empty")
            return
        for i in range(data["count"]):
            print(data["files"][i])
    else:
        print("Error occurred while listing trash files.")
