# AI Blogger Agent

A Python-based AI editorial agent for Blogger. It discovers topics, drafts SEO-aware articles, optionally finds an attributed Unsplash image, checks minimum length and duplicate history, then saves each article to **Blogger Drafts** for a human to review.

> **Safety policy:** this repository intentionally creates drafts only. It does not publish posts automatically and contains no publish/approve command. Review and publish manually from Blogger.

## Features

- Google Trends RSS topic discovery with configurable region and fallback topics.
- Original article generation using OpenAI `gpt-4o-mini`.
- SEO title, meta description, slug, focus keyword and labels.
- HTML word-count gate (800 words by default); failed checks do not create a Blogger draft.
- Optional Unsplash image search with contributor attribution.
- Duplicate topic/title history in `used_titles.json`.
- Review queue in `pending_review.json` and downloadable HTML preview artifact.
- Hourly GitHub Actions schedule plus manual workflow dispatch.

## GitHub Actions setup

In **Settings → Secrets and variables → Actions**, create:

| Secret | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `BLOGGER_BLOG_ID` | Yes | Numeric Blogger blog ID |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
| `GOOGLE_REFRESH_TOKEN` | Yes | OAuth refresh token with Blogger scope |
| `UNSPLASH_ACCESS_KEY` | No | Unsplash API access key for featured images |

Never commit real keys, OAuth tokens, or credential JSON to the repository.

### Google OAuth requirements

1. Enable Blogger API v3 in Google Cloud.
2. Configure an OAuth consent screen and create an OAuth client.
3. Obtain a refresh token with scope `https://www.googleapis.com/auth/blogger`.
4. Add the four Blogger-related values as GitHub Actions secrets.

The OAuth account must have permission to edit the target blog. If the refresh token is revoked or lacks the Blogger scope, the workflow will fail before creating a draft.

## Run

- Automatic: GitHub Actions runs hourly at minute 0 (UTC).
- Manual: **Actions → AI Blogger Agent → Run workflow**.
- Open **Blogger → Posts → Drafts** to review, edit, and publish approved articles.
- The workflow uploads an HTML preview artifact named `blogger-agent-preview`.

The workflow needs repository **Contents: Read and write** permission to persist duplicate history and the review queue. If organization policy blocks write access for GitHub Actions, enable it in repository Settings → Actions → General → Workflow permissions.

## Local development

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set the environment variables listed above, then run:

```bash
python main.py --dry-run
python -m unittest discover -s tests -v
```

A dry run generates a local HTML preview and does not call Blogger. A normal run creates a Blogger draft.

## Configuration

The workflow defaults to English, US Trends, and 800 minimum article words. Adjust `ARTICLE_LANGUAGE`, `TRENDS_GEO`, and `MIN_ARTICLE_WORDS` in the workflow file. Add comma-separated fallback topics in `FALLBACK_TOPICS` if desired.

## Limitations and editorial responsibility

- Google Trends is a discovery signal, not proof that a topic is accurate or suitable.
- Fact-check and edit the article before publishing.
- Unsplash images are optional; without an API key or a match, the draft is created without an image.
- Search Console analytics, a web dashboard, automatic content refresh, and autonomous source verification are not included in this initial implementation.
- Real API operation remains unverified until secrets are configured and a GitHub Actions run succeeds.

## العربية

هذا المشروع وكيل ذكي لإعداد المقالات على Blogger. يجمع موضوعات رائجة من Google Trends، وينشئ مقالًا باستخدام OpenAI، ويفحص الحد الأدنى لعدد الكلمات وتكرار الموضوع، ويبحث اختياريًا عن صورة من Unsplash مع نسبها لصاحبها.

**سياسة النشر:** الوكيل يحفظ المقالات كمسودات فقط. لن ينشر المقال تلقائيًا. راجع المسودة من Blogger ← المشاركات ← المسودات، ثم عدّلها وانشرها بنفسك بعد الموافقة.

### إعداد الأسرار

أضف الأسرار المطلوبة في GitHub: `OPENAI_API_KEY` و`BLOGGER_BLOG_ID` و`GOOGLE_CLIENT_ID` و`GOOGLE_CLIENT_SECRET` و`GOOGLE_REFRESH_TOKEN`. مفتاح Unsplash اختياري. لا تضع أي مفاتيح أو رموز OAuth داخل ملفات المشروع.

يحتاج GitHub Actions إلى صلاحية **Contents: Read and write** لحفظ سجل الموضوعات وطابور المراجعة. شغّل سير العمل يدويًا أول مرة، وتأكد من نجاحه قبل الاعتماد على التشغيل المجدول كل ساعة.

### ما لم يكتمل بعد

التحليلات من Search Console، ولوحة تحكم ويب، وتحديث المقالات القديمة، والتحقق الآلي المستقل من المصادر ليست ضمن هذه المرحلة. يجب مراجعة المعلومات والمصادر يدويًا قبل النشر.
