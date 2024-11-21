from datetime import datetime

from src.models import AlfredOutput, AlfredOutputItem, TotpAccounts


def str_to_bool(val):
    if isinstance(val, str):
        val = val.lower()
    if val in (True, "true", "1", 1):
        return True
    if val in (False, "false", "0", 0):
        return False
    msg = f"Cannot convert value to bool: {val!r}"
    raise ValueError(msg)


def calculate_time_remaining(time_step=30):
    # Calculate the time remaining until the next TOTP period.

    current_time = datetime.now().timestamp()
    return int(time_step - (current_time % time_step))


def fuzzy_search_accounts(search_string: str, values: TotpAccounts) -> TotpAccounts:
    matches: list[tuple[float, str]] = []

    # Split the search_string by spaces for more granular search
    search_parts = search_string.lower().split()

    for service_name, service_info in values.items():
        # Lowercase the service_name and username for case-insensitive matching
        service_name_lower = service_name.lower()
        username_lower = service_info.username.lower()

        # Define match scores for prioritization
        score = 0
        if all(part in service_name_lower for part in search_parts):
            score += 3  # Full match in service name
        if all(part in username_lower for part in search_parts):
            score += 2  # Full match in username
        if any(part in service_name_lower for part in search_parts):
            score += 1  # Partial match in service name
        if any(part in username_lower for part in search_parts):
            score += 0.5  # Partial match in username

        if score > 0:
            matches.append((float(score), service_name))

    # Sort matches by score in descending order
    matches.sort(reverse=True, key=lambda x: x[0])

    matched_accounts = TotpAccounts(
        {k: v for k, v in values.items() if k in [match[1] for match in matches]}
    )

    return matched_accounts


def output_alfred_message(title: str, subtitle: str, variables: dict | None = None):
    AlfredOutput(
        [AlfredOutputItem(title=title, subtitle=subtitle, variables=variables)]
    ).print_json()
