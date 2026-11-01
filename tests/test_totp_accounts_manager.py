import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from src import models
from src.models import TotpAccount, TotpAccounts
from src.totp_accounts_manager import format_totp_result, parse_ente_export
from src.utils import fuzzy_search_accounts

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
    def test_distinct_username_is_still_displayed(self):
        accounts = TotpAccounts([TotpAccount("Porkbun", "person", SECRET)])
        with patch.dict(
            os.environ,
            {"USERNAME_IN_TITLE": "True", "USERNAME_IN_SUBTITLE": "True"},
        ):
            [item] = format_totp_result(accounts).items
        self.assertEqual(item.title, "Porkbun - person")
        self.assertTrue(item.subtitle.endswith(" - person"))

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


class IssuerParsingTests(unittest.TestCase):
    def parse(self, label, issuer=None):
        params = {"secret": "JBSWY3DPEHPK3PXP", "period": "30"}
        if issuer is not None:
            params["issuer"] = issuer
        uri = f"otpauth://totp/{label}?{urlencode(params)}"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ente_auth.txt"
            path.write_text(uri)
            return parse_ente_export(path)

    def test_matching_label_and_issuer_keep_username_but_hide_duplicate_text(self):
        for label in ["Porkbun", "pOrKbUn"]:
            with self.subTest(label=label):
                accounts = self.parse(label, "Porkbun")
                with patch.dict(
                    os.environ,
                    {"USERNAME_IN_TITLE": "True", "USERNAME_IN_SUBTITLE": "True"},
                ):
                    [item] = format_totp_result(accounts).items
                self.assertEqual(item.title, "Porkbun")
                self.assertNotIn("porkbun", item.subtitle.casefold())
                self.assertEqual(accounts[0].username, label)
                self.assertEqual(item.variables["selected_username"], label)

    def test_duplicate_username_has_same_search_score_as_no_username(self):
        for label in ["Porkbun", "pOrKbUn"]:
            duplicate = self.parse(label, "Porkbun")[0]
            no_username = self.parse("Porkbun")[0]
            for ordered in [[no_username, duplicate], [duplicate, no_username]]:
                with self.subTest(label=label, first_username=ordered[0].username):
                    with patch("src.utils.get_local_usage", return_value=0):
                        results = fuzzy_search_accounts("pork", TotpAccounts(ordered))
                    self.assertEqual(results, ordered)

    def test_issuer_only_service_survives_storage_and_is_searchable(self):
        accounts = self.parse("test%40example.com", "Porkbun")
        stored = TotpAccounts.from_json(accounts.to_json())
        with patch("src.utils.get_local_usage", return_value=0):
            results = fuzzy_search_accounts("pork", stored)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].service_name, "Porkbun")
        self.assertEqual(results[0].username, "test@example.com")

    def test_issuer_and_label_prefix_preserve_username(self):
        account = self.parse("Porkbun:test%40example.com", "Porkbun")[0]
        self.assertEqual(account.service_name, "Porkbun")
        self.assertEqual(account.username, "test@example.com")

    def test_label_prefix_still_works_without_issuer(self):
        account = self.parse("Porkbun:test%40example.com")[0]
        self.assertEqual(account.service_name, "Porkbun")
        self.assertEqual(account.username, "test@example.com")

    def test_plain_label_still_works_without_issuer(self):
        account = self.parse("Porkbun")[0]
        self.assertEqual(account.service_name, "Porkbun")
        self.assertEqual(account.username, "")

    def test_blank_issuer_falls_back_to_label(self):
        account = self.parse("Porkbun:test%40example.com", " ")[0]
        self.assertEqual(account.service_name, "Porkbun")
        self.assertEqual(account.username, "test@example.com")


if __name__ == "__main__":
    unittest.main()
