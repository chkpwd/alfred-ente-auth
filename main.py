import logging
import os
import sys
from glob import glob

# Add the venv directory to the path
python_dirs = glob(os.path.join(os.path.dirname(__file__), ".venv/lib/python3.*"))
if python_dirs:
    sys.path.append(os.path.join(python_dirs[0], "site-packages"))
else:
    raise FileNotFoundError("Could not find python3.* directory in .venv/lib")

from src.ente_auth import EnteAuth  # noqa: E402, I001
from src.store_keychain import (  # noqa: E402
    ente_export_to_keychain,
    import_accounts_from_keychain,
)
from src.totp_accounts_manager import format_totp_result  # noqa: E402
from src.utils import (  # noqa: E402
    fuzzy_search_accounts,
    output_alfred_message,
    str_to_bool,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("No subcommand found. Use one of: import, search")

    elif sys.argv[1] == "import":
        ente_export_dir = os.getenv("ENTE_EXPORT_DIR")
        if not ente_export_dir:
            logger.error("ENTE_EXPORT_DIR not configured.")
            sys.exit(1)
        ente_export_path = os.path.join(
            os.path.expanduser(ente_export_dir), "ente_auth.txt"
        )

        overwrite_export = str_to_bool(os.getenv("OVERWRITE_EXPORT", "True"))

        ente_auth = EnteAuth()

        try:
            ente_auth.export_ente_auth_accounts(ente_export_path, overwrite_export)
            logger.info("Exported ente auth TOTP data to file.")
        except Exception as e:
            logger.exception(f"Failed to export ente auth TOTP data: {e}", e)
            output_alfred_message("Failed to export TOTP data", str(e))
        else:
            try:
                service_names_list: list[str] = []
                result = ente_export_to_keychain(ente_export_path)

                variables = result.variables
                totp_accounts = json.loads(variables[CACHE_ENV_VAR])

                for k, _ in totp_accounts.items():
                    try:
                        get_icon(sanitize_service_name(k), ICONS_FOLDER)
                    except Exception as e:
                        logger.warning(f"Failed to download icon: {e}")

                output_alfred_message(
                    "Imported TOTP data",
                    f"Successfully imported {import_result.count} TOTP accounts to keychain and Alfred cache.",
                    import_result.variables,
                )
            except Exception as e:
                logger.exception(
                    f"Failed to populate TOTP data in keychain from file: {e}", e
                )
                output_alfred_message("Failed to import TOTP data", str(e))

            ente_auth.delete_ente_export(ente_export_path)

    elif sys.argv[1] == "search":
        if len(sys.argv) < 3:
            raise ValueError("No search string found")

        try:
            accounts = import_accounts_from_keychain()
            logger.info("Loaded TOTP accounts from keychain.")
        except Exception as e:
            logger.exception(f"Failed to load TOTP accounts from keychain: {e}", e)
            output_alfred_message("Failed to load TOTP accounts", str(e))

        else:
            search_string = sys.argv[2]
            matched_accounts = fuzzy_search_accounts(search_string, accounts)
            formatted_account_data = format_totp_result(matched_accounts)
            formatted_account_data.print_json()
