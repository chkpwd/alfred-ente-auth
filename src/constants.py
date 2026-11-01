from os import environ
from pathlib import Path

# Keychain service and account for storing the TOTP accounts
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"

workflow_data = environ.get("alfred_workflow_data")
if workflow_data:
    ICONS_FOLDER = Path(workflow_data) / "service_icons"
else:
    ICONS_FOLDER = Path("~/.cache/alfred-ente-auth").expanduser() / "service_icons"

ENTE_ICONS_DATABASE_URL = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/mobile/apps/auth/assets/custom-icons/_data/custom-icons.json"
ENTE_CUSTOM_ICONS_URL = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/mobile/apps/auth/assets/custom-icons/icons/"

# Simple Icons revision bundled with Ente Auth (v14.0.0). It includes icons removed from later
# Simple Icons releases, which Ente still offers. To update, use the submodule commit from:
#   gh api repos/ente-io/ente/contents/mobile/apps/auth/assets/simple-icons --jq .sha
ENTE_SIMPLE_ICONS_URL = "https://raw.githubusercontent.com/simple-icons/simple-icons/6dcfdc2f58f6150d7b097b5cab158d27413f6366/"
