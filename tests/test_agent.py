import unittest
from main import normalize, choose_topic
from utils.openai_generator import word_count


class AgentTests(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("AI: The Future!"), "ai the future")

    def test_topic_selection_skips_seen_topic(self):
        history = {"topics": ["Artificial Intelligence"], "titles": []}
        self.assertEqual(choose_topic(["Artificial Intelligence", "Clean Energy"], history), "Clean Energy")

    def test_html_word_count(self):
        self.assertEqual(word_count("<p>One <strong>two</strong> three.</p>"), 3)


if __name__ == "__main__":
    unittest.main()
