import logging
from pathlib import Path
from urllib.parse import urljoin

import requests
from simplepycons import all_icons

from src.constants import ENTE_CUSTOM_ICONS_URL, ENTE_ICONS_DATABASE_URL

logger = logging.getLogger(__name__)


def search_ente_custom_icons(name: str) -> str | None:
    """
    Searches Ente custom icons on GitHub for the provided name and returns the SVG content if found.
    """
    try:
        response = requests.get(ENTE_ICONS_DATABASE_URL)

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
                    urljoin(ENTE_CUSTOM_ICONS_URL, f"{matching_icon[0]}.svg")
                )
                response.raise_for_status()
                return response.text
            else:
                logger.debug(f"Icon for '{name}' not found in Ente custom icons.")
        else:
            logger.error(f"Failed to fetch custom icons: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error while fetching custom icons: {e}")


def search_simple_icons(name: str) -> str | None:
    """Searches Simple Icons for the provided name and returns the SVG content if found."""
    try:
        icon = all_icons[name]  # type: ignore
    except KeyError:
        logger.debug(f"Icon for '{name}' not found in Simple Icons.")
    else:
        icon = icon.customize_svg_as_str(fill=icon.primary_color)
        return str(icon)


def download_icon(service: str, icons_dir: Path) -> None:
    """Downloads the icon for the given service and saves it to the provided icons directory if found."""
    icons_dir.mkdir(parents=True, exist_ok=True)
    icon_path = icons_dir / f"{service}.svg"

    ente_custom_icon_url = search_ente_custom_icons(service)
    simplepycons_icon = search_simple_icons(service)

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
    else:
        logger.warning(f"Could not find an icon for {service}")
