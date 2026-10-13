import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urljoin

import requests

from src import icon_downloader
from src.constants import (
    ENTE_CUSTOM_ICONS_URL,
    ENTE_ICONS_DATABASE_URL,
    ENTE_SIMPLE_ICONS_URL,
)
from src.icon_downloader import (
    ICON_DOWNLOAD_ERRORS,
    download_account_icon,
    record_download_error,
    simple_icon_slug,
)
from src.models import TotpAccount

SECRET = "JBSWY3DPEHPK3PXP"
SVG = (
    '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M0 0"/></svg>'
)
ROUTES = {
    ENTE_ICONS_DATABASE_URL: json.dumps(
        {
            "icons": [
                {"title": "Example Bank", "slug": "example_bank", "altNames": ["EB"]}
            ]
        }
    ),
    urljoin(ENTE_CUSTOM_ICONS_URL, "example_bank.svg"): SVG,
    urljoin(ENTE_SIMPLE_ICONS_URL, "_data/simple-icons.json"): json.dumps(
        [{"title": "Aer Lingus", "hex": "006272"}]
    ),
    urljoin(ENTE_SIMPLE_ICONS_URL, "icons/aerlingus.svg"): SVG,
}


def response(url: str, status: int, text: str) -> requests.Response:
    resp = requests.Response()
    resp.url, resp.status_code, resp._content = url, status, text.encode()
    return resp


class FakeSession:
    """Serves ROUTES and records requested URLs; other URLs return 404."""

    def __init__(self, error: Exception | None = None):
        self.error, self.requested = error, []

    def get(self, url, timeout):
        self.requested.append(url)
        if self.error:
            raise self.error
        if url in ROUTES:
            return response(url, 200, ROUTES[url])
        return response(url, 404, "")


def account(service="Example", icon_id=""):
    return TotpAccount(
        service,
        "person",
        SECRET,
        icon_src="customIcon" if icon_id else "",
        icon_id=icon_id,
    )


class IconDownloaderTestCase(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, logging.NOTSET)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        icon_downloader.load_icon_database.cache_clear()
        ICON_DOWNLOAD_ERRORS.clear()
        self.use_session(FakeSession())

    def use_session(self, session: FakeSession) -> None:
        self.session = session
        patcher = patch("src.http_client.get_icon_session", return_value=session)
        patcher.start()
        self.addCleanup(patcher.stop)


class SimpleIconSlugTests(unittest.TestCase):
    def test_matches_ente_file_names(self):
        for title, slug in {
            ".NET": "dotnet",
            "1.1.1.1": "1dot1dot1dot1",
            "1&1": "1and1",
            "A-Frame": "aframe",
            "AlloCiné": "allocine",
            "Notion+": "notionplus",
            "Aer Lingus": "aerlingus",
        }.items():
            with self.subTest(title=title):
                self.assertEqual(simple_icon_slug(title), slug)


class DownloadAccountIconTests(IconDownloaderTestCase):
    def selected_icon(self, acct: TotpAccount) -> str:
        return (self.folder / f"{acct.selected_icon_name}.svg").read_text()

    def test_selected_ente_custom_icon(self):
        for icon_id in ["examplebank", "eb"]:
            acct = account(icon_id=icon_id)
            download_account_icon(acct, self.folder)
            self.assertEqual(self.selected_icon(acct), SVG)

    def test_selected_bundled_simple_icon(self):
        acct = account(icon_id="1.1.1.1")
        download_account_icon(acct, self.folder)
        self.assertIn("<svg", self.selected_icon(acct))

    def test_selected_simple_icon_only_in_ente_revision(self):
        acct = account(icon_id="aerlingus")
        download_account_icon(acct, self.folder)
        self.assertEqual(
            self.selected_icon(acct), SVG.replace("<svg ", '<svg fill="#006272" ', 1)
        )

    def test_same_service_with_different_selections(self):
        first, second = account(icon_id="examplebank"), account(icon_id="aerlingus")
        download_account_icon(first, self.folder)
        download_account_icon(second, self.folder)
        self.assertNotEqual(first.selected_icon_name, second.selected_icon_name)
        self.assertEqual(len(list(self.folder.glob("selected-*.svg"))), 2)

    def test_unresolved_selection_uses_service_name(self):
        download_account_icon(
            account("Example Bank - Work", icon_id="missing"), self.folder
        )
        self.assertEqual([p.name for p in self.folder.iterdir()], ["examplebank.svg"])

    def test_no_selection_uses_service_name(self):
        download_account_icon(account("Example Bank"), self.folder)
        self.assertEqual([p.name for p in self.folder.iterdir()], ["examplebank.svg"])

    def test_icon_databases_are_downloaded_once(self):
        for _ in range(3):
            download_account_icon(account(icon_id="missing"), self.folder)
        self.assertEqual(self.session.requested.count(ENTE_ICONS_DATABASE_URL), 1)

    def test_existing_icon_is_kept_when_download_fails(self):
        self.use_session(FakeSession(error=requests.exceptions.ConnectTimeout()))
        acct = account(icon_id="examplebank")
        path = self.folder / f"{acct.selected_icon_name}.svg"
        path.write_text("previous")
        download_account_icon(acct, self.folder)
        self.assertEqual(path.read_text(), "previous")
        self.assertEqual(ICON_DOWNLOAD_ERRORS, ["Icon downloads timed out."])


class RecordDownloadErrorTests(IconDownloaderTestCase):
    def test_describes_errors_once(self):
        http_error = requests.exceptions.HTTPError(
            response=response("https://example.test", 503, "")
        )
        for e in [
            requests.exceptions.SSLError(),
            requests.exceptions.SSLError(),
            requests.exceptions.ProxyError(),
            requests.exceptions.ReadTimeout(),
            http_error,
            requests.exceptions.ConnectionError(),
            requests.exceptions.InvalidJSONError(),
        ]:
            record_download_error(e)
        self.assertEqual(
            ICON_DOWNLOAD_ERRORS,
            [
                "HTTPS certificate error while downloading icons.",
                "Proxy connection failed while downloading icons.",
                "Icon downloads timed out.",
                "Icon server returned HTTP 503.",
                "Could not connect to the icon server.",
                "Icon server returned invalid data.",
            ],
        )


if __name__ == "__main__":
    unittest.main()
