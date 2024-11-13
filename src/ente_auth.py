import os
import logging
import subprocess

from pathlib import Path

logger = logging.getLogger(__name__)

# Ente Auth Binary Path
ENTE_AUTH_BINARY_PATH = "/usr/local/bin/ente"
DEFAULT_EXPORT_PATH = f"{str(Path.home())}/Documents/ente"


def create_ente_path(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info("Ente folder created at", path)

    return path

def check_ente_binary() -> bool:
    try:
        subprocess.run([f"{ENTE_AUTH_BINARY_PATH}", "version"], check=True)
        return True
    except subprocess.CalledProcessError:
        logger.error("Ente binary not found. Please install it.")
        return False

def export_ente_auth_secrets() -> bool:
    export_file_path = f"{DEFAULT_EXPORT_PATH}/ente_auth.txt"
    if not os.path.exists(export_file_path):
        logger.info("ente_auth.txt not found. Exporting...")
        try:
            subprocess.run(["ente", "export"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Export failed: {e}")
            return False

        if not os.path.exists(export_file_path):
            logger.error("Export failed. Please check if the command is correct.")
            return False
    else:
        logger.info("Skipping export...")

    return True

def delete_ente_export() -> bool:
    try:
        os.remove(f"{DEFAULT_EXPORT_PATH}/ente_auth.txt")
    except OSError as e:
        logger.error(f"Error during removal: {e}")
        return False

    return True
