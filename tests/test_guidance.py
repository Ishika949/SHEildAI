import unittest

from guidance import search_guidance
import utils
from streamlit.testing.v1 import AppTest


class GuidanceTests(unittest.TestCase):
    def test_returns_relevant_site_content(self):
        results = search_guidance("What should I do if I feel unsafe?")
        self.assertTrue(results)
        self.assertTrue(
            any("When something feels unsafe" == result["topic"] for result in results)
        )

    def test_does_not_invent_answers_for_unmatched_queries(self):
        self.assertEqual(search_guidance("weather forecast"), [])

    def test_ai_chat_page_uses_conversation_history(self):
        app = AppTest.from_file(
            str(utils.BASE_DIR / "pages" / "safety_guide.py"),
            default_timeout=15,
        ).run()

        self.assertEqual([title.value for title in app.title], ["AI Chat"])
        self.assertEqual(len(app.get("chat_input")), 1)
        self.assertEqual(
            app.session_state["ai_chat_messages"][0]["content"],
            "Hi! How can I help you today?",
        )

        app.chat_input[0].set_value("What should I do if I feel unsafe?").run()

        messages = app.session_state["ai_chat_messages"]
        self.assertEqual([message["role"] for message in messages], ["assistant", "user", "assistant"])
        self.assertIn("Focus on immediate support", messages[-1]["content"])

        app.button(key="clear_ai_chat").click().run()

        self.assertEqual(
            app.session_state["ai_chat_messages"],
            [{"role": "assistant", "content": "Hi! How can I help you today?"}],
        )


if __name__ == "__main__":
    unittest.main()
