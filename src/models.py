import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

from src.constants import ICONS_FOLDER


# https://www.alfredapp.com/help/workflows/inputs/script-filter/json
@dataclass
class AlfredOutputItemIcon:
    """
    Class to represent a custom icon for an AlfredOutputItem object.

    See https://www.alfredapp.com/help/workflows/inputs/script-filter/json
    """

    path: str = "icon.png"
    type: str | None = None

    @classmethod
    def from_service(cls, service_name: str, selected_icon_name: str = ""):
        """
        Creates an icon for the AlfredOutputItem, preferring the icon selected in Ente.

        Args:
            service_name (str): The name of the service.
            selected_icon_name (str): File stem of the icon selected in Ente, if any.

        Returns:
            AlfredOutputItemIcon: An instance with the correct icon path.
        """
        if selected_icon_name:
            selected_path = ICONS_FOLDER / f"{selected_icon_name}.svg"
            if selected_path.exists():
                return cls(path=str(selected_path))
        icon_path = ICONS_FOLDER / f"{service_name}.svg"
        if icon_path.exists():
            return cls(path=str(icon_path))
        return cls()

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AlfredOutputItem:
    """
    Class to represent an item in an AlfredOutput object.

    See https://www.alfredapp.com/help/workflows/inputs/script-filter/json
    """

    title: str
    uid: str | None = None
    subtitle: str | None = None
    match: str | None = None
    arg: str | list[str] | None = None
    icon: AlfredOutputItemIcon | None = None
    variables: dict[str, Any] | None = None
    uid: str | None = None

    def __post_init__(self):
        # Automatically fetch an icon based on the title if no icon is provided
        if self.icon is None:
            self.icon = AlfredOutputItemIcon.from_service(self.title)

    def to_dict(self):
        result = {k: v for k, v in asdict(self).items() if v is not None}
        if self.icon is not None:
            result["icon"] = self.icon.to_dict()
        return result


@dataclass
class AlfredOutput:
    """
    Class to represent structured output to an Alfred session.

    See https://www.alfredapp.com/help/workflows/inputs/script-filter/json
    """

    items: list[AlfredOutputItem]
    rerun: float | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    skipknowledge: bool = True

    def to_dict(self):
        result = {
            k: v
            for k, v in {
                "items": [item.to_dict() for item in self.items],
                "rerun": self.rerun,
                "variables": self.variables,
            }.items()
            if v
        }
        if self.skipknowledge:
            result["skipknowledge"] = True
        return result

    def to_json(self):
        return json.dumps(self.to_dict(), separators=(",", ":"))

    def print_json(self):
        sys.stdout.write(self.to_json())


@dataclass
class TotpAccount:
    """Class to represent a TOTP account imported from Ente or stored locally."""

    service_name: str
    username: str
    secret: str
    period: int = 30
    pinned: bool = False
    last_used_at: int = 0
    tap_count: int = 0
    icon_src: str = ""
    icon_id: str = ""

    @property
    def selected_icon_name(self) -> str:
        """
        File stem for the icon selected in Ente, or an empty string if none was selected.

        Ente only uses a selected icon when both iconSrc and iconID are set, and looks it up by
        iconID alone. The ID is hashed because icon titles may contain characters such as "/".
        """
        if not (self.icon_src and self.icon_id):
            return ""
        icon_key = self.icon_id.replace(" ", "").lower()
        return "selected-" + hashlib.sha256(icon_key.encode("utf-8")).hexdigest()[:16]


class TotpAccounts(list[TotpAccount]):
    """Class to represent a collection of TOTP accounts."""

    def to_json(self) -> str:
        json_data = [asdict(i) for i in self]
        return json.dumps(json_data, separators=(",", ":"))

    @classmethod
    def from_json(cls, json_str: str) -> "TotpAccounts":
        data = json.loads(json_str)
        try:
            if isinstance(data, dict):
                return cls(_accounts_from_older_format(data))
            return cls([TotpAccount(**i) for i in data])
        except (KeyError, TypeError, ValueError) as e:
            raise ValueError(
                "Stored accounts use an unrecognized format. Run 'ente import' to refresh them."
            ) from e


def _accounts_from_older_format(data: dict) -> list[TotpAccount]:
    """Reads accounts saved by releases before v2.2.3, which grouped them by service name."""
    accounts = []
    for service_name, entries in data.items():
        if isinstance(entries, dict):
            # v2.0.0 to v2.2.2: {service: {"username": ..., "secret": ..., "period": ...}}
            accounts.append(TotpAccount(service_name, **entries))
        else:
            # Before v2.0.0: {service: [[username, secret], ...]}
            accounts.extend(TotpAccount(service_name, *entry) for entry in entries)
    return accounts


@dataclass
class ImportResult:
    """Class to represent the result of a parsed Ente export."""

    count: int
    accounts: TotpAccounts
