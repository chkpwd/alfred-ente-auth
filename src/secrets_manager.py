import json
import logging
import os
from datetime import datetime, timedelta
from urllib.parse import parse_qs, unquote, urlparse

import pyotp
from attrs.converters import to_bool

from src.models import (
    AlfredOutput,
    AlfredOutputItem,
    AlfredOutputItemIcon,
    TotpAccount,
    TotpAccounts,
)

logger = logging.getLogger(__name__)

USERNAME_IN_TITLE = to_bool(os.getenv("username_in_title", "False"))
USERNAME_IN_SUBTITLE = to_bool(os.getenv("username_in_subtitle", "False"))


def parse_secrets(file_path: str) -> TotpAccounts:
    accounts = TotpAccounts()

    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                line = line.replace("=sha1", "=SHA1")
                if "codeDisplay" in line:
                    line = line.split("codeDisplay")[0][:-1]

                # Manually parse the secrets without pyotp
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


def format_secrets_data(secrets: TotpAccounts) -> AlfredOutput:
    """Format the secrets data."""
    try:
        items: list[AlfredOutputItem] = []

        for service_name, service_data in secrets.items():
            current_totp = pyotp.TOTP(service_data.secret).now()
            next_time = datetime.now() + timedelta(seconds=30)
            next_totp = pyotp.TOTP(service_data.secret).at(next_time)

            service_name = (
                f"{service_name} - {service_data.username}"
                if service_data.username and USERNAME_IN_TITLE
                else service_name
            )
            subtitle = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}" + (
                f" - {service_data.username}"
                if service_data.username and USERNAME_IN_SUBTITLE
                else ""
            )

            items.append(
                AlfredOutputItem(
                    title=service_name,
                    subtitle=subtitle,
                    arg=current_totp,
                    icon=AlfredOutputItemIcon(path="../icon.png"),
                )
            )

        if items:
            output = AlfredOutput(items)
        else:
            output = AlfredOutput(
                [AlfredOutputItem(title="No matching services found.")]
            )

        logger.debug(json.dumps(output, indent=4))

        return output

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return AlfredOutput(
            [
                AlfredOutputItem(
                    title="Unexpected error in format_secrets_data function."
                )
            ]
        )
