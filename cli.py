import argparse

parser = argparse.ArgumentParser(description="CLI tool for a private cloud on my raspberry pi")
parser.add_argument("commands", choices=["upload", "download"])
parser.add_argument("filename")

args = parser.parse_args()
if (args.commands == "upload"):
    upload(args.filename)
elif (args.commands == "download"):
    download(args.filename)
