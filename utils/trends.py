"""Google Trends RSS topic discovery with safe configured fallbacks."""
import xml.etree.ElementTree as ET
import requests


def get_trending_topics(geo: str = "US", fallback: list[str] | None = None) -> list[str]:
    try:
        response = requests.get(
            "https://trends.google.com/trending/rss", params={"geo": geo},
            timeout=20, headers={"User-Agent": "AutoBloggerAgent/1.0"},
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)
        topics = []
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            if title and title not in topics:
                topics.append(title)
        if topics:
            return topics
    except (requests.RequestException, ET.ParseError) as exc:
        print(f"Trends feed unavailable; using configured topics. Details: {exc}")
    return [item.strip() for item in (fallback or []) if item.strip()]
