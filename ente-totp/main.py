import os
import sys

# Add the vendor directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import json
import logging
import pathlib
from collections import defaultdict
from datetime import datetime, timedelta

import keyring
import requests

import click
import pyotp

# Keychain service and account for storing the secrets
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"

LOGO_DEV_API_URL = "https://img.logo.dev/{domain}?token={api_key}"
LOGO_DEV_API_KEY = "pk_T0ZUG4poQGqfGcFoeCpRww"
ICONS_FOLDER = pathlib.Path.home() / ".local/share/ente-totp/icons"


def load_secrets():
    """Load secrets from the environment variable or keychain."""
    # Try to load from the cached environment variable first
    cached_secrets = os.getenv(CACHE_ENV_VAR)

    if cached_secrets:
        logging.warning("Loading secrets from environment variable cache.")
        return json.loads(cached_secrets)

    # If not cached, load from the keychain
    logging.warning("Loading secrets from keychain.")
    secrets_json = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)

    if secrets_json is None:
        raise Exception("No secrets found in keychain.")

    return json.loads(secrets_json)


@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("file", type=click.Path(exists=False), required=False)
def import_file(file):
    try:
        logging.warning(f"import_file: {file}")
        secret_dict = defaultdict(list)
        for service_name, username, secret in parse_secrets(file):
            secret_dict[service_name].append((username, secret))

        secrets_json = json.dumps(secret_dict)
        if secrets_json:
            keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT, secrets_json)

        download_icons(secret_dict.keys())
        logging.warning(
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
        logging.error(error_message)
        print(
            json.dumps(
                {"items": [{"title": "Import Failed", "subtitle": error_message}]}
            )
        )
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        print(
            json.dumps(
                {"items": [{"title": "Import Failed", "subtitle": error_message}]}
            )
        )


def parse_secrets(file_path="secrets.txt"):
    secrets_list = []
    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                line = line.replace("=sha1", "=SHA1")
                if "codeDisplay" in line:
                    line = line.split("codeDisplay")[0][:-1]

                parsed_uri = pyotp.parse_uri(line)
                if parsed_uri:
                    service_name = parsed_uri.issuer or parsed_uri.name
                    username = parsed_uri.name
                    secret = parsed_uri.secret
                    if secret:
                        secrets_list.append((service_name, username, secret))
                    else:
                        logging.warning(f"Unable to parse secret in: {line}")
                else:
                    logging.warning(f"Unable to parse the line: {line}")
    return secrets_list


def format_data(
    service_name, username, current_totp, next_totp, time_remaining, output_type
):
    """Format the TOTP data based on the output type."""
    time_unit = "second" if time_remaining == 1 else "seconds"
    subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}, {time_remaining} {time_unit} left"
    icon_path = get_icon_path(service_name)

    if output_type == "alfred":
        title = f"{service_name} - {username}" if username else service_name
        return {
            "title": title,
            "subtitle": subset,
            "arg": f"{current_totp},{next_totp}",
            "icon": {"path": str(icon_path)},
        }
    elif output_type == "json":
        return {
            "service_name": service_name,
            "username": username,
            "current_totp": current_totp,
            "next_totp": next_totp,
            "time_remaining": time_remaining,
            "service_data": subset,
            "icon_path": str(icon_path),
        }
    return None


def download_icon(service_name):
    if not LOGO_DEV_API_KEY:
        logging.warning("LOGO_DEV_API_KEY is not set. Skipping icon download.")
        return

    domain = (
        service_name.lower() if "." in service_name else f"{service_name.lower()}.com"
    )
    icon_url = LOGO_DEV_API_URL.format(domain=domain, api_key=LOGO_DEV_API_KEY)
    icon_path = ICONS_FOLDER / f"{service_name.replace('.', '_').lower()}.png"

    if not icon_path.exists():
        try:
            logging.warning(
                f"Attempting to download icon for {service_name} from {icon_url}"
            )
            response = requests.get(icon_url, timeout=5)
            logging.warning(
                f"Response status for {service_name}: {response.status_code}"
            )

            if response.status_code == 200:
                with open(icon_path, "wb") as icon_file:
                    icon_file.write(response.content)
                logging.warning(
                    f"Icon downloaded successfully for {service_name} at {icon_path}"
                )
            else:
                logging.warning(
                    f"Failed to download icon for {service_name}. Status code: {response.status_code}"
                )
        except requests.RequestException as e:
            logging.warning(f"Request failed for {service_name}: {e}")
    else:
        logging.warning(f"Icon already exists for {service_name} at {icon_path}")


def download_icons(services):
    ICONS_FOLDER.mkdir(parents=True, exist_ok=True)
    for service in services:
        download_icon(service)


def get_icon_path(service_name):
    sanitized_service_name = service_name.replace(" ", "").lower()
    icon_path = ICONS_FOLDER / f"{sanitized_service_name}.png"

    if icon_path.exists():
        logging.warning(f"Using downloaded icon for {service_name}")
        return icon_path

    logging.warning(f"No icon found for {service_name}, attempting to download.")
    download_icon(service_name)

    if icon_path.exists():
        logging.warning(f"Icon downloaded and saved for {service_name}")
        return icon_path
    else:
        logging.warning(
            f"Using default icon for {service_name}, download failed or icon not available."
        )
        return "icon.png"


@cli.command("get")
@click.argument("secret_id")
@click.option(
    "-o",
    "output_format",
    type=click.Choice(["json", "alfred"]),
    default="json",
    help="Data output format",
)
def generate_totp(secret_id, output_format):
    """Generate the current TOTP for a given secret."""
    try:
        # Load secrets from the cache or keychain
        data = load_secrets()
        items = []

        logging.warning(f"Searching for {secret_id} in {len(data)} services.\n")

        # Split the secret_id by spaces for more granular search
        search_parts = secret_id.lower().split()

        matches = []

        for service_name, service_data in data.items():
            for username, secret in service_data:
                # Lowercase the service_name and username for case-insensitive matching
                service_name_lower = service_name.lower()
                username_lower = username.lower()

                # Define match scores for prioritization
                score = 0
                if all(part in service_name_lower for part in search_parts):
                    score += 3  # Full match in service name
                if all(part in username_lower for part in search_parts):
                    score += 2  # Full match in username
                if any(part in service_name_lower for part in search_parts):
                    score += 1  # Partial match in service name
                if any(part in username_lower for part in search_parts):
                    score += 0.5  # Partial match in username

                if score > 0:
                    # Generate TOTP for the matching service
                    current_totp = pyotp.TOTP(secret).now()
                    next_time = datetime.now() + timedelta(seconds=30)
                    next_totp = pyotp.TOTP(secret).at(next_time)
                    time_remaining = 30 - (datetime.now().second % 30)
                    formatted_data = format_data(
                        service_name,
                        username,
                        current_totp,
                        next_totp,
                        time_remaining,
                        output_format,
                    )
                    matches.append((score, formatted_data))

        # Sort matches by score in descending order
        matches.sort(reverse=True, key=lambda x: x[0])
        items = [match[1] for match in matches]  # Extract the formatted results

        # Set the output JSON with the items (either matching services or no matches)

        output = (
            {"items": items}
            if items
            else {"items": [{"title": "No matching services found."}]}
        )

        # Always check if the secrets were cached, and include the cache variable
        if os.getenv(CACHE_ENV_VAR) is None:
            secrets_json = json.dumps(data)
            output["variables"] = {CACHE_ENV_VAR: secrets_json}

        print(json.dumps(output, indent=4))

    except Exception as e:
        logging.warning(f"Error: {str(e)}")
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()
