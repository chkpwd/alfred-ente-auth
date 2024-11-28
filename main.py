import logging
import os
import sys

from src.constants import (
    CACHE_ENV_VAR,
    ICONS_FOLDER,
)
from src.ente_auth import EnteAuth
from src.icon_downloader import get_icon
from src.models import AlfredOutput
from src.store_keychain import (
    ente_export_to_keychain,
    get_totp_accounts,
)
from src.totp_accounts_manager import format_totp_result
from src.utils import (
    fuzzy_search_accounts,
    output_alfred_message,
    sanitize_service_name,
    str_to_bool,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def get_accounts(search_string: str | None = None) -> AlfredOutput | None:
    """
    Load TOTP accounts from the environment variable or keychain, filtering by `search_string`.
    Dumps the results to stdout in Alfred JSON format, adding all TotpAccounts for Alfred cache."""
    try:
        accounts = get_totp_accounts()
        logger.info("Loaded TOTP accounts.")
    except Exception as e:
        logger.exception(f"Failed to load TOTP accounts: {e}", e)
        output_alfred_message("Failed to load TOTP accounts", str(e))
    else:
        # Store all TOTP accounts for Alfred cache
        alfred_cache = {CACHE_ENV_VAR: accounts.to_json()}

        if search_string:
            accounts = fuzzy_search_accounts(search_string, accounts)

        # Format accounts/search results for Alfred, adding all accounts to the 'variables' key for Alfred cache.
        fmt_result = format_totp_result(accounts)
        fmt_result.variables = alfred_cache
        return fmt_result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("No subcommand found. Use one of: import, search, get_accounts")

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

                for k, _ in result.accounts.items():
                    try:
                        get_icon(sanitize_service_name(k), ICONS_FOLDER)
                    except Exception as e:
                        logger.warning(f"Failed to download icon: {e}")

                output_alfred_message(
                    "Imported TOTP data",
                    f"Successfully imported {result.count} TOTP accounts and downloaded icons.",
                    variables=result.accounts,
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

        results = get_accounts(sys.argv[2])
        if results:
            results.print_json()
        else:
            output_alfred_message("No results found", "Try a different search term.")

    elif sys.argv[1] == "get_accounts":
        accounts = get_accounts()
        if accounts:
            accounts.print_json()
        else:
            output_alfred_message("No TOTP accounts found", "Try importing some accounts.")
