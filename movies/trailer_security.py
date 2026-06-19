import re
from urllib.parse import urlparse
from django.core.exceptions import ValidationError


class YouTubeURLValidator:
    """Validates and extracts video IDs from YouTube URLs"""

    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*?[?&]v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]

    VIDEO_ID_PATTERN = r'^[a-zA-Z0-9_-]{11}$'

    @classmethod
    def extract_video_id(cls, url):
        """
        Extract video ID from YouTube URL
        Returns: (success, video_id, error)
        """
        if not url:
            return False, None, "URL is empty"

        url = url.strip()

        if not cls._is_valid_url_format(url):
            return False, None, "Invalid URL format"

        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)

                if re.fullmatch(cls.VIDEO_ID_PATTERN, video_id):
                    return True, video_id, None

        return False, None, "Could not extract valid YouTube video ID"

    @staticmethod
    def _is_valid_url_format(url):
        """Basic URL validation"""
        try:
            result = urlparse(url)
            host = result.netloc.lower()

            allowed_domains = {
                "youtube.com",
                "www.youtube.com",
                "youtu.be"
            }

            return (
                host in allowed_domains
                or host.endswith(".youtube.com")
            )

        except Exception:
            return False

    @classmethod
    def validate_url(cls, url):
        """
        Validate URL and return video ID
        """
        success, video_id, error = cls.extract_video_id(url)

        if not success:
            raise ValidationError(f"Invalid YouTube URL: {error}")

        return video_id


class XSSProtection:
    """XSS prevention utilities"""

    @staticmethod
    def sanitize_html_attribute(value):
        """Escape HTML special characters"""
        if not isinstance(value, str):
            return value

        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
        }

        for char, escaped in replacements.items():
            value = value.replace(char, escaped)

        return value

    @staticmethod
    def is_safe_video_id(video_id):
        """Check whether video ID is safe"""
        return bool(
            re.fullmatch(r'[a-zA-Z0-9_-]{11}', video_id)
        )

    @staticmethod
    def sanitize_url(url):
        """Allow only HTTP(S) YouTube URLs"""
        if not url.startswith(("https://", "http://")):
            return None

        if not any(domain in url for domain in ["youtube.com", "youtu.be"]):
            return None

        return url


class TrailerEmbedCode:
    """Generate safe embed code"""

    @staticmethod
    def generate_iframe_src(video_id):
        """
        Generate secure YouTube embed URL
        """
        if not XSSProtection.is_safe_video_id(video_id):
            return None

        return (
            f"https://www.youtube-nocookie.com/embed/{video_id}"
            "?modestbranding=1"
            "&rel=0"
            "&controls=1"
            "&fs=1"
        )

    @staticmethod
    def generate_embed_html(
        video_id,
        title="Movie Trailer",
        width="100%",
        height="500"
    ):
        """
        Generate complete embed HTML
        """

        if not XSSProtection.is_safe_video_id(video_id):
            return TrailerEmbedCode._generate_error_html(
                "Invalid video ID"
            )

        src = TrailerEmbedCode.generate_iframe_src(video_id)

        html = f"""
        <div class="trailer-container" data-video-id="{video_id}">
            <div class="trailer-wrapper" style="width:{width};max-width:100%;">
                <iframe
                    class="trailer-iframe"
                    width="100%"
                    height="{height}"
                    src="{src}"
                    title="{TrailerEmbedCode._escape_attr(title)}"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                    loading="lazy">
                </iframe>
            </div>

            <noscript>
                <p>Please enable JavaScript to view the trailer.</p>
            </noscript>
        </div>
        """

        return html

    @staticmethod
    def _escape_attr(value):
        """Escape attribute values"""
        if not isinstance(value, str):
            return ""

        return XSSProtection.sanitize_html_attribute(value)

    @staticmethod
    def _generate_error_html(message):
        """Generate fallback error HTML"""

        return f"""
        <div class="trailer-error"
             style="background:#f8d7da;
                    color:#721c24;
                    padding:15px;
                    border-radius:4px;">

            <p><strong>Trailer Unavailable</strong></p>
            <p>{TrailerEmbedCode._escape_attr(message)}</p>

        </div>
        """