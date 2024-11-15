import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class EnteAuth:
    def __init__(self):
        ente_auth_binary_path_env = os.getenv("ENTE_AUTH_BINARY_PATH")
        if ente_auth_binary_path_env:
            self.ente_auth_binary_path = self.check_ente_binary(
                ente_auth_binary_path_env
            )
        else:
            self.ente_auth_binary_path = self._find_ente_path()

    def _find_ente_path(self) -> str:
        result = subprocess.run(
            ["which", "ente"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            raise OSError("'ente' binary not found. Please ensure it's installed.")

        return result.stdout.decode("utf-8").strip()

    def create_ente_path(self, path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"Ente folder created at: {path}")

    def export_ente_auth_accounts(self, export_path: str, overwrite: bool) -> None:
        path_exists = os.path.exists(export_path)

        if path_exists and overwrite:
            logger.debug("Ente auth export file found. Overwrite is true. Deleting...")
            self.delete_ente_export(export_path)
        elif path_exists and not overwrite:
            logger.info("Export file already exists. Skipping export.")
            return

        logger.debug("Ente auth export file not found. Exporting...")
        try:
            result = subprocess.run(
                ["ente", "export"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # When export directory doesn't exist, Ente CLI still returns rc0 but prints an error to stderr.
            # If this happens, we'll create the path and retry.
            if "error: path does not exist" in result.stderr.decode("utf-8"):
                export_dir = os.path.dirname(export_path)
                logger.info(f"Export directory does not exist. Creating: {export_dir}")
                self.create_ente_path(export_dir)
                logger.info("Retrying export...")
                self.export_ente_auth_accounts(export_path, overwrite)

        except subprocess.CalledProcessError as e:
            logger.exception("Export failed", e)
            raise e

        if not os.path.exists(export_path):
            raise Exception(
                "Export appeared to succeed, but the export file was not found."
            )

    def delete_ente_export(self, export_path: str) -> None:
        try:
            os.remove(export_path)
            logger.info("Ente export file deleted")
        except OSError as e:
            logger.exception("Error during removal", e)
            raise e

    @staticmethod
    def check_ente_binary(path) -> bool:
        try:
            subprocess.run([f"{path}", "version"], check=True)
            return True
        except subprocess.CalledProcessError:
            logger.error(
                f"Ente binary not found at {path}. Please check ente CLI is installed and the path is correct."
            )
            return False
