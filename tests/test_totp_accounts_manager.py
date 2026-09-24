import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from src import models
from src.models import TotpAccount, TotpAccounts
from src.totp_accounts_manager import format_totp_result, parse_ente_export

SECRET = "JBSWY3DPEHPK3PXP"
SVG = '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'


def otpauth_uri(issuer: str, username: str, code_display: dict | None = None) -> str:
    query = {"secret": SECRET, "period": "30"}
    if code_display is not None:
        query["codeDisplay"] = json.dumps(code_display)
    return f"otpauth://totp/{issuer}:{username}?{urlencode(query)}"


class ParseEnteExportTests(unittest.TestCase):
    def parse(self, *lines: str) -> TotpAccounts:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ente_auth.txt"
            path.write_text("\n".join(lines))
            return parse_ente_export(path)

    def test_reads_selected_icon(self):
        [account] = self.parse(
            otpauth_uri(
                "Example",
                "person",
                {"iconSrc": "simpleIcon", "iconID": "github", "pinned": True},
            )
        )
        self.assertEqual(
            (account.icon_src, account.icon_id, account.pinned),
            ("simpleIcon", "github", True),
        )

    def test_missing_or_invalid_icon_fields(self):
        accounts = self.parse(
            otpauth_uri("Example", "none"),
            otpauth_uri("Example", "empty", {"iconSrc": "", "iconID": ""}),
            otpauth_uri("Example", "invalid", {"iconSrc": None, "iconID": 5}),
        )
        self.assertEqual([(a.icon_src, a.icon_id) for a in accounts], [("", "")] * 3)

    def test_trashed_accounts_are_skipped(self):
        self.assertEqual(
            self.parse(
                otpauth_uri("Example", "person", {"trashed": True, "iconID": "x"})
            ),
            [],
        )


class FormatTotpResultTests(unittest.TestCase):
    def test_uses_selected_icon_then_service_icon(self):
        selected = TotpAccount(
            "Example", "one", SECRET, icon_src="customIcon", icon_id="github"
        )
        missing = TotpAccount(
            "Example", "two", SECRET, icon_src="customIcon", icon_id="gitlab"
        )
        unselected = TotpAccount("Example", "three", SECRET)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / f"{selected.selected_icon_name}.svg").write_text(SVG)
            (folder / "example.svg").write_text(SVG)
            with patch.object(models, "ICONS_FOLDER", folder):
                result = format_totp_result(
                    TotpAccounts([selected, missing, unselected])
                )
        self.assertEqual(
            [Path(item.icon.path).name for item in result.items],
            [f"{selected.selected_icon_name}.svg", "example.svg", "example.svg"],
        )


if __name__ == "__main__":
    unittest.main()
