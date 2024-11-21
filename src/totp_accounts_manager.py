import logging
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, unquote, urlparse

import pyotp

from src.icon_downloader import get_icon_path
from src.models import (
    AlfredOutput,
    AlfredOutputItem,
    AlfredOutputItemIcon,
    TotpAccount,
    TotpAccounts,
)
from src.utils import calculate_time_remaining, str_to_bool

logger = logging.getLogger(__name__)


USERNAME_IN_TITLE = str_to_bool(os.getenv("USERNAME_IN_TITLE", "False"))
USERNAME_IN_SUBTITLE = str_to_bool(os.getenv("USERNAME_IN_SUBTITLE", "False"))


def parse_ente_export(file_path: str) -> TotpAccounts:
    accounts = TotpAccounts()

    with open(file_path, "r") as ente_export_file:
        for line in ente_export_file:
            line = line.strip()
            if line:
                line = line.replace("=sha1", "=SHA1")
                if "codeDisplay" in line:
                    line = line.split("codeDisplay")[0][:-1]

                # Manually parse the otpauth URI without pyotp
                # https://github.com/pyauth/pyotp/issues/171
                parsed_uri = urlparse(line)
                if parsed_uri.scheme == "otpauth":
                    path_items = unquote(parsed_uri.path).strip("/").split(":", 1)
                    if len(path_items) == 2:
                        service_name, username = path_items[0], path_items[1]
                    else:
                        service_name, username = path_items[0].strip(":"), ""

                    query_params = parse_qs(parsed_uri.query)
                    secret = query_params.get("secret", [None])[0]

                    if not secret:
                        raise ValueError(
                            f"Unable to parse 'secret' parameter in: {line}"
                        )

                    accounts[service_name] = TotpAccount(username, secret)
    return accounts


def format_totp_result(accounts: TotpAccounts) -> AlfredOutput:
    """Format TOTP accounts for Alfred."""
    result = AlfredOutput([])
    try:
        for service_name, service_data in accounts.items():
            # Generate TOTP
            totp = pyotp.TOTP(service_data.secret)
            current_totp = totp.now()
            next_totp = totp.at(datetime.now() + timedelta(seconds=30))

            # Calculate remaining time using the utility
            time_remaining = calculate_time_remaining()

            # Sanitize service name for display and icons
            sanitized_service_name = service_name.strip()

            # Update title and subtitle
            title = (
                f"{sanitized_service_name} - {service_data.username}"
                if service_data.username and USERNAME_IN_TITLE
                else sanitized_service_name
            )
            subtitle = (
                f"Current TOTP: {current_totp} | Next TOTP: {next_totp}, {time_remaining} seconds left"
                + (
                    f" - {service_data.username}"
                    if service_data.username and USERNAME_IN_SUBTITLE
                    else ""
                )
            )

            # Add icon dynamically for each item
            icon_path = get_icon_path(sanitized_service_name)

            result.items.append(
                AlfredOutputItem(
                    title=title,
                    subtitle=subtitle,
                    arg=current_totp,
                    icon=AlfredOutputItemIcon(path=icon_path),  # Add the icon here
                )
            )

        if not result.items:
            result.items = [AlfredOutputItem(title="No matching services found.")]

    except Exception as e:
        logging.exception(f"Error: {str(e)}")
        result.items = [
            AlfredOutputItem(title="Unexpected error in format_totp_result function.")
        ]

    return result
