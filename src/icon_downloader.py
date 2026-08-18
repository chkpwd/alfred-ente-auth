import logging
import re
from pathlib import Path
from urllib.parse import urljoin

from src.constants import ENTE_CUSTOM_ICONS_URL, ENTE_ICONS_DATABASE_URL

logger = logging.getLogger(__name__)


def search_ente_custom_icons(name: str) -> str | None:
    """
    Searches Ente custom icons on GitHub for the provided name and returns the SVG content if found.
    """
    import requests
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


def _glyph_color(background_color: str) -> str:
    """Pick a glyph colour (white or black) that contrasts with the background."""
    color = background_color.lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    if len(color) != 6:
        return "#ffffff"
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#000000" if luminance > 128 else "#ffffff"


def add_icon_background(svg: str, background_color: str) -> str:
    """
    Wrap a monochrome SVG glyph in a rounded, brand-coloured background.

    The glyph is recoloured to contrast with the background so the icon stays
    visible on both light and dark Alfred themes, instead of disappearing when
    the brand colour happens to match the current theme.
    """
    rect = f'<rect width="24" height="24" rx="4" fill="{background_color}"/>'
    # Insert the background right after the top-level <svg ...> tag so it is
    # painted behind the (recoloured) glyph.
    return re.sub(r"(<svg[^>]*>)", rf"\1{rect}", svg, count=1)


def search_simple_icons(name: str) -> str | None:
    """Searches Simple Icons for the provided name and returns the SVG content if found."""
    from simplepycons import all_icons
    try:
        icon = all_icons[name]  # type: ignore
    except KeyError:
        logger.debug(f"Icon for '{name}' not found in Simple Icons.")
    else:
        background = icon.primary_color
        glyph = str(icon.customize_svg_as_str(fill=_glyph_color(background)))
        return add_icon_background(glyph, background)


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
