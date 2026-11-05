"""AI Blogger Agent: researches, writes, checks and saves Blogger drafts for human review."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils.blogger import BloggerClient
from utils.image_search import find_image
from utils.openai_generator import generate_article
from utils.trends import get_trending_topics

ROOT = Path(__file__).resolve().parent
HISTORY_PATH = ROOT / "used_titles.json"
OUTPUT_DIR = ROOT / "output"


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_history() -> dict:
    if not HISTORY_PATH.exists():
        return {"titles": [], "topics": []}
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return {"titles": data.get("titles", [])[-500:], "topics": data.get("topics", [])[-500:]}
    except (json.JSONDecodeError, OSError):
        print("Warning: history file could not be read; starting with empty history.")
        return {"titles": [], "topics": []}


def save_history(history: dict) -> None:
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def choose_topic(topics: list[str], history: dict) -> str:
    seen = {normalize(x) for x in history.get("topics", [])}
    for topic in topics:
        if normalize(topic) and normalize(topic) not in seen:
            return topic
    raise RuntimeError("No fresh topic was found. Add new topics or review used_titles.json.")


def save_preview(article: dict, image: dict | None) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9-]+", "-", article["slug"].lower()).strip("-") or "article-preview"
    path = OUTPUT_DIR / f"{slug}.html"
    content = article["content_html"]
    if image:
        content = (
            f'<figure><img src="{image["url"]}" alt="{article["title"]}" style="max-width:100%;height:auto" />'
            f'<figcaption>Photo: <a href="{image["author_url"]}">{image["author"]}</a> / '
            f'<a href="{image["source_url"]}">Unsplash</a></figcaption></figure>\n' + content
        )
    path.write_text(
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        f"<title>{article['title']}</title></head><body><h1>{article['title']}</h1>"
        f"<p><strong>Meta description:</strong> {article['meta_description']}</p>{content}</body></html>",
        encoding="utf-8",
    )
    return path


def run(dry_run: bool = False) -> None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY secret.")
    history = load_history()
    topics = get_trending_topics(
        geo=os.getenv("TRENDS_GEO", "US"),
        fallback=os.getenv("FALLBACK_TOPICS", "artificial intelligence, consumer technology, science discoveries, digital productivity, renewable energy").split(","),
    )
    topic = choose_topic(topics, history)
    print(f"Selected topic: {topic}")
    article = generate_article(
        api_key=api_key, topic=topic,
        language=os.getenv("ARTICLE_LANGUAGE", "English"),
        min_words=int(os.getenv("MIN_ARTICLE_WORDS", "800")),
    )
    known_titles = {normalize(title) for title in history.get("titles", [])}
    if normalize(article["title"]) in known_titles:
        raise RuntimeError("Duplicate article title detected. No Blogger draft was created; review the topic/history.")
    image = find_image(article.get("focus_keyword") or article["title"], os.getenv("UNSPLASH_ACCESS_KEY", "").strip())
    preview = save_preview(article, image)
    print(f"Article generated ({article['word_count']} words). Preview: {preview}")
    if dry_run:
        print("Dry run complete. No Blogger API request was made.")
        return

    blogger = BloggerClient.from_env()
    draft = blogger.create_draft(article, image=image)
    post_id = draft.get("id", "unknown")
    print(f"Draft created successfully. Blogger post ID: {post_id}")
    print("Review it in Blogger → Posts → Drafts. The agent did not publish it.")

    history.setdefault("titles", []).append(article["title"])
    history.setdefault("topics", []).append(topic)
    history["titles"] = history["titles"][-500:]
    history["topics"] = history["topics"][-500:]
    save_history(history)

    record = {
        "post_id": post_id, "title": article["title"], "topic": topic,
        "status": "pending_human_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "url": draft.get("url", ""), "preview": str(preview.relative_to(ROOT)),
    }
    review_path = ROOT / "pending_review.json"
    records = []
    if review_path.exists():
        try:
            records = json.loads(review_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            records = []
    records.append(record)
    review_path.write_text(json.dumps(records[-200:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Blogger draft for human review.")
    parser.add_argument("--dry-run", action="store_true", help="Generate a local preview without calling Blogger.")
    args = parser.parse_args()
    try:
        run(dry_run=args.dry_run)
    except Exception as exc:
        print(f"AI Blogger Agent failed: {exc}", file=sys.stderr)
        sys.exit(1)
