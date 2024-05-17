import os
from googleapiclient.discovery import build
import dotenv
import requests
from bs4 import BeautifulSoup

dotenv.load_dotenv()

def get_page_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(strip=True)

def main():
    service = build(
        "customsearch", "v1", developerKey=os.environ["GOOGLE_API_KEY"]
    )

    res = (
        service.cse()
        .list(
            q="do fish need bath",
            cx=os.environ["GOOGLE_SEARCH_ENGINE_ID"],
        )
        .execute()
    )

    top_results = res["items"][:5]

    for i, result in enumerate(top_results, start=1):
        url = result["link"]
        title = result["title"]
        text = get_page_text(url)

        print(f"Result {i}:")
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Text: {text}")
        print()

if __name__ == "__main__":
    main()