import logging
from pathlib import Path
from urllib.parse import urljoin

import requests
from simplepycons import all_icons

logger = logging.getLogger(__name__)


def get_ente_custom_icon(name: str):
    icons_database_url = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/auth/assets/custom-icons/_data/custom-icons.json"
    ente_custom_icons_db = "https://raw.githubusercontent.com/ente-io/ente/refs/heads/main/auth/assets/custom-icons/icons/"

    try:
        response = requests.get(icons_database_url)

        if response.status_code == 200:
            ente_custom_icons = response.json()
            matching_icon = [
                icon["slug"] if icon.get("slug") else icon["title"].lower()
                for icon in ente_custom_icons.get("icons", [])
                if name.lower()
                in [
                    icon["title"].lower(),
                    icon.get("slug", "").lower(),
                    *[name.lower() for name in icon.get("altNames", [])],
                ]
            ]
            # matching_icon: next(icon["slug"] for icon in iter(ente_custom_icons) if name.lower() in )
            if matching_icon:
                response = requests.get(
                    urljoin(ente_custom_icons_db, f"{matching_icon[0]}.svg")
                )
                response.raise_for_status()
                return response.text
        else:
            logger.error(f"Failed to fetch custom icons: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error while fetching custom icons: {e}")


def get_simplepycons_icon(name: str):
    """
    Gets an icon for a given service name.

    Returns:
        str: Path to the icon, or the default icon if retrieving the object fails.
    """

    try:
        simplepycons_icon = all_icons[name].raw_svg  # type: ignore
        return str(simplepycons_icon)

    except KeyError:
        logger.warning(f"Icon for '{name}' not found in Simplepycons.")


def get_icon(service: str, icons_dir: Path):
    icons_dir.mkdir(parents=True, exist_ok=True)
    icon_path = icons_dir / f"{service}.svg"

    ente_custom_icon_url = get_ente_custom_icon(service)
    simplepycons_icon = get_simplepycons_icon(service)

    icon = (
        ente_custom_icon_url
        if ente_custom_icon_url
        else simplepycons_icon
        if simplepycons_icon
        else None
    )

    if icon:
        with open(icon_path, mode="w") as icon_file:
            icon_file.write(icon)
        logger.debug(f"Icon imported successfully for {service} at {icon_path}")
