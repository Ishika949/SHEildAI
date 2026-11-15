import tempfile
import unittest
from pathlib import Path

import utils
from streamlit.testing.v1 import AppTest


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_data_dir = utils.DATA_DIR
        utils.DATA_DIR = Path(self.temporary_directory.name)
        utils.initialize_data()
        self.account = utils.create_account(
            "sos@example.test",
            "SOS Tester",
            "",
            "test-password-123",
        )

    def tearDown(self):
        utils.DATA_DIR = self.original_data_dir
        self.temporary_directory.cleanup()

    def test_sos_button_plays_local_audio_and_can_stop_it(self):
        app = AppTest.from_file(str(utils.BASE_DIR / "app.py"), default_timeout=15).run()
        app.session_state["current_user"] = self.account
        app.switch_page("pages/dashboard.py").run()
        self.assertNotIn("SMS preview", [header.value for header in app.subheader])

        app.button(key="play_sos_sound").click().run()

        self.assertEqual(len(app.get("audio")), 1)
        self.assertEqual(len(app.get("video")), 0)
        self.assertIn("SMS preview", [header.value for header in app.subheader])
        self.assertEqual(
            app.session_state["sos_sound_requested"],
            True,
        )

        app.button(key="stop_sos_sound").click().run()

        self.assertEqual(len(app.get("audio")), 0)
        self.assertEqual(app.session_state["sos_sound_requested"], False)
        self.assertNotIn("SMS preview", [header.value for header in app.subheader])


if __name__ == "__main__":
    unittest.main()
