#!/usr/bin/env python3
import os
import shutil
import ct

PUBLIC_PATH = "../public"

os.chdir(os.path.join(os.path.dirname(__file__), "raw"))
os.mkdir(PUBLIC_PATH)

for dirpath, dirnames, filenames in os.walk("."):
    for dirname in dirnames:
        os.mkdir(os.path.join(PUBLIC_PATH, dirpath, dirname))

    for filename in filenames:
        if filename.startswith("_"):
            continue

        base, ext = os.path.splitext(filename)

        if ext == ".ct":
            with open(os.path.join(dirpath, filename)) as file:
                contents = file.read()

            contents = ct.parse(contents)

            new_filename = os.path.join(PUBLIC_PATH, dirpath, base + ".html")
            with open(new_filename, "w") as file:
                file.write(contents)
        else:
            shutil.copyfile(
                filename, os.path.join(PUBLIC_PATH, dirpath, filename))
