import json
import logging
import os

import keyring

from src.constants import CACHE_ENV_VAR, KEYCHAIN_ACCOUNT, KEYCHAIN_SERVICE
from src.models import AlfredOutput, AlfredOutputItem, ImportResult, TotpAccounts
from src.totp_accounts_manager import parse_ente_export

logger = logging.getLogger(__name__)

def get_totp_accounts() -> TotpAccounts:
    """Load TOTP accounts from the environment variable or keychain."""
    cached_accounts = os.getenv(CACHE_ENV_VAR)

    if cached_accounts:
        logger.info("Loading TOTP accounts from environment variable cache.")
        return json.loads(cached_accounts)

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
    result = ImportResult(0, {})

    try:
        logger.debug(f"import_file: {file}")

        accounts = parse_ente_export(file)
        accounts_json = accounts.to_json()

        if accounts:
            keyring.set_password(
                service_name=KEYCHAIN_SERVICE,
                username=KEYCHAIN_ACCOUNT,
                password=accounts_json,
            )

        secrets_imported_count = sum(len(k) for k in accounts.items())

        logger.info(f"Keychain database created with {secrets_imported_count} entries.")

        result.count = secrets_imported_count
        result.variables = {CACHE_ENV_VAR: accounts_json}

    except FileNotFoundError:
        error_message = f"File not found: {file}"
        logger.error(error_message)
        AlfredOutput(
            [
                AlfredOutputItem(
                    title="Import Failed",
                    subtitle=f"File not found: {file}",
                )
            ]
        ).print_json()

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.exception(error_message, e)
        AlfredOutput(
            [
                AlfredOutputItem(
                    title="Import Failed",
                    subtitle=error_message,
                )
            ]
        ).print_json()

    return result
