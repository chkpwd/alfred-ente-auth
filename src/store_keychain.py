import logging
import os

import keyring

from src.constants import CACHE_ENV_VAR, KEYCHAIN_ACCOUNT, KEYCHAIN_SERVICE
from src.models import ImportResult, TotpAccounts
from src.totp_accounts_manager import parse_ente_export
from src.utils import output_alfred_message

logger = logging.getLogger(__name__)

def get_totp_accounts() -> TotpAccounts:
    """Load TOTP accounts from Alfred session cache or keychain."""
    cached_accounts = os.getenv(CACHE_ENV_VAR)

    if cached_accounts:
        logger.info("Loading TOTP accounts from environment variable cache.")
        return TotpAccounts().from_json(cached_accounts)

    # If not cached, load from the keychain
    logger.info("Loading TOTP accounts from keychain.")
    accounts_json = keyring.get_password(
        service_name=KEYCHAIN_SERVICE, username=KEYCHAIN_ACCOUNT
    )

    if accounts_json is None:
        raise Exception("No TOTP accounts found in keychain.")

    accounts = TotpAccounts().from_json(accounts_json)

    return accounts


def ente_export_to_keychain(file: str) -> ImportResult:
    """Import TOTP accounts from an Ente export file and store them in the keychain."""
    try:
        logger.debug(f"import_file: {file}")

        accounts = parse_ente_export(file)
        accounts_json = accounts.to_json()

        keyring.set_password(
            service_name=KEYCHAIN_SERVICE,
            username=KEYCHAIN_ACCOUNT,
            password=accounts_json,
        )

        secrets_imported_count = sum(len(k) for k in accounts.items())

        logger.info(f"Keychain database created with {secrets_imported_count} entries.")

        return ImportResult(secrets_imported_count, accounts)

    except FileNotFoundError as e:
        output_alfred_message("Import Failed", f"File not found: {file}")
        raise e

    except Exception as e:
        output_alfred_message("Import Failed", f"An error occurred during Ente export: {str(e)}")
        raise e
