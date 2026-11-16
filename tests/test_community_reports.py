import tempfile
import unittest
from pathlib import Path

import utils
from streamlit.testing.v1 import AppTest


class CommunityReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_data_dir = utils.DATA_DIR
        utils.DATA_DIR = Path(self.temporary_directory.name)
        utils.initialize_data()

    def tearDown(self):
        utils.DATA_DIR = self.original_data_dir
        self.temporary_directory.cleanup()

    def test_report_form_saves_a_report(self):
        app = AppTest.from_file(
            str(utils.BASE_DIR / "pages" / "community_reports.py"),
            default_timeout=15,
        ).run()

        app.selectbox[0].set_value("Unsafe Area")
        app.text_input[0].set_value("Near the station")
        app.text_area[0].set_value("The path is poorly lit after dark.")
        app.button(key="submit_community_report").click().run()

        reports = utils.load_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["category"], "Unsafe Area")
        self.assertEqual(reports[0]["location"], "Near the station")
        self.assertEqual(
            reports[0]["description"],
            "The path is poorly lit after dark.",
        )
        self.assertIn("Report published.", [item.value for item in app.success])
        self.assertIn("Unsafe Area", [item.value for item in app.subheader])


if __name__ == "__main__":
    unittest.main()
