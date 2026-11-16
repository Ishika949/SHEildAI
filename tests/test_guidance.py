import unittest

from guidance import search_guidance
import utils
from streamlit.testing.v1 import AppTest


class GuidanceTests(unittest.TestCase):
    def test_returns_relevant_site_content(self):
        results = search_guidance("What should I do if I feel unsafe?")
        self.assertTrue(results)
        self.assertTrue(
            any(
                "What To Do in an Unsafe Situation" == result["topic"]
                for result in results
            )
        )

    def test_does_not_invent_answers_for_unmatched_queries(self):
        self.assertEqual(search_guidance("weather forecast"), [])

    def test_ai_chat_page_uses_conversation_history(self):
        app = AppTest.from_file(
            str(utils.BASE_DIR / "pages" / "safety_guide.py"),
            default_timeout=15,
        ).run()

        self.assertEqual([title.value for title in app.title], ["🛡️ SHEild AI"])
        self.assertEqual([header.value for header in app.header], ["💬 AI Chat"])
        self.assertEqual(len(app.get("chat_input")), 1)
        self.assertEqual(
            app.session_state["ai_chat_messages"][0]["content"],
            "Hi! How can I help you today?",
        )

        app.chat_input[0].set_value("What should I do if I feel unsafe?").run()

        messages = app.session_state["ai_chat_messages"]
        self.assertEqual([message["role"] for message in messages], ["assistant", "user", "assistant"])
        self.assertIn(
            "What To Do in an Unsafe Situation",
            messages[-1]["content"],
        )

        app.button(key="clear_ai_chat").click().run()

        self.assertEqual(
            app.session_state["ai_chat_messages"],
            [{"role": "assistant", "content": "Hi! How can I help you today?"}],
        )

    def test_learning_page_shows_requested_topics_and_legal_notes(self):
        app = AppTest.from_file(
            str(utils.BASE_DIR / "pages" / "learning.py"),
            default_timeout=15,
        ).run()

        self.assertFalse(app.exception)
        self.assertEqual([title.value for title in app.title], ["🛡️ SHEild AI"])
        self.assertEqual([header.value for header in app.header], ["📚 Learn & Know"])
        self.assertEqual(
            app.selectbox[0].options,
            [
                "Women's Safety Rules",
                "Legal Rights in India",
                "Constitutional Rights",
                "What To Do in an Unsafe Situation",
            ],
        )

        expected_content = {
            "Women's Safety Rules": (
                [
                    "Stay aware of your surroundings.",
                    "Keep emergency contacts easily accessible.",
                    "Inform a trusted person when travelling alone.",
                    "Avoid sharing personal information with strangers.",
                    "Move to a safe and populated place if you feel unsafe.",
                    "Report serious safety concerns to the appropriate authorities.",
                ],
                None,
                None,
                None,
                None,
                "🛡️",
            ),
            "Legal Rights in India": (
                [
                    "Protection against sexual harassment",
                    "Protection against stalking",
                    "Protection against certain forms of assault",
                    "Protection against cruelty and certain marriage-related offences",
                    "Protection under the Bharatiya Nyaya Sanhita, 2023",
                ],
                (
                    "Indian law provides various protections against offences and "
                    "unfair treatment of women."
                ),
                "This information is provided for educational awareness and is not legal advice.",
                None,
                None,
                "⚖️",
            ),
            "Constitutional Rights": (
                [
                    "Article 14 – Equality before law.",
                    "Article 15 – Prohibits discrimination on grounds including sex.",
                    "Article 15(3) – Special provisions can be made for women and children.",
                    "Article 16 – Equal opportunity in public employment.",
                    "Article 21 – Right to life and personal liberty.",
                    "Article 39(d) – Equal pay for equal work.",
                    "Article 42 – Humane working conditions and maternity relief.",
                ],
                None,
                None,
                "These provisions support equality, dignity and protection of women.",
                None,
                "🏛️",
            ),
            "What To Do in an Unsafe Situation": (
                [
                    "Move towards a safe and populated place.",
                    "Contact a trusted family member, friend or teacher.",
                    "Seek emergency help if there is immediate danger.",
                    "Clearly explain your situation to someone you trust.",
                    "Avoid confronting someone who may be dangerous.",
                    "Report the incident to the appropriate authority when appropriate.",
                ],
                None,
                None,
                None,
                "If you are in immediate danger, focus on reaching a safe place and getting help.",
                "🚨",
            ),
        }
        for topic, (
            points,
            introduction,
            note,
            info,
            warning,
            emoji,
        ) in expected_content.items():
            app.selectbox[0].set_value(topic).run()
            rendered_markdown = "\n".join(item.value for item in app.markdown)
            for point in points:
                self.assertIn(point, rendered_markdown, topic)
            if introduction:
                self.assertIn(introduction, rendered_markdown, topic)
            self.assertIn(
                f"{emoji} {topic}",
                [header.value for header in app.subheader],
            )
            if note:
                self.assertTrue(
                    any(note in item.value for item in app.info),
                    topic,
                )
            if info:
                self.assertTrue(
                    any(info in item.value for item in app.info),
                    topic,
                )
            if warning:
                self.assertTrue(
                    any(warning in item.value for item in app.warning),
                    topic,
                )


if __name__ == "__main__":
    unittest.main()
