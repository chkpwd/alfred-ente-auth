#!/usr/bin/env python3

import os
import plistlib
import shutil
import subprocess
from zipfile import ZIP_STORED, ZipFile

import tomllib

WORKFLOW_PLIST_PATH = "info.plist"


def find_venv_py_version() -> str:
    venv_python_version = os.listdir(os.path.join(os.getcwd(), ".venv", "lib"))[0]
    return venv_python_version


def parse_info_plist():
    """Parse a plist file"""
    with open(WORKFLOW_PLIST_PATH, "rb") as f:
        plist = plistlib.load(f)
    return plist


def get_workflow_name(plist):
    """Get the workflow name from parsed plist"""
    name = plist["name"].replace(" ", "_").lower()
    return name


def get_pyproject_version():
    """Get the project version from pyproject.toml"""
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
    version = pyproject["tool"]["poetry"]["version"]
    return version


def get_workflow_version(plist):
    """Get the workflow version from parsed plist"""
    version = plist["version"].replace(" ", "_").lower()
    return version


def update_workflow_version(plist, version: str):
    """Update "version" string in parsed plist"""
    plist["version"] = version
    with open(WORKFLOW_PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)


def update_workflow_pythonpath(plist, python_dirname: str):
    """Update "PYTHONPATH" in parsed plist"""
    script_filters = [
        obj
        for obj in plist["objects"]
        if obj["type"] == "alfred.workflow.input.scriptfilter"
    ]

    for script_filter in script_filters:
        print(script_filter)
        script_lines = str(script_filter["config"]["script"]).split("\n")
        pythonpath = os.path.join(".venv", "lib", python_dirname, "site-packages")
        script_lines[0] = f"export PYTHONPATH='{pythonpath}'"
        script_filter["config"]["script"] = "\n".join(script_lines)

    with open(WORKFLOW_PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)


def init_venv():
    """Initialize the venv"""

    if os.path.exists(".venv"):
        shutil.rmtree(".venv")

    subprocess.run(["poetry", "install", "--only", "main"], check=True)

    print("Dependencies installed successfully.")


def zip_workflow(filename: str):
    """Zip the workflow"""
    basepath = os.getcwd()

    zip_contents = [
        "icon.png",
        "info.plist",
        "main.py",
        "src",
        ".venv",
    ]
    zip_contents = [os.path.join(basepath, file) for file in zip_contents]
    zip_exlude = ["__pycache__"]

    def should_include(path):
        exclude_paths = any(excluded in path for excluded in zip_exlude)
        include_paths = any(included in path for included in zip_contents)
        return not exclude_paths and include_paths

    with ZipFile(filename, "w", ZIP_STORED, strict_timestamps=False) as zip:
        for root, _, files in os.walk(basepath):
            for file in files:
                full_path = os.path.join(root, file)
                if should_include(full_path):
                    arcname = os.path.relpath(full_path, basepath)
                    zip.write(full_path, arcname)


def main():
    plist = parse_info_plist()

    workflow_name = get_workflow_name(plist)
    workflow_version = get_workflow_version(plist)
    pyproject_version = get_pyproject_version()

    init_venv()

    venv_python_version = find_venv_py_version()
    update_workflow_pythonpath(plist, venv_python_version)

    if workflow_version != pyproject_version:
        update_workflow_version(plist, pyproject_version)
        workflow_version = pyproject_version
    else:
        print(
            "\nWARNING: Workflow version matches PyProject version. Should this be updated?"
        )

    zip_name = f"{workflow_name}_{workflow_version}.alfredworkflow"
    zip_workflow(zip_name)

    if os.getenv("GITHUB_ACTIONS"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"OUTPUT_FILE={zip_name}\n")

        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("# Alfred Workflow Build\n")
            f.write(f"* Workflow name: {workflow_name}\n")
            f.write(f"* Workflow version: {workflow_version}\n")
            f.write(f"* Pyproject version: {pyproject_version}\n")
            f.write(f"* ZIP name: {zip_name}\n")


if __name__ == "__main__":
    main()
