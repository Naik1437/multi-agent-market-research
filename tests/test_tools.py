from crew.tools import (
    market_web_search,
    website_scraper
)

# TEST 1: WEB SEARCH

print("\n========== WEB SEARCH TEST ==========\n")

result = market_web_search.run(
    "Indian smartphone market 2026"
)

print(result)


# TEST 2: WEBSITE SCRAPER

print("\n========== WEBSITE SCRAPER TEST ==========\n")

result = website_scraper.run(
    "https://www.wikipedia.org/"
)

print(result[:1000])


print("\n========== TESTING COMPLETED ==========")