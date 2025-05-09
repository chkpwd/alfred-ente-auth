import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class EnteAuth:
    def __init__(self):
        env_path = os.getenv("ENTE_AUTH_BINARY_PATH")

        if env_path:
            ente_auth_binary_path_env = Path(env_path).expanduser()

            if self.check_ente_binary(ente_auth_binary_path_env):
                self.ente_auth_binary_path = ente_auth_binary_path_env
            else:
                raise OSError(
                    f"Ente binary was not found at '{ente_auth_binary_path_env}' or is not executable. Please check the path is correct."
                )
        else:
            self.ente_auth_binary_path = self._find_ente_path()

    def _find_ente_path(self) -> str:
        """Returns the path to the ente binary if it can be found."""
        result = subprocess.run(
            ["which", "ente"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            raise OSError("'ente' binary not found. Please ensure it's installed.")

        return result.stdout.decode("utf-8").strip()

    def create_ente_export_dir(self, path: Path) -> None:
        if not path.exists():
            os.makedirs(path)
            logger.info(f"Ente folder created at: {path}")

    def export_ente_auth_accounts(self, export_path: Path, overwrite: bool) -> None:
        """
        Execute Ente export command.

        Handles removing an old export file if it exists and overwrite is True, and creating the export directory if it doesn't exist.
        """
        export_path = export_path.expanduser()

        if export_path.exists() and overwrite:
            logger.debug("Ente auth export file found. Overwrite is true. Deleting...")
            self.delete_ente_export(export_path)
        elif export_path.exists() and not overwrite:
            logger.info("Export file already exists. Skipping export.")
            return

        logger.debug("Ente auth export file not found. Exporting...")
        try:
            result = subprocess.run(
                [self.ente_auth_binary_path, "export"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # When export directory doesn't exist, Ente CLI still returns rc0 but prints an error to stderr.
            # If this happens, we'll create the path and retry.
            if "error: path does not exist" in result.stderr.decode("utf-8"):
                export_dir = export_path.parent
                logger.info(f"Export directory does not exist. Creating: {export_dir}")
                self.create_ente_export_dir(Path(export_dir))
                logger.info("Retrying export...")
                self.export_ente_auth_accounts(export_path, overwrite)

        except subprocess.CalledProcessError as e:
            logger.error("Export failed", e)
            raise e

        if not export_path.exists():
            raise OSError(
                "Export appeared to succeed, but the export file was not found."
            )

    def delete_ente_export(self, export_path: Path) -> None:
        try:
            export_path.unlink()
            logger.info("Ente export file deleted")
        except OSError as e:
            logger.error("Error during removal", e)
            raise e

    @staticmethod
    def check_ente_binary(path: Path) -> bool:
        """Check if the ente binary exists and is executable."""
        try:
            subprocess.run(
                [path, "version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except subprocess.CalledProcessError:
            logger.error(
                f"Ente binary not found at {path}. Please check ente CLI is installed and the path is correct."
            )
            return False
