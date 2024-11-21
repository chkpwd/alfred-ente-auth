import logging
import os
import pathlib

import requests

LOGO_DEV_API_URL = "https://img.logo.dev/{domain}?token={api_key}"
LOGO_DEV_API_KEY = "pk_T0ZUG4poQGqfGcFoeCpRww"
ICONS_FOLDER = pathlib.Path.home() / ".local/share/ente-totp/icons"


def sanitize_service_name(service_name):
    return service_name.split("-")[0].strip()


def download_icon(service_name):
    """
    Downloads an icon for a given service name.

    Returns:
        str: Path to the downloaded icon, or the default icon if download fails.
    """
    sanitized_name = sanitize_service_name(service_name)

    if not LOGO_DEV_API_KEY:
        logging.warning("LOGO_DEV_API_KEY is not set. Skipping icon download.")
        return "icon.png"

    # Determine the domain for the icon service
    domain = (
        sanitized_name.lower()
        if "." in sanitized_name
        else f"{sanitized_name.lower()}.com"
    )
    icon_url = LOGO_DEV_API_URL.format(domain=domain, api_key=LOGO_DEV_API_KEY)
    icon_path = ICONS_FOLDER / f"{sanitized_name.replace('.', '_').lower()}.png"

    if not icon_path.exists():
        try:
            logging.warning(
                f"Attempting to download icon for {sanitized_name} from {icon_url}"
            )
            response = requests.get(icon_url, timeout=5)
            logging.warning(
                f"Response status for {sanitized_name}: {response.status_code}"
            )

            if response.status_code == 200:
                ICONS_FOLDER.mkdir(parents=True, exist_ok=True)
                with open(icon_path, "wb") as icon_file:
                    icon_file.write(response.content)
                logging.warning(
                    f"Icon downloaded successfully for {sanitized_name} at {icon_path}"
                )
            else:
                logging.warning(
                    f"Failed to download icon for {sanitized_name}. Status code: {response.status_code}"
                )
                return "icon.png"
        except requests.RequestException as e:
            logging.warning(f"Request failed for {sanitized_name}: {e}")
            return "icon.png"
    else:
        logging.warning(f"Icon already exists for {sanitized_name} at {icon_path}")

    return str(icon_path)


def get_icon_path(service_name):
    """
    Gets the path to the icon for a given service, downloading it if necessary.

    Returns:
        str: Path to the icon file.
    """
    sanitized_name = sanitize_service_name(service_name)
    sanitized_service_name = sanitized_name.replace(" ", "").lower()
    icon_path = ICONS_FOLDER / f"{sanitized_service_name}.png"

    if icon_path.exists():
        logging.warning(f"Using downloaded icon for {sanitized_name}")
        return str(icon_path)

    logging.warning(f"No icon found for {sanitized_name}, attempting to download.")
    return download_icon(sanitized_name)


def download_icons(services):
    ICONS_FOLDER.mkdir(parents=True, exist_ok=True)
    for service in services:
        download_icon(service)
