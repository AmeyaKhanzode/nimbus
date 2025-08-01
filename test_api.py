import requests
try:
    filename = "test.txt"
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "application/pdf")}
        response = requests.post("http://192.168.1.100:8000/upload", files=files)

    print(response.json())
except FileNotFoundError:
    print({"status": "File not found on client", "status_code": 404})