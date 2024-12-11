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
    def from_service(cls, service_name: str):
        """
        Creates an icon for the AlfredOutputItem based on the service name.

        Args:
            service_name (str): The name of the service.

        Returns:
            AlfredOutputItemIcon: An instance with the correct icon path.
        """
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

    def to_dict(self):
        return {
            k: v
            for k, v in {
                "items": [item.to_dict() for item in self.items],
                "rerun": self.rerun,
                "variables": self.variables,
            }.items()
            if v
        }

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


class TotpAccounts(list[TotpAccount]):
    """Class to represent a collection of TOTP accounts."""

    def to_json(self) -> str:
        json_data = [asdict(i) for i in self]
        return json.dumps(json_data, separators=(",", ":"))

    @classmethod
    def from_json(cls, json_str: str) -> "TotpAccounts":
        data = json.loads(json_str)
        return cls([TotpAccount(**i) for i in data])


@dataclass
class ImportResult:
    """Class to represent the result of a parsed Ente export."""

    count: int
    accounts: TotpAccounts
