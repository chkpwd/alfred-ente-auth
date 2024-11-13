import os
import json
import logging
import keyring

from collections import defaultdict

logger = logging.getLogger(__name__)

# Keychain service and account for storing the secrets
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"


def load_secrets():
    """Load secrets from the environment variable or keychain."""
    # Try to load from the cached environment variable first
    cached_secrets = os.getenv(CACHE_ENV_VAR)

    if cached_secrets:
        logger.warning("Loading secrets from environment variable cache.")
        return json.loads(cached_secrets)

    # If not cached, load from the keychain
    logger.warning("Loading secrets from keychain.")
    secrets_json = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)

    if secrets_json is None:
        raise Exception("No secrets found in keychain.")

    return json.loads(secrets_json)


def import_file(file):
    try:
        logger.warning(f"import_file: {file}")
        secret_dict = defaultdict(list)
        for service_name, username, secret in parse_secrets(file):
            secret_dict[service_name].append((username, secret))

        secrets_json = json.dumps(secret_dict)
        # Store secrets in the keychain
        if secrets_json:
            keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT, secrets_json)

        logger.warning(
            f"Database created with {sum(len(v) for v in secret_dict.values())} entries."
        )
        output = {
            "items": [
                {
                    "title": "Import Successful",
                    "subtitle": f"Database created with {sum(len(v) for v in secret_dict.values())} entries.",
                }
            ],
            "variables": {
                CACHE_ENV_VAR: secrets_json  # Set the TOTP_CACHE environment variable for Alfred
            },
        }
        print(json.dumps(output))

    except FileNotFoundError:
        error_message = f"File not found: {file}"
        logger.error(error_message)
        print(
            json.dumps(
                {"items": [{"title": "Import Failed", "subtitle": error_message}]}
            )
        )
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logger.error(error_message)
        print(
            json.dumps(
                {"items": [{"title": "Import Failed", "subtitle": error_message}]}
            )
        )
