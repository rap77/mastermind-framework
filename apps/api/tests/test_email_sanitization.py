"""Tests for email HTML sanitization with nh3."""

from routers.email import sanitize_html, EmailMessage


class TestSanitizeHtml:
    """Test HTML sanitization function."""

    def test_sanitizes_safe_html(self):
        """Safe HTML tags should be preserved."""
        html = "<p>Hello <strong>world</strong></p>"
        result = sanitize_html(html)
        assert result == html

    def test_sanitizes_links(self):
        """Safe links with href should be preserved."""
        html = '<a href="https://example.com">Link</a>'
        result = sanitize_html(html)
        # nh3 adds rel="noopener noreferrer" for security
        assert 'href="https://example.com"' in result
        assert ">Link<" in result

    def test_removes_script_tags(self):
        """Script tags should be removed."""
        html = "<p>Hello</p><script>alert('xss')</script>"
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "alert" not in result
        assert "<p>Hello</p>" in result

    def test_removes_iframe_tags(self):
        """Iframe tags should be removed."""
        html = '<p>Content</p><iframe src="evil.com"></iframe>'
        result = sanitize_html(html)
        assert "<iframe>" not in result
        assert "evil.com" not in result
        assert "<p>Content</p>" in result

    def test_removes_object_tags(self):
        """Object tags should be removed."""
        html = '<p>Content</p><object data="evil.swf"></object>'
        result = sanitize_html(html)
        assert "<object>" not in result
        assert "<p>Content</p>" in result

    def test_removes_embed_tags(self):
        """Embed tags should be removed."""
        html = '<p>Content</p><embed src="evil.swf">'
        result = sanitize_html(html)
        assert "<embed>" not in result
        assert "<p>Content</p>" in result

    def test_removes_onclick_attributes(self):
        """Event handler attributes should be removed."""
        html = "<p onclick=\"alert('xss')\">Click me</p>"
        result = sanitize_html(html)
        assert "onclick" not in result
        assert "alert" not in result
        assert "<p>Click me</p>" in result

    def test_allows_safe_attributes(self):
        """Safe attributes like href and title should be preserved."""
        html = '<a href="https://example.com" title="Example">Link</a>'
        result = sanitize_html(html)
        assert 'href="https://example.com"' in result
        assert 'title="Example"' in result

    def test_preserves_heading_tags(self):
        """Heading tags should be preserved."""
        html = "<h1>Title</h1><h2>Subtitle</h2>"
        result = sanitize_html(html)
        assert result == html

    def test_preserves_list_tags(self):
        """List tags should be preserved."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = sanitize_html(html)
        assert result == html


class TestEmailMessage:
    """Test EmailMessage model with sanitization."""

    def test_html_body_sanitized_on_validation(self):
        """HTML body should be sanitized during validation."""
        email = EmailMessage(
            to="test@example.com",
            subject="Test",
            html_body="<p>Safe</p><script>alert('xss')</script>",
        )
        assert "<script>" not in email.html_body
        assert "<p>Safe</p>" in email.html_body

    def test_plain_text_unchanged(self):
        """Plain text should not be modified."""
        email = EmailMessage(
            to="test@example.com",
            subject="Test",
            plain_text="Hello world",
        )
        assert email.plain_text == "Hello world"

    def test_none_html_body_allowed(self):
        """None HTML body should be allowed."""
        email = EmailMessage(
            to="test@example.com",
            subject="Test",
            plain_text="Hello",
        )
        assert email.html_body is None

    def test_complex_xss_attempt_sanitized(self):
        """Complex XSS attempts should be neutralized."""
        xss_payload = """
        <p>Normal content</p>
        <img src=x onerror="alert('xss')">
        <script>alert('xss')</script>
        <iframe src="javascript:alert('xss')"></iframe>
        """
        email = EmailMessage(
            to="test@example.com",
            subject="Test",
            html_body=xss_payload,
        )
        # Check that dangerous elements are removed
        assert "<script>" not in email.html_body
        assert "<iframe>" not in email.html_body
        assert "onerror" not in email.html_body
        assert "javascript:" not in email.html_body
        # Safe content preserved
        assert "<p>Normal content</p>" in email.html_body
