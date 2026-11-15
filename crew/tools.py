import http.client
import ipaddress
import os
import socket
import ssl
from email.message import Message
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from crewai.tools import tool


TAVILY_SEARCH_URL = "https://api.tavily.com/search"
MAX_SEARCH_RESULTS = 5
MAX_PAGES_TO_SCRAPE = 3
MAX_PAGE_BYTES = 2 * 1024 * 1024
MAX_PAGE_CHARS = 10000


def validate_public_url(url):
    """Resolve and validate a public URL; return the address to pin the request to."""
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Only valid HTTP or HTTPS URLs are allowed.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    host = parsed.hostname.rstrip(".").lower()
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Localhost URLs are not allowed.")

    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(record[4][0])
                for record in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            }
        except OSError as error:
            raise ValueError("URL host could not be resolved.") from error

    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Private or non-public network URLs are not allowed.")
    return parsed, next(iter(addresses)), port


def _fetch_page(url):
    """Fetch a page using the IP that was just validated, preventing DNS rebinding."""
    parsed, address, port = validate_public_url(url)
    host = parsed.hostname
    raw_socket = socket.create_connection((str(address), port), timeout=15)
    connection = http.client.HTTPConnection(host, port, timeout=15)
    connection.sock = raw_socket
    try:
        if parsed.scheme == "https":
            raw_socket = ssl.create_default_context().wrap_socket(
                raw_socket,
                server_hostname=host
            )
            connection.sock = raw_socket
        request_target = urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
        connection.request(
            "GET",
            request_target,
            headers={
                "Host": parsed.netloc,
                "User-Agent": "Mozilla/5.0 MarketResearchBot/1.0",
                "Accept": "text/html,application/xhtml+xml,text/plain"
            }
        )
        response = connection.getresponse()
        body = response.read(MAX_PAGE_BYTES + 1)
        if len(body) > MAX_PAGE_BYTES:
            raise ValueError("Webpage exceeds the 2 MB content limit.")

        content_type = Message()
        content_type["content-type"] = response.getheader("Content-Type", "")
        charset = content_type.get_content_charset() or "utf-8"
        try:
            text = body.decode(charset, errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        return response.status, dict(response.getheaders()), text
    finally:
        connection.close()


def _scrape_url(url):
    current_url = url
    for redirect_count in range(6):
        status, headers, body = _fetch_page(current_url)
        if status not in (301, 302, 303, 307, 308):
            if status < 200 or status >= 300:
                raise ValueError(f"Webpage returned HTTP status {status}.")
            soup = BeautifulSoup(body, "html.parser")
            for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                element.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return text[:MAX_PAGE_CHARS] if text else "No readable content found."

        location = next((v for k, v in headers.items() if k.lower() == "location"), None)
        if not location or redirect_count == 5:
            raise ValueError("Too many or invalid webpage redirects.")
        current_url = urljoin(current_url, location)
    raise ValueError("Too many webpage redirects.")


def _tavily_search(query):
    from monitoring.execution_tracker import record_provider_event

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        record_provider_event("Tavily", "FAILED", error_type="MissingAPIKey")
        raise RuntimeError("TAVILY_API_KEY is missing; configure it in the environment or .env.")

    try:
        response = requests.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": MAX_SEARCH_RESULTS
            },
            timeout=30
        )
        response.raise_for_status()
        results = [result for result in response.json().get("results", []) if result.get("url")]
    except Exception as error:
        error_type = (
            "TimeoutError"
            if isinstance(error, requests.Timeout)
            else type(error).__name__
        )
        record_provider_event("Tavily", "FAILED", error_type=error_type)
        raise

    record_provider_event("Tavily", "SUCCESS", result_count=len(results))
    return results


@tool("Market Web Search")
def market_web_search(query: str) -> str:
    """Search Tavily for current market information and return cited result URLs."""
    try:
        results = _tavily_search(query)
        if not results:
            return "No search results found."
        return "\n\n".join(
            f"Result {i}\nTitle: {r.get('title', 'N/A')}\nURL: {r['url']}\n"
            f"Summary: {r.get('content', 'N/A')}"
            for i, r in enumerate(results, start=1)
        )
    except RuntimeError as error:
        return str(error)
    except requests.RequestException as error:
        return f"Tavily search failed ({type(error).__name__}). Check API access and try again."
    except (ValueError, KeyError) as error:
        return f"Tavily search failed: {error}"


@tool("Website Content Scraper")
def website_scraper(url: str) -> str:
    """Fetch readable text from a public webpage, validating every redirect."""
    try:
        return _scrape_url(url)
    except (ValueError, OSError, ssl.SSLError, http.client.HTTPException) as error:
        return f"Website scraping failed: {error}"


@tool("Market Search and Page Scraper")
def market_search_and_scrape(query: str) -> str:
    """Search Tavily, then fetch and return readable text from up to three result pages."""
    try:
        results = _tavily_search(query)
        if not results:
            return "No search results found."

        gathered = []
        for result in results[:MAX_PAGES_TO_SCRAPE]:
            url = result["url"]
            title = result.get("title", "Untitled result")
            summary = result.get("content", "")
            try:
                page_text = _scrape_url(url)
            except (ValueError, OSError, ssl.SSLError, http.client.HTTPException) as error:
                page_text = f"Page could not be scraped: {error}"
            gathered.append(
                f"Title: {title}\nURL: {url}\nSearch summary: {summary}\n"
                f"Page content: {page_text}"
            )
        return "\n\n---\n\n".join(gathered)
    except RuntimeError as error:
        return str(error)
    except requests.RequestException as error:
        return f"Tavily search failed ({type(error).__name__}). Check API access and try again."
    except (ValueError, KeyError) as error:
        return f"Market search failed: {error}"


print("Custom Tavily search and secure webpage tools loaded successfully!")
