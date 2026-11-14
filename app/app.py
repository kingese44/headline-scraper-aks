from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

WEBSITES = [
    "https://www.bbc.com/news",
    "https://www.theguardian.com/international",
]

MAX_HEADLINES = 15


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


# The HTML for the page. The {{ ... }} and {% ... %} parts are filled in by Python.
PAGE = """
<!doctype html>
<html>
<head>
  <title>Headlines</title>
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
    h2 { margin-top: 2rem; color: #444; }
    li { margin-bottom: 0.4rem; }
  </style>
</head>
<body>
  <h1>Today's headlines</h1>
  {% for site in results %}
    <h2>{{ site.url }}</h2>
    {% if site.error %}
      <p>Could not fetch this site: {{ site.error }}</p>
    {% else %}
      <ul>
        {% for headline in site.headlines %}
          <li>{{ headline }}</li>
        {% endfor %}
      </ul>
    {% endif %}
  {% endfor %}
</body>
</html>
"""


@app.route("/")
def home():
    results = []
    for url in WEBSITES:
        try:
            headlines = get_headlines(url)[:MAX_HEADLINES]
            results.append({"url": url, "headlines": headlines, "error": None})
        except requests.RequestException as error:
            results.append({"url": url, "headlines": [], "error": str(error)})
    return render_template_string(PAGE, results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)