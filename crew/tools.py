import requests

from bs4 import BeautifulSoup
from ddgs import DDGS
from crewai.tools import tool


# ==========================================
# TOOL 1: WEB SEARCH
# ==========================================

@tool("Market Web Search")
def market_web_search(query: str) -> str:
    """
    Search the web for market research, industry trends,
    company information and financial news.

    Input: A market research search query.
    Output: Search results containing titles, URLs and summaries.
    """

    try:
        results = DDGS().text(
            query,
            max_results=5
        )

        if not results:
            return "No search results found."

        formatted_results = []

        for index, result in enumerate(results, start=1):

            formatted_results.append(
                f"""
                Result {index}
                Title: {result.get('title', 'N/A')}
                URL: {result.get('href', 'N/A')}
                Summary: {result.get('body', 'N/A')}
                """
            )

        return "\n".join(formatted_results)

    except Exception as error:

        return f"Web search failed: {str(error)}"


# ==========================================
# TOOL 2: WEBSITE SCRAPER
# ==========================================

@tool("Website Content Scraper")

def website_scraper(url: str) -> str:
    """
    Extract readable text from a publicly accessible webpage.
    Handles character encoding and HTML parsing.
    """

    try:
        if not url.startswith(("http://", "https://")):
            return "Invalid URL. Use HTTP or HTTPS."

        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 MarketResearchBot/1.0"
            },
            timeout=15
        )

        response.raise_for_status()

        # Detect the correct character encoding
        response.encoding = response.apparent_encoding

        # Parse HTML
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unnecessary elements
        for element in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "noscript"
        ]):
            element.decompose()

        # Extract readable text
        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if not text:
            return "No readable content found."

        return text[:10000]

    except requests.RequestException as error:
        return f"Website scraping failed: {str(error)}"

    except Exception as error:
        return f"Unexpected scraping error: {str(error)}"
        return text[:10000]

    except requests.RequestException as error:

        return f"Website scraping failed: {str(error)}"

    except Exception as error:

        return f"Unexpected scraping error: {str(error)}"


print("Custom research tools loaded successfully!")