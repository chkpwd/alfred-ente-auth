import os
import json
import logging
import keyring

from src.secrets_manager import parse_secrets
from src.models import AlfredOutput, AlfredOutputItem, TotpAccounts

logger = logging.getLogger(__name__)

# Keychain service and account for storing the secrets
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"


def import_secrets_from_keychain() -> TotpAccounts:
    """Load secrets from the environment variable or keychain."""
    cached_secrets = os.getenv(CACHE_ENV_VAR)

    if cached_secrets:
        logger.info("Loading secrets from environment variable cache.")
        return json.loads(cached_secrets)

    # If not cached, load from the keychain
    logger.info("Loading secrets from keychain.")
    secrets_json = keyring.get_password(
        service_name=KEYCHAIN_SERVICE, username=KEYCHAIN_ACCOUNT
    )

    if secrets_json is None:
        raise Exception("No secrets found in keychain.")

    accounts = TotpAccounts().from_json(secrets_json)

    return accounts


def ente_export_to_keychain(file: str) -> None:
    """Import secrets from an Ente export file and store them in the keychain."""
    try:
        logger.debug(f"import_file: {file}")

        accounts = parse_secrets(file)
        accounts_json = accounts.to_json()

        if accounts:
            keyring.set_password(
                service_name=KEYCHAIN_SERVICE,
                username=KEYCHAIN_ACCOUNT,
                password=accounts_json,
            )

        logger.info(
            f"Keychain database created with {sum(len(k) for k in accounts.items())} entries."
        )

        output = {
            "variables": {
                CACHE_ENV_VAR: accounts_json  # Set the TOTP_CACHE environment variable for Alfred
            },
        }

        logger.debug(json.dumps(output))

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
