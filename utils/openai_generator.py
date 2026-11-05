"""SEO article generation through the OpenAI Chat Completions API."""
from __future__ import annotations
import json
import re
import requests
from html.parser import HTMLParser


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def word_count(html: str) -> int:
    parser = _TextExtractor()
    parser.feed(html)
    return len(re.findall(r"\b[\w'-]+\b", " ".join(parser.parts)))


def _extract_json(content: str) -> dict:
    cleaned = re.sub(r"^\s*```(?:json)?\s*", "", content.strip())
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise


def generate_article(api_key: str, topic: str, language: str = "English", min_words: int = 800) -> dict:
    system_prompt = (
        "You are the editorial and SEO agent for a reputable international blog. "
        "Write original, useful content. Never invent quotes, statistics, studies, URLs, "
        "or source attributions. Qualify uncertain claims. Avoid sensationalism and harmful instructions. "
        "Return only valid JSON."
    )
    user_prompt = f"""
Write a publication-ready article in {language} about: {topic}
Requirements:
- At least {min_words} words in content_html, excluding title and metadata.
- Natural tone, short paragraphs, useful sections, practical takeaways where appropriate, and conclusion.
- Semantic HTML only: h2, h3, p, ul, ol, li, strong, em, blockquote, a.
- No scripts, CSS, html/head/body tags, fabricated citations, or unsupported external links.
- SEO title ideally 50-60 chars; meta description 150-160 chars; readable English slug;
  one focus keyword and 3-6 relevant tags. No keyword stuffing.
Return JSON with exactly these keys:
{{"title":"...","meta_description":"...","slug":"...","focus_keyword":"...","tags":["..."],"content_html":"..."}}
"""
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "temperature": 0.7,
              "response_format": {"type": "json_object"},
              "messages": [{"role": "system", "content": system_prompt},
                           {"role": "user", "content": user_prompt}]},
        timeout=120,
    )
    response.raise_for_status()
    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("OpenAI returned an unexpected response format.")
    article = _extract_json(content)
    required = ("title", "meta_description", "slug", "focus_keyword", "content_html")
    missing = [key for key in required if not isinstance(article.get(key), str) or not article[key].strip()]
    if missing:
        raise RuntimeError("Generated article is missing fields: " + ", ".join(missing))
    if not isinstance(article.get("tags", []), list):
        article["tags"] = []
    count = word_count(article["content_html"])
    article["word_count"] = count
    if count < min_words:
        raise RuntimeError(f"Article quality check failed: {count} words; minimum is {min_words}. No draft was created.")
    if len(article["meta_description"]) < 140 or len(article["meta_description"]) > 170:
        print("Warning: meta description is outside the preferred 150-160 character range.")
    return article
