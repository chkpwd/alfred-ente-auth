from os import environ
from pathlib import Path

# Keychain service and account for storing the TOTP accounts
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"

ICONS_FOLDER = Path(environ["alfred_workflow_data"]) / "service_icons"

ENTE_ICONS_DATABASE_URL = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/auth/assets/custom-icons/_data/custom-icons.json"
ENTE_CUSTOM_ICONS_URL = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/auth/assets/custom-icons/icons/"
