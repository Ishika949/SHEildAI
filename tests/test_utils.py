import tempfile
import csv
import unittest
from pathlib import Path

import utils


class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.original_data_dir = utils.DATA_DIR
        utils.DATA_DIR = Path(self.temporary_directory.name)
        utils.initialize_data()

    def tearDown(self):
        utils.DATA_DIR = self.original_data_dir
        self.temporary_directory.cleanup()

    def test_account_password_is_hashed_and_verifiable(self):
        account = utils.create_account(
            "Person@example.test",
            "Test Student",
            "",
            "classroom-password",
        )
        self.assertIsNotNone(account)
        self.assertEqual(account["email"], "person@example.test")
        self.assertEqual(
            utils.authenticate("PERSON@example.test", "classroom-password"),
            account,
        )
        self.assertIsNone(utils.authenticate("person@example.test", "wrong-password"))
        with (utils.DATA_DIR / "accounts.csv").open(
            newline="",
            encoding="utf-8",
        ) as file:
            stored = next(csv.DictReader(file))
        self.assertNotEqual(stored["password_hash"], "classroom-password")

    def test_duplicate_accounts_are_rejected(self):
        utils.create_account("person@example.test", "Test Student", "", "classroom-password")
        duplicate = utils.create_account(
            "PERSON@example.test",
            "Another Student",
            "",
            "another-password",
        )
        self.assertIsNone(duplicate)

    def test_account_changes_are_saved_to_csv(self):
        account = utils.create_account(
            "profile@example.test",
            "Original Name",
            "",
            "classroom-password",
        )

        updated = utils.update_account(account["id"], "Updated Name", "555-0101")

        self.assertEqual(updated["name"], "Updated Name")
        self.assertEqual(updated["phone"], "555-0101")
        self.assertEqual(
            utils.authenticate("profile@example.test", "classroom-password"),
            updated,
        )

    def test_csv_files_start_empty_without_a_database(self):
        self.assertTrue((utils.DATA_DIR / "accounts.csv").is_file())
        self.assertTrue((utils.DATA_DIR / "contacts.csv").is_file())
        self.assertTrue((utils.DATA_DIR / "community_reports.csv").is_file())
        self.assertFalse(list(utils.DATA_DIR.glob("*.sqlite3")))
        self.assertEqual(utils.load_reports(), [])

    def test_report_saves_urgency_and_is_public(self):
        report = utils.save_report(
            "Unsafe Area",
            "Test landmark",
            "High",
            "Test report content.",
        )
        stored = utils.load_reports()[0]
        self.assertEqual(stored["id"], report["id"])
        self.assertEqual(stored["urgency"], "High")
        self.assertEqual(stored["description"], "Test report content.")

    def test_contacts_are_scoped_by_account(self):
        first = utils.create_account("one@example.test", "First", "", "password-one")
        second = utils.create_account("two@example.test", "Second", "", "password-two")
        utils.save_contacts(first["id"], [{"name": "Trusted person", "phone": "0000000000"}])
        utils.save_contacts(second["id"], [{"name": "Other person", "phone": "1111111111"}])
        self.assertEqual(len(utils.load_contacts(first["id"])), 1)
        self.assertEqual(utils.load_contacts(first["id"])[0]["name"], "Trusted person")
        self.assertEqual(utils.load_contacts(second["id"])[0]["name"], "Other person")


if __name__ == "__main__":
    unittest.main()
