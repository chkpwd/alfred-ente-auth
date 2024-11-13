import os

from urllib.parse import parse_qs, unquote, urlparse


USERNAME_IN_TITLE = os.getenv("username_in_title", "false").lower() in (
    "true",
    "1",
    "t",
    "y",
    "yes",
)
USERNAME_IN_SUBTITLE = os.getenv("username_in_subtitle", "false").lower() in (
    "true",
    "1",
    "t",
    "y",
    "yes",
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

                    if secret:
                        secrets_list.append((service_name, username, secret))
                    else:
                        print(f"Unable to parse secret in: {line}")

                # parsed_uri = pyotp.parse_uri(line)
                # if parsed_uri:
                #     service_name = parsed_uri.issuer or parsed_uri.name
                #     username = parsed_uri.name
                #     secret = parsed_uri.secret
                #     if secret:
                #         secrets_list.append((service_name, username, secret))
                #     else:
                #         print(f"Unable to parse secret in: {line}")
                # else:
                #     print(f"Unable to parse the line: {line}")
    return secrets_list

def format_data(service_name, username, current_totp, next_totp):
    """Format the TOTP data based on the output type."""
    subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}" + (
        f" - {username}" if username and USERNAME_IN_SUBTITLE else ""
    )
    service_name = (
        f"{service_name} - {username}"
        if username and USERNAME_IN_TITLE
        else service_name
    )

    return {
        "title": service_name,
        "subtitle": subset,
        "arg": current_totp,
        "icon": {"path": "../icon.png"},
    }
