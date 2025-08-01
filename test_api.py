import requests
import os
import argparse

def upload(filename):
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/plain")}
            response = requests.post("http://192.168.1.100:8000/upload", files=files)

        print(response.json())
        print(f"{filename} uploaded to cloud.")
    except FileNotFoundError:
        print({"status": "File not found on client", "status_code": 404})

def download(filename):
    params = {"filename": filename}
    response = requests.get("http://192.168.1.100:8000/download", params=params)

    if response.status_code == 200:
        os.makedirs("cloudbox_downloads", exist_ok=True)
        with open(f"cloudbox_downloads/{filename}", "wb") as f:
            f.write(response.content)
    print(f"{filename} downloaded from cloud and saved to cloudbox_downloads.")

parser = argparse.ArgumentParser(description="CLI tool for a private cloud on my raspberry pi")
parser.add_argument("commands", choices=["upload", "download"])
parser.add_argument("filename")

args = parser.parse_args()
if (args.commands == "upload"):
    upload(args.filename)
elif (args.commands == "download"):
    download(args.filename)
