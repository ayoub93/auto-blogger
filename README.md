# Auto Blogger

## Current status
This repository currently contains a Blogger API connection test, not the completed automatic article publisher. The workflow is manual-only so it does not repeatedly run an incomplete publisher.

## Setup / الإعداد
1. Enable Blogger API v3 in Google Cloud and create OAuth credentials.
2. Add these repository secrets in **Settings → Secrets and variables → Actions**: `BLOGGER_BLOG_ID`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REFRESH_TOKEN`.
3. Open **Actions → Auto Blogger - Connection Test → Run workflow** to test access.

## العربية
المشروع حاليًا يختبر الاتصال بـ Blogger فقط، ولم يكتمل بعد إنشاء المقالات والنشر التلقائي. أضف الأسرار الأربعة في إعدادات المستودع، ثم شغّل اختبار الاتصال يدويًا من تبويب Actions. لا تضع المفاتيح الحقيقية في ملفات المشروع أو الرسائل العامة.

The current workflow does not publish posts. OpenAI article generation and the hourly publishing workflow still need to be implemented and tested before enabling automation.
