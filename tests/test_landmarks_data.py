import unittest
from urllib.parse import urlparse

from landmarks import LANDMARKS


class TestLandmarksData(unittest.TestCase):
    # Contract expected by the game engine and content workflow.
    required_keys = {"name", "aliases", "description", "hint", "location", "year", "sources"}

    def test_landmarks_dataset_is_not_empty(self) -> None:
        self.assertIsInstance(LANDMARKS, list)
        self.assertGreater(len(LANDMARKS), 0)

    def test_every_landmark_has_required_fields(self) -> None:
        for idx, landmark in enumerate(LANDMARKS):
            with self.subTest(landmark_index=idx):
                self.assertTrue(self.required_keys.issubset(landmark.keys()))

    def test_text_fields_are_non_empty(self) -> None:
        text_fields = ["name", "description", "hint", "location", "year"]

        for idx, landmark in enumerate(LANDMARKS):
            with self.subTest(landmark_index=idx):
                for field in text_fields:
                    value = landmark[field]
                    self.assertIsInstance(value, str)
                    self.assertTrue(value.strip(), f"Field '{field}' must not be empty")

    def test_aliases_are_well_formed(self) -> None:
        for idx, landmark in enumerate(LANDMARKS):
            with self.subTest(landmark_index=idx):
                aliases = landmark["aliases"]
                self.assertIsInstance(aliases, list)
                self.assertGreaterEqual(len(aliases), 1)
                for alias in aliases:
                    self.assertIsInstance(alias, str)
                    self.assertTrue(alias.strip())

    def test_sources_are_valid_urls(self) -> None:
        for idx, landmark in enumerate(LANDMARKS):
            with self.subTest(landmark_index=idx):
                sources = landmark["sources"]
                self.assertIsInstance(sources, list)
                self.assertGreaterEqual(len(sources), 2)

                for source in sources:
                    self.assertIsInstance(source, str)
                    parsed = urlparse(source)
                    self.assertIn(parsed.scheme, {"http", "https"})
                    self.assertTrue(parsed.netloc, f"Source has no hostname: {source}")

    def test_landmark_names_are_unique(self) -> None:
        normalized_names = [landmark["name"].strip().lower() for landmark in LANDMARKS]
        self.assertEqual(len(normalized_names), len(set(normalized_names)))


if __name__ == "__main__":
    unittest.main()
