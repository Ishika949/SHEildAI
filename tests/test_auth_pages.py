import tempfile
import unittest
from pathlib import Path

import utils
from streamlit.testing.v1 import AppTest


class AuthPageTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_data_dir = utils.DATA_DIR
        utils.DATA_DIR = Path(self.temporary_directory.name)
        utils.initialize_data()

    def tearDown(self):
        utils.DATA_DIR = self.original_data_dir
        self.temporary_directory.cleanup()

    def open_page(self, page_name):
        app = AppTest.from_file(str(utils.BASE_DIR / "app.py"), default_timeout=15).run()
        app.switch_page(f"pages/{page_name}.py").run()
        return app

    def assert_page_image(self, app):
        images = app.get("imgs")
        self.assertEqual(len(images), 1)
        self.assertFalse(images[0].proto.imgs[0].caption)

    def test_signup_validates_confirmation_then_creates_and_signs_in(self):
        app = self.open_page("signup")
        app.text_input(key="signup_name").set_value("Demo Student")
        app.text_input(key="signup_email").set_value("demo@example.test")
        app.text_input(key="signup_password").set_value("demo-pass-123")
        app.text_input(key="signup_confirm_password").set_value("different-pass")
        app.button[0].click().run()
        self.assertIn("The passwords do not match.", [error.value for error in app.error])
        with utils._database() as connection:
            account_count = connection.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        self.assertEqual(account_count, 0)

        app.text_input(key="signup_confirm_password").set_value("demo-pass-123")
        app.button[0].click().run()
        self.assertEqual(app.session_state["current_user"]["email"], "demo@example.test")
        self.assertEqual([title.value for title in app.title], ["Dashboard"])

    def test_login_signs_in_and_opens_dashboard(self):
        utils.create_account("demo@example.test", "Demo Student", "", "demo-pass-123")
        app = self.open_page("login")
        app.text_input(key="login_email").set_value("demo@example.test")
        app.text_input(key="login_password").set_value("demo-pass-123")
        app.button[0].click().run()
        self.assertEqual(app.session_state["current_user"]["email"], "demo@example.test")
        self.assertEqual([title.value for title in app.title], ["Dashboard"])

    def test_login_rejects_an_incorrect_password(self):
        utils.create_account("demo@example.test", "Demo Student", "", "demo-pass-123")
        app = self.open_page("login")
        app.text_input(key="login_email").set_value("demo@example.test")
        app.text_input(key="login_password").set_value("incorrect-password")
        app.button[0].click().run()
        self.assertIn("Email or password is incorrect.", [error.value for error in app.error])
        self.assertNotIn("current_user", app.session_state)

    def test_account_pages_hide_storage_notice(self):
        for page_name in ("login", "signup"):
            app = self.open_page(page_name)
            self.assertNotIn(
                "Account details are stored in this app.",
                [caption.value for caption in app.caption],
            )

        account = utils.create_account(
            "profile@example.test",
            "Profile Tester",
            "",
            "test-password-123",
        )
        app = AppTest.from_file(str(utils.BASE_DIR / "app.py"), default_timeout=15).run()
        app.session_state["current_user"] = account
        app.switch_page("pages/profile.py").run()
        self.assertNotIn(
            "Account details are stored in this app.",
            [caption.value for caption in app.caption],
        )

    def test_login_and_signup_show_images_without_captions(self):
        for page_name in ("login", "signup"):
            app = self.open_page(page_name)
            self.assert_page_image(app)

    def test_content_pages_show_supplied_images(self):
        account = utils.create_account(
            "images@example.test",
            "Image Tester",
            "",
            "test-password-123",
        )
        app = AppTest.from_file(str(utils.BASE_DIR / "app.py"), default_timeout=15).run()
        self.assert_page_image(app)

        pages = ("dashboard", "safety_guide", "community_reports", "learning")
        for page_name in pages:
            page = AppTest.from_file(
                str(utils.BASE_DIR / "pages" / f"{page_name}.py"),
                default_timeout=15,
            )
            if page_name == "dashboard":
                page.session_state["current_user"] = account
            page.run()
            self.assertFalse(page.exception)
            self.assert_page_image(page)

    def test_signed_in_account_pages_render_supplied_images(self):
        account = utils.create_account(
            "signed-in@example.test",
            "Signed In Student",
            "",
            "test-password-123",
        )
        for page_name in ("login", "signup"):
            app = AppTest.from_file(
                str(utils.BASE_DIR / "pages" / f"{page_name}.py"),
                default_timeout=15,
            )
            app.session_state["current_user"] = account
            app.run()
            self.assertFalse(app.exception)
            self.assertTrue(
                any(
                    item.value.startswith("You are already signed in.")
                    for item in app.info
                )
            )
            self.assert_page_image(app)


if __name__ == "__main__":
    unittest.main()
