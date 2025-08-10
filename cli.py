#!/usr/bin/env python3

import argparse
import importnb
import os
import sys

with importnb.Notebook():
    import api_handlers

user_exists = api_handlers.check_user_exists()

if not user_exists[0] and user_exists[1] == 0:
    if not api_handlers.register_user():
        sys.exit(1)
elif user_exists[0]:
    if not api_handlers.auth():
        sys.exit(1)
else:
    sys.exit(1)
parser = argparse.ArgumentParser(description="CLI tool for a private cloud on my raspberry pi")
parser.add_argument("commands", choices=["upload", "download", "list", "restore"])
parser.add_argument("filenames", nargs="*")

args = parser.parse_args()

if args.commands in ["upload", "download"] and not args.filenames:
    print(f"Error: '{args.commands}' command requires at least one filename.")
    sys.exit(1)

match args.commands:
    case "upload":
        for filename in args.filenames:
            api_handlers.upload(filename)
    case "download":
        for filename in args.filenames:
            api_handlers.download(filename)
    case "list":
        print()
        api_handlers.list_files()
    case "delete":
        for filename in args.filenames:
            api_handlers.handle_delete(filename)
    case "restore":
        for filename in args.filenames:
            api_handlers.restore(filename)
