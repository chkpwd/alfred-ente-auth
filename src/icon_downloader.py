import logging
from functools import lru_cache
from pathlib import Path
from urllib.parse import urljoin

from src.constants import (
    ENTE_CUSTOM_ICONS_URL,
    ENTE_ICONS_DATABASE_URL,
    ENTE_SIMPLE_ICONS_URL,
)
from src.models import TotpAccount
from src.utils import sanitize_service_name

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 15

# Summaries of icon download errors, shown in the import result
ICON_DOWNLOAD_ERRORS: list[str] = []

# Port of Ente Auth's charMap, used to derive a Simple Icons file name from its title
# https://github.com/ente-io/ente/blob/main/mobile/apps/auth/lib/ui/utils/icon_utils.dart
SIMPLE_ICONS_CHAR_MAP = {
    **dict.fromkeys("áàâäã", "a"),
    **dict.fromkeys("éèêë", "e"),
    **dict.fromkeys("íìîï", "i"),
    **dict.fromkeys("óòôö", "o"),
    **dict.fromkeys("úùûü", "u"),
    "ç": "c",
    "ñ": "n",
    "ř": "r",
    "š": "s",
    "ż": "z",
    ".": "dot",
    "&": "and",
    "+": "plus",
    **dict.fromkeys("-:'/!_°", ""),
}


def simple_icon_slug(title: str) -> str:
    """Derives the Simple Icons file name for a title, as Ente Auth does."""
    title = title.replace(" ", "").lower()
    return "".join(SIMPLE_ICONS_CHAR_MAP.get(c, c) for c in title).strip()


def record_download_error(e: Exception) -> None:
    """Records a short description of a download error, without URLs or account data."""
    import requests

    if isinstance(e, requests.exceptions.SSLError):
        message = "HTTPS certificate error while downloading icons."
    elif isinstance(e, requests.exceptions.ProxyError):
        message = "Proxy connection failed while downloading icons."
    elif isinstance(e, requests.exceptions.Timeout):
        message = "Icon downloads timed out."
    elif isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
        message = f"Icon server returned HTTP {e.response.status_code}."
    elif isinstance(e, requests.exceptions.ConnectionError):
        message = "Could not connect to the icon server."
    else:
        message = "Icon server returned invalid data."
    if message not in ICON_DOWNLOAD_ERRORS:
        ICON_DOWNLOAD_ERRORS.append(message)


@lru_cache(maxsize=None)
def load_icon_database(url: str) -> list[dict]:
    """Downloads an icon database once per import, returning an empty list on failure."""
    import requests

    from src.http_client import get_icon_session

    try:
        response = get_icon_session().get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        record_download_error(e)
        logger.error(f"Failed to fetch icon database: {e}")
        return []
    return data.get("icons", []) if isinstance(data, dict) else data


def search_ente_custom_icons(name: str) -> str | None:
    """
    Searches Ente custom icons on GitHub for the provided name and returns the SVG content if found.
    """
    import requests

    from src.http_client import get_icon_session

    try:
        # Ente matches titles with spaces removed
        matching_icon = [
            icon["slug"] if icon.get("slug") else icon["title"].replace(" ", "").lower()
            for icon in load_icon_database(ENTE_ICONS_DATABASE_URL)
            if name.replace(" ", "").lower()
            in [
                icon["title"].replace(" ", "").lower(),
                icon.get("slug", "").lower(),
                *[name.replace(" ", "").lower() for name in icon.get("altNames", [])],
            ]
        ]
        if matching_icon:
            response = get_icon_session().get(
                urljoin(ENTE_CUSTOM_ICONS_URL, f"{matching_icon[0]}.svg"),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.text
        else:
            logger.debug(f"Icon for '{name}' not found in Ente custom icons.")
    except requests.RequestException as e:
        record_download_error(e)
        logger.error(f"Error while fetching custom icons: {e}")


def search_simple_icons(name: str) -> str | None:
    """Searches Simple Icons for the provided name and returns the SVG content if found."""
    from simplepycons import all_icons
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


def search_ente_simple_icons(name: str) -> str | None:
    """
    Searches the Simple Icons revision used by Ente Auth, which includes icons removed from
    later releases, and returns the SVG content if found.
    """
    import requests

    from src.http_client import get_icon_session

    database_url = urljoin(ENTE_SIMPLE_ICONS_URL, "_data/simple-icons.json")
    for icon in load_icon_database(database_url):
        if icon["title"].replace(" ", "").lower() == name.replace(" ", "").lower():
            slug = icon.get("slug") or simple_icon_slug(icon["title"])
            try:
                response = get_icon_session().get(
                    urljoin(ENTE_SIMPLE_ICONS_URL, f"icons/{slug}.svg"),
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()
            except requests.RequestException as e:
                record_download_error(e)
                logger.error(f"Error while fetching Simple Icons: {e}")
                return None
            return response.text.replace("<svg ", f'<svg fill="#{icon["hex"]}" ', 1)
    logger.debug(f"Icon for '{name}' not found in Ente's Simple Icons.")


def download_account_icon(account: TotpAccount, icons_dir: Path) -> None:
    """
    Downloads the icon selected in Ente for the account, looked up the way Ente Auth does.
    Falls back to the icon for the account's service name.
    """
    if account.selected_icon_name:
        icon = (
            search_ente_custom_icons(account.icon_id)
            or search_simple_icons(simple_icon_slug(account.icon_id))
            or search_ente_simple_icons(account.icon_id)
        )
        if icon:
            icons_dir.mkdir(parents=True, exist_ok=True)
            icon_path = icons_dir / f"{account.selected_icon_name}.svg"
            with open(icon_path, mode="w") as icon_file:
                icon_file.write(icon)
            logger.debug(f"Selected icon imported successfully at {icon_path}")
            return
        logger.warning(f"Could not find the selected icon {account.icon_id}")

    download_icon(sanitize_service_name(account.service_name), icons_dir)
