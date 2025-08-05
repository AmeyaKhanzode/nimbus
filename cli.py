#!/usr/bin/env python3

import argparse
import importnb

with importnb.Notebook():
    import api_handlers

parser = argparse.ArgumentParser(description="CLI tool for a private cloud on my raspberry pi")
parser.add_argument("commands", choices=["upload", "download"])
parser.add_argument("filename")

args = parser.parse_args()
if (args.commands == "upload"):
    api_handlers.upload(args.filename)
elif (args.commands == "download"):
    api_handlers.download(args.filename)
