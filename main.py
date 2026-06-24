import logging
import os
import sys
from pathlib import Path

from src.constants import (
    CACHE_ENV_VAR,
    ICONS_FOLDER,
)
from src.models import AlfredOutput
from src.store_keychain import get_totp_accounts
from src.totp_accounts_manager import format_totp_result
from src.utils import (
    fuzzy_search_accounts,
    output_alfred_message,
    str_to_bool,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



def get_accounts(search_string: str | None = None) -> AlfredOutput:
    """
    Load TOTP accounts from the environment variable or keychain, filtering by `search_string`.
    """
    accounts = get_totp_accounts()
    logger.info("Loaded TOTP accounts.")

    # Get the session seed for UIDs to clear Alfred's knowledge sorting across session boundaries
    uid_seed = os.getenv("UID_SEED")
    if not uid_seed:
        import uuid
        uid_seed = str(uuid.uuid4())

    # Store all TOTP accounts for Alfred cache along with the UID seed
    alfred_cache = {
        CACHE_ENV_VAR: accounts.to_json(),
        "UID_SEED": uid_seed
    }

    if search_string:
        accounts = fuzzy_search_accounts(search_string, accounts)
    else:
        from src.utils import get_local_usage
        accounts.sort(key=lambda x: (x.pinned, get_local_usage(x.service_name, x.username), x.tap_count, x.last_used_at), reverse=True)

    # Format accounts/search results for Alfred, adding all accounts to the 'variables' key for Alfred cache.
    fmt_result = format_totp_result(accounts, uid_seed=uid_seed)
    fmt_result.variables = alfred_cache
    return fmt_result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(
            "No subcommand found. Use one of: import, search, get_accounts, record_usage"
        )

    elif sys.argv[1] == "import":
        from src.ente_auth import EnteAuth
        from src.icon_downloader import download_icon
        from src.store_keychain import ente_export_to_keychain
        from src.utils import sanitize_service_name

        ente_export_dir = os.getenv("ENTE_EXPORT_DIR")
        if not ente_export_dir:
            logger.error("ENTE_EXPORT_DIR not configured.")
            sys.exit(1)

        ente_export_path = Path(ente_export_dir).expanduser() / "ente_auth.txt"

        overwrite_export = str_to_bool(os.getenv("OVERWRITE_EXPORT", "True"))

        ente_auth = EnteAuth()

        try:
            try:
                ente_auth.export_ente_auth_accounts(ente_export_path, overwrite_export)
                logger.info("Exported ente auth TOTP data to file.")
            except Exception as e:
                logger.exception(f"Failed to export ente auth TOTP data: {e}", e)
                output_alfred_message("Failed to export TOTP data", str(e))
                sys.exit(1)

            try:
                # Clear local workflow usage database on import to fall back to Ente's usage numbers
                from src.utils import get_usage_db_path
                try:
                    usage_path = get_usage_db_path()
                    if usage_path.exists():
                        usage_path.unlink()
                        logger.info("Cleared local workflow usage database on import.")
                except Exception as e:
                    logger.warning(f"Failed to clear local workflow usage database: {e}")

                result = ente_export_to_keychain(ente_export_path)

                for k in result.accounts:
                    try:
                        download_icon(sanitize_service_name(k.service_name), ICONS_FOLDER)
                    except Exception as e:
                        logger.warning(f"Failed to download icon: {e}")

                output_alfred_message(
                    "Imported TOTP data",
                    f"Successfully imported {result.count} TOTP accounts and downloaded icons.",
                    variables={CACHE_ENV_VAR: result.accounts.to_json()},
                )
            except Exception as e:
                output_alfred_message("Failed to import TOTP data", str(e))
                logger.exception(
                    f"Failed to populate TOTP data in keychain from file: {e}", e
                )
        finally:
            if ente_export_path.exists():
                ente_auth.delete_ente_export(ente_export_path)

    elif sys.argv[1] == "search":
        search_str = sys.argv[2] if len(sys.argv) >= 3 else ""
        if search_str == "{query}":
            search_str = ""
        try:
            results = get_accounts(search_str)
            if results and results.items:
                results.print_json()
            else:
                output_alfred_message("No results found", "Try a different search term.")
        except Exception as e:
            logger.exception(f"Failed to load TOTP accounts: {e}", e)
            output_alfred_message("Failed to load TOTP accounts", str(e))

    elif sys.argv[1] == "get_accounts":
        try:
            accounts = get_accounts()
            if accounts and accounts.items:
                accounts.print_json()
            else:
                output_alfred_message("No TOTP accounts found", "Try importing some accounts.")
        except Exception as e:
            logger.exception(f"Failed to load TOTP accounts: {e}", e)
            output_alfred_message("Failed to load TOTP accounts", str(e))

    elif sys.argv[1] == "record_usage":
        from src.utils import record_local_usage
        service = os.getenv("selected_service")
        username = os.getenv("selected_username")
        if service:
            record_local_usage(service, username or "")
