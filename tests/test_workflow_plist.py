import plistlib
import unittest
from pathlib import Path

INFO_PLIST = Path(__file__).parent.parent / "info.plist"


class WorkflowPlistTests(unittest.TestCase):
    def test_import_keyword_runs_the_import_script(self):
        with open(INFO_PLIST, "rb") as f:
            plist = plistlib.load(f)
        [trigger] = [
            o for o in plist["objects"] if o["config"].get("keyword") == "ente import"
        ]
        self.assertEqual(trigger["type"], "alfred.workflow.input.scriptfilter")
        self.assertIn("main.py import", trigger["config"]["script"])


if __name__ == "__main__":
    unittest.main()
