import logging
import os
import sys
from difflib import get_close_matches

from attrs.converters import to_bool

from src.ente_auth import EnteAuth
from src.secrets_manager import format_secrets_data, parse_secrets
from src.store_keychain import ente_export_to_keychain, import_secrets_from_keychain

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the vendor directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))


"""
TODO:
- [x] Add import
- [x] Add export
- [x] Add parsing
- [x] Check keyring for secrets
- [x] Add error handling
- [x] Check caching works correctly
- [x] Check if ente is installed
- [] Add testing
- [] Redo deps in a better way (poetry, maybe?)
- [] Check lowercase
- [] implement fuzzy search
- [] Improve logging/error handling. Need a consistent way of handling and returning errors. Always to Alfred? Probably not. Categorise by whether it should go to the user/Alfred or not, maybe helper functions ¯\\_(ツ)_/¯
"""

if __name__ == "__main__":
    if not sys.argv[1]:
        raise ValueError("No subcommand found. Use one of: import, search")

    elif sys.argv[1] == "import":
        ente_export_dir = os.getenv("ENTE_EXPORT_DIR")
        if not ente_export_dir:
            logger.error("ENTE_EXPORT_DIR not configured.")
            sys.exit(1)
        ente_export_path = os.path.join(
            os.path.expanduser(ente_export_dir), "ente_auth.txt"
        )

        overwrite_export = to_bool(os.getenv("OVERWRITE_EXPORT", "True"))

        ente_auth = EnteAuth()

        try:
            ente_auth.export_ente_auth_secrets(ente_export_path, overwrite_export)
            logger.info("Exported ente auth secrets to file.")
        except Exception as e:
            logger.error(f"Failed to export ente auth secrets: {e}")
        else:
            try:
                ente_export_to_keychain(ente_export_path)
            except Exception as e:
                logger.error(f"Failed to import secrets from file: {e}")

            ente_auth.delete_ente_export(ente_export_path)

    elif sys.argv[1] == "search":
        if not sys.argv[2]:
            raise ValueError("No search string found")

        try:
            secrets = import_secrets_from_keychain()
            logger.info("Loaded secrets from keychain.")
        except Exception as e:
            logger.exception(f"Failed to load secrets from keychain: {e}", e)

        else:
            search_string = sys.argv[2]
            # matches = get_close_matches(search_string, secrets.keys())
            print(secrets.to_json())
            # for service_name, username, secret in secrets:
            #     if service_name in secrets:
            #         current_totp = secrets[service_name][0]

    else:
        raise ValueError(f"Unrecognized subcommand: {sys.argv[1]}")
