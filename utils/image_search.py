"""Optional Unsplash lookup with contributor attribution."""
import requests


def find_image(query: str, access_key: str = "") -> dict | None:
    if not access_key:
        print("UNSPLASH_ACCESS_KEY is not configured; continuing without a featured image.")
        return None
    response = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {access_key}"},
        timeout=25,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        print("No Unsplash image matched this topic; continuing without an image.")
        return None
    photo, user = results[0], results[0].get("user", {})
    image_url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small")
    if not image_url:
        return None
    return {
        "url": image_url,
        "author": user.get("name", "Unsplash contributor"),
        "author_url": user.get("links", {}).get("html", "https://unsplash.com"),
        "source_url": photo.get("links", {}).get("html", "https://unsplash.com"),
    }
