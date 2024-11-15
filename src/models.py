import json
from dataclasses import asdict, dataclass


# https://www.alfredapp.com/help/workflows/inputs/script-filter/json
@dataclass
class AlfredOutputItemIcon:
    path: str = "icon.png"
    type: str | None = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AlfredOutputItem:
    title: str
    uid: str | None = None
    subtitle: str | None = None
    arg: str | list[str] | None = None
    icon: AlfredOutputItemIcon | None = None

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AlfredOutput:
    items: list[AlfredOutputItem]

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), separators=(",", ":"))

    def print_json(self):
        print(self.to_json())


@dataclass
class TotpAccount:
    username: str
    secret: str


class TotpAccounts(dict[str, TotpAccount]):
    def to_json(self) -> str:
        json_data = {k: asdict(v) for k, v in self.items()}
        return json.dumps(json_data, separators=(",", ":"))

    def from_json(self, json_str: str) -> "TotpAccounts":
        data = json.loads(json_str)
        return TotpAccounts({k: TotpAccount(**v) for k, v in data.items()})
