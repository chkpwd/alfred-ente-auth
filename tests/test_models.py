import json
import unittest

from src.models import TotpAccount, TotpAccounts

SECRET = "JBSWY3DPEHPK3PXP"


class TotpAccountsFromJsonTests(unittest.TestCase):
    def test_current_format_round_trip(self):
        accounts = TotpAccounts(
            [
                TotpAccount("Example", "person", SECRET, period=60, pinned=True),
                TotpAccount(
                    "Example", "other", SECRET, icon_src="simpleIcon", icon_id="github"
                ),
            ]
        )
        self.assertEqual(TotpAccounts.from_json(accounts.to_json()), accounts)

    def test_current_format_without_icon_fields(self):
        data = [
            {
                "service_name": "Example",
                "username": "person",
                "secret": SECRET,
                "period": 30,
            }
        ]
        [account] = TotpAccounts.from_json(json.dumps(data))
        self.assertEqual((account.icon_src, account.icon_id), ("", ""))

    def test_format_before_v2_0_0(self):
        data = {"Example": [["person", SECRET], ["other", SECRET]]}
        self.assertEqual(
            TotpAccounts.from_json(json.dumps(data)),
            [
                TotpAccount("Example", "person", SECRET),
                TotpAccount("Example", "other", SECRET),
            ],
        )

    def test_format_v2_0_0_to_v2_2_2(self):
        data = {
            "Example": {"username": "person", "secret": SECRET, "period": 60},
            "Other": {"username": "", "secret": SECRET},
        }
        self.assertEqual(
            TotpAccounts.from_json(json.dumps(data)),
            [
                TotpAccount("Example", "person", SECRET, period=60),
                TotpAccount("Other", "", SECRET),
            ],
        )

    def test_unrecognized_data_asks_for_import(self):
        for data in [
            json.dumps("text"),
            json.dumps([{"service_name": "Example", "username": "person"}]),
            json.dumps(["Example"]),
            json.dumps({"Example": [["person"]]}),
            json.dumps({"Example": {"username": "person"}}),
            json.dumps({"Example": "person"}),
        ]:
            with (
                self.subTest(data=data),
                self.assertRaisesRegex(ValueError, "ente import"),
            ):
                TotpAccounts.from_json(data)


class SelectedIconNameTests(unittest.TestCase):
    def test_requires_icon_source_and_id(self):
        self.assertEqual(TotpAccount("Example", "", SECRET).selected_icon_name, "")
        self.assertEqual(
            TotpAccount("Example", "", SECRET, icon_id="github").selected_icon_name, ""
        )
        self.assertTrue(
            TotpAccount(
                "Example", "", SECRET, icon_src="customIcon", icon_id="github"
            ).selected_icon_name.startswith("selected-")
        )

    def test_depends_only_on_normalized_icon_id(self):
        def name(icon_src, icon_id):
            return TotpAccount(
                "Example", "", SECRET, icon_src=icon_src, icon_id=icon_id
            ).selected_icon_name

        self.assertEqual(name("simpleIcon", "Git Hub"), name("customIcon", "github"))
        self.assertNotEqual(name("simpleIcon", "github"), name("simpleIcon", "gitlab"))

    def test_is_safe_as_a_file_name(self):
        name = TotpAccount(
            "Example", "", SECRET, icon_src="simpleIcon", icon_id="/e/"
        ).selected_icon_name
        self.assertRegex(name, r"^selected-[0-9a-f]{16}$")


if __name__ == "__main__":
    unittest.main()
