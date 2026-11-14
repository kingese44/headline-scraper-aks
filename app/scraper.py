import requests
from bs4 import BeautifulSoup

# A list: an ordered collection of values, in square brackets.
websites = [
    "https://www.bbc.com/news",
    "https://www.theguardian.com/international",
]


def get_headlines(url):
    """Download one page and return its headlines as a list of strings."""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(strip=True)
        if text:
            headlines.append(text)
    return headlines


for site in websites:
    print(f"\n=== {site} ===")
    try:
        for headline in get_headlines(site):
            print(f"- {headline}")
    except requests.RequestException as error:
        print(f"Could not fetch this site: {error}")