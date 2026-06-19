import unittest
from .trailer_security import YouTubeURLValidator, XSSProtection, TrailerEmbedCode

class TestYouTubeURLValidator(unittest.TestCase):

    def test_valid_youtube_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success, video_id, error = YouTubeURLValidator.extract_video_id(url)
        
        self.assertTrue(success)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        self.assertIsNone(error)

    def test_youtu_be_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        success, video_id, error = YouTubeURLValidator.extract_video_id(url)
        
        self.assertTrue(success)
        self.assertEqual(video_id, "dQw4w9WgXcQ")
        self.assertIsNone(error)

    def test_invalid_url_no_video_id(self):
        url = "https://www.youtube.com/watch?v="
        success, video_id, error = YouTubeURLValidator.extract_video_id(url)
        
        self.assertFalse(success)
        self.assertIsNone(video_id)
        self.assertIsNotNone(error)

    def test_empty_url(self):
        url = ""
        success, video_id, error = YouTubeURLValidator.extract_video_id(url)
        
        self.assertFalse(success)
        self.assertIsNone(video_id)
        self.assertEqual(error, "URL is empty")


class TestXSSProtection(unittest.TestCase):

    def test_sanitize_html_attribute(self):
        dangerous = 'value" onclick="alert(\'xss\')'
        safe = XSSProtection.sanitize_html_attribute(dangerous)
        
        self.assertNotIn('onclick=', safe)
        self.assertIn('&quot;', safe)

    def test_script_tag_escape(self):
        dangerous = '<script>alert("xss")</script>'
        safe = XSSProtection.sanitize_html_attribute(dangerous)
        
        self.assertNotIn('<script>', safe)
        self.assertIn('&lt;', safe)
        self.assertIn('&gt;', safe)

    def test_video_id_validation(self):
        valid_id = "dQw4w9WgXcQ"
        invalid_id = "dQw4w9WgXcQ<script>"
        
        self.assertTrue(XSSProtection.is_safe_video_id(valid_id))
        self.assertFalse(XSSProtection.is_safe_video_id(invalid_id))


class TestTrailerEmbedCode(unittest.TestCase):

    def test_valid_embed_code_generation(self):
        video_id = "dQw4w9WgXcQ"
        html = TrailerEmbedCode.generate_embed_html(video_id)
        
        self.assertIsNotNone(html)
        self.assertIn('youtube-nocookie.com', html)
        self.assertIn(video_id, html)
        self.assertIn('iframe', html)

    def test_lazy_loading_attribute(self):
        video_id = "dQw4w9WgXcQ"
        html = TrailerEmbedCode.generate_embed_html(video_id)
        
        self.assertIn('loading="lazy"', html)


if __name__ == '__main__':
    unittest.main()