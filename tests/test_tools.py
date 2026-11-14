from unittest.mock import patch

from crew.tools import market_web_search, website_scraper


def test_market_web_search():
    """Verify that the web search tool returns search results."""

    mock_results = [
        {
            "title": "Indian Smartphone Market",
            "href": "https://example.com/smartphones",
            "body": "Smartphone market research information."
        }
    ]

    with patch("crew.tools.DDGS") as mock_ddgs:
        # Support both direct and context-manager initialization.
        mock_ddgs.return_value.text.return_value = mock_results
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs.return_value

        result = market_web_search.run("Indian smartphone market 2026")

        assert result
        assert "Indian Smartphone Market" in result
def test_website_scraper():
    """Verify that the scraper extracts webpage text."""

    mock_html = """
    <html>
        <body>
            <h1>Market Research</h1>
            <p>Smartphone industry analysis.</p>
        </body>
    </html>
    """

    with patch("crew.tools.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html
        mock_get.return_value.raise_for_status.return_value = None

        result = website_scraper.run("https://example.com")

        assert result is not None
        assert "Market Research" in result
        assert "Smartphone industry analysis" in result