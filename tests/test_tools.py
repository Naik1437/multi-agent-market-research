from unittest.mock import patch

import requests

from crew.tools import market_search_and_scrape, market_web_search, website_scraper


def test_market_web_search():
    """Verify that the web search tool returns search results."""

    mock_results = [
        {
            "title": "Indian Smartphone Market",
            "href": "https://example.com/smartphones",
            "body": "Smartphone market research information."
        }
    ]

    with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}), \
         patch("crew.tools.requests.post") as mock_post, \
         patch("monitoring.execution_tracker.record_provider_event") as telemetry:
        mock_post.return_value.json.return_value = {
            "results": [{
                "title": mock_results[0]["title"],
                "url": mock_results[0]["href"],
                "content": mock_results[0]["body"]
            }]
        }
        mock_post.return_value.raise_for_status.return_value = None

        result = market_web_search.run("Indian smartphone market 2026")

        assert result
        assert "Indian Smartphone Market" in result
        assert "https://example.com/smartphones" in result
        mock_post.assert_called_once()
        telemetry.assert_called_once_with("Tavily", "SUCCESS", result_count=1)


def test_search_and_scrape_returns_actual_page_text():
    results = [{"title": "Market report", "url": "https://example.com/report",
                "content": "Search excerpt"}]
    with patch("crew.tools._tavily_search", return_value=results), \
         patch("crew.tools._scrape_url", return_value="Full page content") as scrape:
        result = market_search_and_scrape.run("market query")

    assert "Search excerpt" in result
    assert "Full page content" in result
    scrape.assert_called_once_with("https://example.com/report")


def test_tavily_search_reports_missing_key_without_request():
    with patch.dict("os.environ", {"TAVILY_API_KEY": ""}), \
         patch("crew.tools.requests.post") as mock_post, \
         patch("monitoring.execution_tracker.record_provider_event") as telemetry:
        result = market_web_search.run("market query")

    assert "TAVILY_API_KEY is missing" in result
    mock_post.assert_not_called()
    telemetry.assert_called_once_with("Tavily", "FAILED", error_type="MissingAPIKey")


def test_tavily_api_failure_is_recorded_without_sensitive_details():
    with patch.dict("os.environ", {"TAVILY_API_KEY": "never-log-this"}), \
         patch("crew.tools.requests.post", side_effect=requests.Timeout("private diagnostic")), \
         patch("monitoring.execution_tracker.record_provider_event") as telemetry:
        result = market_web_search.run("market query")

    assert "Tavily search failed" in result
    telemetry.assert_called_once_with("Tavily", "FAILED", error_type="TimeoutError")
    assert "never-log-this" not in str(telemetry.call_args)
    assert "private diagnostic" not in str(telemetry.call_args)
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

    with patch("crew.tools._fetch_page", return_value=(200, {}, mock_html)):

        result = website_scraper.run("https://example.com")

        assert result is not None
        assert "Market Research" in result
        assert "Smartphone industry analysis" in result


def test_website_scraper_blocks_private_addresses():
    with patch("crew.tools.socket.create_connection") as mock_connect:
        result = website_scraper.run("http://127.0.0.1/admin")

    assert "not allowed" in result.lower()
    mock_connect.assert_not_called()


def test_website_scraper_revalidates_redirect_target():
    with patch("crew.tools._fetch_page", side_effect=[
        (302, {"Location": "http://127.0.0.1/private"}, ""),
        ValueError("Private or non-public network URLs are not allowed.")
    ]) as mock_fetch:
        result = website_scraper.run("https://example.com")

    assert "not allowed" in result.lower()
    assert mock_fetch.call_count == 2


def test_scraper_connects_to_the_validated_dns_address():
    from types import SimpleNamespace

    fake_response = SimpleNamespace(
        status=200,
        read=lambda size: b"ok",
        getheaders=lambda: [("Content-Type", "text/plain")],
        getheader=lambda name, default=None: "text/plain" if name == "Content-Type" else default
    )
    fake_connection = SimpleNamespace(
        request=lambda *args, **kwargs: None,
        getresponse=lambda: fake_response,
        close=lambda: None,
        sock=None
    )
    with patch("crew.tools.socket.getaddrinfo", return_value=[
        (2, 1, 6, "", ("93.184.216.34", 80))
    ]), patch("crew.tools.socket.create_connection", return_value=object()) as connect, \
         patch("crew.tools.http.client.HTTPConnection", return_value=fake_connection):
        from crew.tools import _fetch_page
        status, _, text = _fetch_page("http://example.com/article")

    assert status == 200
    assert text == "ok"
    assert connect.call_args.args[0] == ("93.184.216.34", 80)
