import hashlib
import uuid
from datetime import datetime

from src.models import AlfredOutput, AlfredOutputItem, TotpAccounts


def sanitize_service_name(service_name: str) -> str:
    return service_name.split("-")[0].strip().replace(" ", "").lower()


def str_to_bool(val: str | bool) -> bool:
    if isinstance(val, str):
        val = val.lower()
    if val in (True, "true", "1", 1):
        return True
    if val in (False, "false", "0", 0):
        return False
    msg = f"Cannot convert value to bool: {val!r}"
    raise ValueError(msg)


def calculate_time_remaining(time_step: int) -> int:
    """
    Calculate the seconds remaining until the next multiple of the given time step.
    """
    current_time = datetime.now().timestamp()
    return int(time_step - (current_time % time_step))


def is_subsequence(query: str, target: str) -> bool:
    """Check if all characters of query appear in target in the same order."""
    it = iter(target)
    return all(char in it for char in query)


def fuzzy_search_accounts(search_string: str, accounts: TotpAccounts) -> TotpAccounts:
    """
    Fuzzy search given TOTP accounts, matching on service name and username, and return the matched accounts.
    """
    matches: list[tuple[float, TotpAccount]] = []

    # Split the search_string by spaces for more granular search
    search_parts = search_string.lower().split()

    for account in accounts:
        # Lowercase the service_name and username for case-insensitive matching
        service_name_lower = account.service_name.lower()
        username_lower = account.username.lower()

        # Define match scores for prioritization
        score: float = 0
        all_parts_match_service = True
        all_parts_match_user = True

        for part in search_parts:
            # Check service name
            if part in service_name_lower:
                score += 3.0
            elif is_subsequence(part, service_name_lower):
                score += 1.0
            else:
                all_parts_match_service = False

            # Check username
            if part in username_lower:
                score += 2.0
            elif is_subsequence(part, username_lower):
                score += 0.5
            else:
                all_parts_match_user = False

        # Boost scores if all search parts match the service name or username
        if all_parts_match_service:
            score += 5.0
        if all_parts_match_user:
            score += 3.0

        if score > 0:
            matches.append((score, account))

    # Sort matches: pinned status first, then by search score, then local usage count, then tap_count, then last_used_at
    matches.sort(
        reverse=True,
        key=lambda x: (
            x[1].pinned,
            x[0],
            get_local_usage(x[1].service_name, x[1].username),
            x[1].tap_count,
            x[1].last_used_at,
        ),
    )

    return TotpAccounts([match[1] for match in matches])


def output_alfred_message(
    title: str, subtitle: str, variables: dict | None = None
) -> None:
    """Helper function to print a simple message in Alfred JSON format."""
    AlfredOutput(
        [AlfredOutputItem(title=title, subtitle=subtitle, variables=variables)]
    ).print_json()


def create_uuid_from_string(val: str) -> str:
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))


def get_usage_db_path() -> Path:
    import os
    from pathlib import Path
    workflow_data = os.getenv("alfred_workflow_data")
    if workflow_data:
        path = Path(workflow_data)
    else:
        path = Path("~/.cache/alfred-ente-auth").expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path / "local_usage.json"


def record_local_usage(service: str, username: str) -> None:
    import json
    path = get_usage_db_path()
    db = {}
    if path.exists():
        try:
            with open(path, "r") as f:
                db = json.load(f)
        except Exception:
            pass
    key = f"{service}:{username}"
    db[key] = db.get(key, 0) + 1
    try:
        with open(path, "w") as f:
            json.dump(db, f)
    except Exception:
        pass


def get_local_usage(service: str, username: str) -> int:
    import json
    path = get_usage_db_path()
    if not path.exists():
        return 0
    try:
        with open(path, "r") as f:
            db = json.load(f)
            return db.get(f"{service}:{username}", 0)
    except Exception:
        return 0
