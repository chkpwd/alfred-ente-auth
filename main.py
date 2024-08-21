import json
import pathlib
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.parse import parse_qs, unquote, urlparse

import click
import pyotp

DB_FILE = pathlib.Path.home() / ".local/share/ente-totp/db.json"


@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("file", type=click.Path(exists=True))
def import_file(file):
    secret_dict = defaultdict(list)
    for service_name, username, secret in parse_secrets(file):
        secret_dict[service_name].append((username, secret))
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DB_FILE.open("w") as json_file:
        json.dump(secret_dict, json_file, indent=2)
    print("Database created.")


def parse_secrets(file_path="secrets.txt"):
    secrets_list = []

    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                parsed_url = urlparse(line)
                if parsed_url.scheme == "otpauth":
                    path_items = unquote(parsed_url.path).strip("/").split(":", 1)
                    if len(path_items) == 2:
                        service_name, username = path_items[0], path_items[1]
                    else:
                        service_name, username = path_items[0].strip(":"), ""
                    query_params = parse_qs(parsed_url.query)
                    secret = query_params.get("secret", [None])[0]
                    if secret:
                        secrets_list.append((service_name, username, secret))

    return secrets_list


def format_data(service_name, username, current_totp, next_totp, output_type):
    """Format the data based on the output type."""
    if username:
        subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp} - {username}"
    else:
        subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}"

    if output_type == "alfred":
        return {
            "title": service_name,
            "subtitle": subset,
            "arg": current_totp,
            "icon": {"path": "./icon.png"},
        }

    elif output_type == "json":
        return {
            "service_name": service_name,
            "current_totp": current_totp,
            "next_totp": next_totp,
            "service_data": subset,
        }

    elif output_type == "print":
        print(f"Service: {service_name}")
        print(f"Current TOTP: {current_totp}")
        print(f"Next TOTP: {next_totp}")
        if username:
            print(f"Username: {username}")
        print()

    return None


@cli.command("get")
@click.argument("secret_id")
@click.option(
    "-o",
    "output_format",
    type=click.Choice(["json", "alfred", "print"]),
    default="print",
    help="Data output format",
)
def generate_totp(secret_id, output_format):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
        items = []  # Collect all items in this list
        for service_name, service_data in data.items():
            if secret_id.lower() in service_name.lower():
                for username, secret in service_data:
                    current_totp = pyotp.TOTP(secret).now()
                    next_time = datetime.now() + timedelta(seconds=30)
                    next_totp = pyotp.TOTP(secret).at(next_time)
                    formatted_data = format_data(
                        service_name, username, current_totp, next_totp, output_format
                    )
                    if formatted_data:
                        items.append(formatted_data)

        if output_format == "alfred":
            print(json.dumps({"items": items}, indent=4))
        elif output_format == "json":
            print(json.dumps({"items": items}, indent=4))
        elif output_format == "print" and not items:
            print("No matching services found.")

    except Exception as e:
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()
