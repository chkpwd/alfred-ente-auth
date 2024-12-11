import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import pyotp

from src.models import (
    AlfredOutput,
    AlfredOutputItem,
    AlfredOutputItemIcon,
    TotpAccount,
    TotpAccounts,
)
from src.utils import (
    calculate_time_remaining,
    create_uuid_from_string,
    sanitize_service_name,
    str_to_bool,
)

logger = logging.getLogger(__name__)


def parse_ente_export(file_path: Path) -> TotpAccounts:
    """Parses an Ente export file of otpauth URIs and returns a TotpAccounts object."""
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
                    period = query_params.get("period", [None])[0]

                    if not secret:
                        raise KeyError(f"Unable to parse 'secret' parameter in: {line}")

                    if not period or period == "null":
                        logger.warning(
                            f"Unable to parse 'period' parameter for '{service_name} - {username}'. Will use default of 30 seconds."
                        )
                        accounts.append(TotpAccount(service_name, username, secret))
                    else:
                        try:
                            period = int(period)
                        except ValueError:
                            logger.warning(
                                f"Value of 'period' parameter ('{period}') for '{service_name} - {username}' could not be cast to int. Will use default of 30 seconds."
                            )
                            period = 30

                        accounts.append(TotpAccount(service_name, username, secret, period))

    return accounts


def format_totp_result(accounts: TotpAccounts) -> AlfredOutput:
    """Transforms a TotpAccounts object into an AlfredOutput object."""
    result = AlfredOutput([], rerun=1)

    username_in_title = str_to_bool(os.getenv("USERNAME_IN_TITLE", "False"))
    username_in_subtitle = str_to_bool(os.getenv("USERNAME_IN_SUBTITLE", "False"))

    try:
        for account in accounts:
            # Generate TOTP
            totp = pyotp.TOTP(account.secret)
            current_totp = totp.now()
            next_totp = totp.at(datetime.now() + timedelta(seconds=account.period))

            time_remaining = calculate_time_remaining(account.period)

            sanitized_service_name = sanitize_service_name(account.service_name)

            # Conditionally add username to title and subtitle
            title = (
                f"{account.service_name} - {account.username}"
                if account.username and username_in_title
                else account.service_name
            )
            subtitle = (
                f"Current TOTP: {current_totp} | Next TOTP: {next_totp}, {time_remaining} seconds left"
                + (
                    f" - {account.username}"
                    if account.username and username_in_subtitle
                    else ""
                )
            )

            result.items.append(
                AlfredOutputItem(
                    title=title,
                    subtitle=subtitle,
                    arg=current_totp,
                    match=account.service_name,
                    icon=AlfredOutputItemIcon.from_service(sanitized_service_name),
                    uid=create_uuid_from_string(account.service_name + account.username),
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
