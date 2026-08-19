# Gold & Forex News Bot

> بيعيش جوه ريبو PyAutoPytest، بس مستقل تمامًا عن إطار الاختبارات:
> الكود كله في `gold_news_bot/` والتشغيل من `.github/workflows/news-bot.yml`.

بوت تيليجرام بيقرأ 5 مصادر RSS (Investing ×2، FXStreet، Kitco، Reuters عن طريق Google News)،
بيفلتر الأخبار اللي فيها **ذهب / الفيدرالي / تضخم / NFP**، وبيبعتها على تيليجرام **من غير تكرار**.
بيشتغل مجانًا على GitHub Actions كل 15 دقيقة — من غير سيرفر.

---

## التشغيل في 4 خطوات

### 1) اعمل البوت وهات الـ IDs
- كلّم [@BotFather](https://t.me/BotFather) → `/newbot` → هيديك الـ **token**.
- كلّم [@userinfobot](https://t.me/userinfobot) → هيديك الـ **chat_id** بتاعك.
- ابعت أي رسالة للبوت بتاعك مرة واحدة (`/start`)، عشان تيليجرام مايسمحش للبوت يبدأ محادثة لوحده.

### 2) حط القيم في Secrets
في الريبو ده: **Settings → Secrets and variables → Actions → New repository secret**

| الاسم | القيمة |
|---|---|
| `TELEGRAM_BOT_TOKEN` | التوكن من BotFather |
| `TELEGRAM_CHAT_ID` | الرقم من userinfobot |

> ⚠️ متحطش التوكن في أي ملف داخل الريبو. لو التوكن اتسرب في أي وقت، افتح BotFather → `/revoke` واعمل واحد جديد.

### 3) فعّل الـ Actions
افتح تاب **Actions** ووافق على تشغيل الـ workflows. بعدها اختار **News Bot → Run workflow** عشان تجرّب فورًا
(في خيار `dry_run` لو عايز تشوف الأخبار في اللوج من غير ما تتبعت على تيليجرام).

### 4) خلاص
الـ cron بيشتغل كل 15 دقيقة لوحده: `.github/workflows/news-bot.yml`

---

## تشغيل محلي (للتجربة)

```bash
pip install -r gold_news_bot/requirements.txt

# معاينة من غير إرسال
python gold_news_bot/bot.py --dry-run

# إرسال فعلي
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
python gold_news_bot/bot.py
```

## الاختبارات

```bash
pip install -r gold_news_bot/requirements.txt pytest
pytest gold_news_bot/tests
```

---

## التعديل على المصادر والكلمات

كل حاجة في `gold_news_bot/feeds.yml` — مش محتاج تفتح الكود:

```yaml
feeds:
  - name: "Investing – Commodities"
    url: "https://www.investing.com/rss/news_11.rss"

keywords:
  - gold
  - inflation
  - ذهب
```

الكلمات بتتقارن على **العنوان + الملخص** و case-insensitive، وبتقبل عربي وإنجليزي.
لو مصدر وقع أو غيّر رابطه، البوت بيسيبه ويكمّل باقي المصادر وبيكتب warning في اللوج
(شوفها في Actions → آخر run) — عدّل الرابط في `feeds.yml` وخلاص.

## الإعدادات (environment variables)

| المتغير | الافتراضي | المعنى |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | — | مطلوب |
| `TELEGRAM_CHAT_ID` | — | مطلوب |
| `MAX_AGE_HOURS` | `6` | تجاهل أي خبر أقدم من كده |
| `MAX_ITEMS_PER_RUN` | `10` | أقصى عدد رسايل في التشغيلة الواحدة (حماية من الفيضان) |
| `STATE_TTL_DAYS` | `7` | مدة تذكّر الخبر عشان مايتبعتش تاني |
| `FEEDS_FILE` | `gold_news_bot/feeds.yml` | مسار ملف المصادر |
| `STATE_FILE` | `state/seen.json` (من الـ workflow) | مسار ملف الحالة |

## إزاي بيمنع التكرار

- لكل خبر بصمة (SHA-256) من الـ guid بتاع الـ feed، أو من اللينك بعد تنضيف باراميترات التتبّع (`utm_*` وغيرها) —
  فنفس الخبر من مصدرين بيتبعت مرة واحدة.
- البصمات بتتخزن في `state/seen.json`، والملف ده بيتحفظ في **cache** بتاع GitHub Actions بين التشغيلات
  (`actions/cache` — مفتاح جديد كل run لأن مفاتيح الكاش immutable).
- لو الكاش ضاع لأي سبب، فلتر `MAX_AGE_HOURS` + `MAX_ITEMS_PER_RUN` بيمنع إن البوت يبعتلك تاريخ الـ feed كله.
- الخبر مابيتسجّلش كـ "مبعوت" غير لما تيليجرام يقبله فعلًا، فلو الشبكة وقعت بيتبعت في الـ run اللي بعده.

## ملاحظات

- كرون GitHub Actions **best-effort**: ممكن يتأخر شوية في أوقات الزحمة، وده طبيعي ومش مشكلة في الكود.
- GitHub بيوقف الـ scheduled workflows تلقائيًا لو الريبو قعد **60 يوم من غير أي نشاط** — أي commit بيرجّعها.
- المجاني بتاع GitHub Actions: الريبو العام مجاني بالكامل. لو خليته private، كل run بياخد أقل من دقيقة.
