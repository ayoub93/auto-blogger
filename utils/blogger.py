"""Blogger API v3 client. Draft creation only; no publishing method is exposed."""
from __future__ import annotations
import os
from html import escape
import requests


class BloggerClient:
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    API_ROOT = "https://www.googleapis.com/blogger/v3"

    def __init__(self, blog_id: str, client_id: str, client_secret: str, refresh_token: str):
        self.blog_id, self.client_id = blog_id, client_id
        self.client_secret, self.refresh_token = client_secret, refresh_token
        self.session = requests.Session()

    @classmethod
    def from_env(cls):
        names = ("BLOGGER_BLOG_ID", "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN")
        values = {key: os.getenv(key, "").strip() for key in names}
        missing = [key for key, value in values.items() if not value]
        if missing:
            raise RuntimeError("Missing GitHub Actions secrets: " + ", ".join(missing))
        return cls(values[names[0]], values[names[1]], values[names[2]], values[names[3]])

    def _access_token(self):
        response = self.session.post(self.TOKEN_URL, data={
            "client_id": self.client_id, "client_secret": self.client_secret,
            "refresh_token": self.refresh_token, "grant_type": "refresh_token",
        }, timeout=30)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise RuntimeError("Google OAuth response did not contain an access token.")
        return token

    def create_draft(self, article: dict, image: dict | None = None):
        content = article["content_html"]
        if image and image.get("url"):
            content = (
                f'<figure><img src="{escape(image["url"], quote=True)}" alt="{escape(article["title"], quote=True)}" style="max-width:100%;height:auto" />'
                f'<figcaption>Photo by <a href="{escape(image["author_url"], quote=True)}">{escape(image["author"])}</a> '
                f'on <a href="{escape(image["source_url"], quote=True)}">Unsplash</a></figcaption></figure>\n' + content
            )
        # isDraft=true is intentional. This agent never publishes automatically.
        response = self.session.post(
            f"{self.API_ROOT}/blogs/{self.blog_id}/posts/",
            params={"isDraft": "true"},
            headers={"Authorization": f"Bearer {self._access_token()}"},
            json={"kind": "blogger#post", "title": article["title"],
                  "content": content, "labels": article.get("tags", [])},
            timeout=45,
        )
        response.raise_for_status()
        result = response.json()
        if not result.get("id"):
            raise RuntimeError("Blogger response did not include a post ID.")
        return result
