import requests

with open("Ameya_Resume_SDE.pdf", "rb") as f:
    files = {"file": ("Ameya_Resume_SDE.pdf", f, "application/pdf")}
    response = requests.post("http://127.0.0.1:8000/upload", files=files)

print(response.json())