import unittest

from app.command_processor import match_command, normalize


class CommandProcessorTests(unittest.TestCase):
    def test_arabic_diacritics_are_ignored(self):
        self.assertEqual(normalize("إفتحْ فَايْرَفُوكْس"), "افتح فايرفوكس")

    def test_arabic_app_alias(self):
        self.assertEqual(match_command("افتح فايرفوكس"), "open_firefox")

    def test_english_volume_alias(self):
        self.assertEqual(match_command("please volume up"), "volume_up")

    def test_website_alias(self):
        self.assertEqual(match_command("افتح يوتيوب"), "open_youtube")

    def test_only_http_urls_are_opened(self):
        self.assertEqual(
            match_command("open https://example.com/path"),
            ("open_url", "https://example.com/path"),
        )
        self.assertIsNone(match_command("open file:///etc/passwd"))

    def test_unknown_command_is_rejected(self):
        self.assertIsNone(match_command("delete all my files"))


if __name__ == "__main__":
    unittest.main()
