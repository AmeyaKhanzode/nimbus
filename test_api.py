import requests
import os
# try:
#     filename = "test.txt"
#     with open(filename, "rb") as f:
#         files = {"file": (filename, f, "text/plain")}
#         response = requests.post("http://192.168.1.100:8000/upload", files=files)

#     print(response.json())
# except FileNotFoundError:
#     print({"status": "File not found on client", "status_code": 404})

filename = "test.txt"
params = {"filename": filename}
response = requests.get("http://192.168.1.100:8000/download", params=params)

print("Download response status:", response.status_code)
print("Download response headers:", response.headers)
print("Download response content (first 200 bytes):", response.content[:200])
print("Raw downloaded bytes:", response.content[:100])


if response.status_code == 200:
    os.makedirs("cloudbox_downloads", exist_ok=True)
    with open(f"cloudbox_downloads/{filename}", "wb") as f:
        f.write(response.content)