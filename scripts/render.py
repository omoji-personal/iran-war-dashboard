"""Render the predictive-agent homepage from portfolio.yaml + memory + logs.

Produces production-grade HTML using the editorial-brief aesthetic:
- Iowan Old Style / Palatino serif for headlines + body
- Inter sans for UI metadata
- Dark navy (#0b1322) + cream (#ecdfd0) + rust (#d97757) palette
- 1480px max-width, 2-col body, responsive

Usage:
    python3 scripts/render.py            # renders index.html
    python3 scripts/render.py --public   # also renders public.html (stripped)
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = REPO_ROOT / "portfolio.yaml"
MEMORY_PATH = REPO_ROOT / "agent" / "memory.md"
QUEUE_PATH = REPO_ROOT / "agent" / "operator-queue.md"
HISTORY_PATH = REPO_ROOT / "portfolio_history.json"
SOURCES_SHIFTED_DIR = REPO_ROOT / "logs" / "sources-shifted"
EVENTS_DIR = REPO_ROOT / "logs" / "events"
OUTPUT_INDEX = REPO_ROOT / "index.html"
OUTPUT_INDEX_FA = REPO_ROOT / "fa.html"
OUTPUT_PUBLIC = REPO_ROOT / "public.html"
OUTPUT_PUBLIC_FA = REPO_ROOT / "public.fa.html"

LANGS = ("en", "fa")

# Visitor-facing chrome strings — section labels, button text, etc.
# Question content (question text + notes) lives in portfolio.yaml; it stays
# English for now and will pick up `_fa` overrides when those are filled in.
STRINGS = {
    "en": {
        "site_eyebrow": "2026 Iran-US Conflict",
        "site_title": "Predictive Agent",
        "topbar_next_label": "Next:",
        "topbar_next_value": "Daily 07:00 ET update",
        "lang_toggle_to_fa": "فارسی",
        "lang_toggle_to_en": "English",
        "masthead_classification": "For analytic reading · Probability brief, not advice",
        "masthead_publisher": "2026 IRAN-US CONFLICT MONITOR",
        "masthead_subline": "Daily 07:00 ET update",
        "masthead_issue_prefix": "Issue",
        "issue_day": "Day",
        "translation_in_progress_notice": "",
        "banner_strong": "EXPERIMENTAL — UNCALIBRATED",
        "banner_text": "None of these questions has resolved yet, so the probabilities have no track record. Treat them as structured scenario reasoning, not as forecasts.",
        "banner_legacy_link": "Older dashboard",
        "headline_eyebrow_today": "Today's read",
        "headline_eyebrow_tagline": "interpretation, not forecast",
        "headline_lead_template": "{day_phrase} of the 2026 Iran-US conflict. The questions below are scored from a daily reading of public news and prediction-market prices. None have resolved yet, so the probabilities have no track record — treat them as structured guesses, not predictions.",
        "headline_body_intro": "The three highest-stakes questions to watch right now",
        "headline_body_outro_full": "The PERSONAL-tagged questions track family-business consequences — Iranfarhang (Persian-content distribution to US/UK universities) and Kipa (specialty-chemicals importer into Iran). Each card below shows the current probability, the 80% range it's likely to fall in, and a one-line rationale. Updated each morning.",
        "headline_body_outro_public": "Each card below shows the current probability, the 80% range it's likely to fall in, and a one-line rationale. The list is grouped by topic and updated each morning.",
        "frame_eyebrow": "Why this page exists",
        "frame_map_label": "How the questions map",
        "basecase_eyebrow": "The most likely path forward",
        "basecase_eyebrow_revised": "last revised",
        "basecase_h": "What's most likely to keep being true",
        "basecase_foot": "Each topic below leads with the questions sitting closest to this base case, then shows the lower-probability scenarios that would break it.",
        "diff_h": "What changed since the last update",
        "diff_first_msg": "First update — no prior day to compare against. From tomorrow on, this panel will list only the probabilities that moved more than the question's own uncertainty range. Quiet days will say so.",
        "diff_quiet_msg_template": "No probability moves on the question cards since {date}. The \"What's most likely to keep being true\" section above has the freshest read on the situation; the card values update when the questions are formally revised.",
        "topq_eyebrow": "Today's top question",
        "topq_link": "Read full evidence chain ↓",
        "topq_delta_suffix": "since last update",
        "topq_ci_label": "80% CI:",
        "qcard_ci_label": "80% CI:",
        "qcard_flag_humility": "HUMILITY",
        "qcard_flag_humility_title": "This kind of event is historically very hard to forecast — treat the number as a placeholder, read the rationale instead",
        "qcard_flag_personal": "PERSONAL",
        "qcard_flag_personal_title": "Directly affects family business",
        "board_h_template": "Question portfolio · {n} questions",
        "board_sub": "Within each topic, most-likely outcomes lead; lower-probability scenarios to watch follow under the divider. Each card shows the current probability and the 80% range it's likely to fall in.",
        "cluster_likely_h": "Most-likely outcomes",
        "cluster_tail_h": "Lower-probability scenarios to watch",
        "cat_count_template": "{n} questions",
        "method_h": "What to keep in mind",
        "method_b1": "<strong>The \"most-likely scenario\" paragraph above is the anchor.</strong> It's the single future getting the most probability mass once you average across the questions. The questions below — especially the ones in the \"lower-probability\" cluster of each topic — are the named ways that base case could break. Most of those tail-risk cards will read low for a reason.",
        "method_b2": "<strong>Experimental — no track record yet.</strong> None of these questions has resolved, so the probabilities haven't been graded against reality. Treat them as structured guesses.",
        "method_b3": "<strong>Two questions are intentionally fuzzy</strong> — anything tied to whether a leader is alive, ill, or being succeeded (Khamenei, Mojtaba). Forecasting models historically fail at these. The number is a placeholder; the rationale is what to read.",
        "method_b4": "<strong>How probabilities move</strong>: each morning, public news and prediction-market prices are re-read. If something shifts a question by more than its 80% range, it shows up at the top in \"What changed since the last update.\"",
        "method_b5": "<strong>What this is not.</strong> It is not financial or political advice. No one is being told to act on these numbers. Probabilities are scenario weighing, not forecasts.",
        "footer_brand": "2026 IRAN-US CONFLICT PREDICTIVE AGENT",
        "footer_meta": "Daily structured scenario analysis · experimental · no track record yet",
        "footer_legacy_link": "Older dashboard",
        "category_diplomatic_resolution": "Diplomatic resolution",
        "category_military_escalation": "Military escalation",
        "category_regime_leadership": "Regime / leadership",
        "category_economic_structural": "Economic / structural",
        "category_us_side": "US side",
        "category_family_business_iranfarhang": "Iranfarhang business",
        "category_family_business_kipa": "Kipa business",
        "category_num_diplomatic_resolution": "§ A",
        "category_num_military_escalation": "§ B",
        "category_num_regime_leadership": "§ C",
        "category_num_economic_structural": "§ D",
        "category_num_us_side": "§ E",
        "category_num_family_business_iranfarhang": "§ F.1",
        "category_num_family_business_kipa": "§ F.2",
        "icd_vanishing": "vanishing",
        "icd_almost_no_chance": "almost no chance",
        "icd_very_unlikely": "very unlikely",
        "icd_unlikely": "unlikely",
        "icd_roughly_even_chance": "roughly even chance",
        "icd_likely": "likely",
        "icd_very_likely": "very likely",
        "icd_almost_certain": "almost certain",
        "icd_near_certain": "near certain",
    },
    "fa": {
        "site_eyebrow": "نزاع ایران و آمریکا ۲۰۲۶",
        "site_title": "تحلیل‌گر پیش‌بینی",
        "topbar_next_label": "بعدی:",
        "topbar_next_value": "به‌روزرسانی هر روز ساعت ۷:۰۰ شرق آمریکا",
        "lang_toggle_to_fa": "فارسی",
        "lang_toggle_to_en": "English",
        "masthead_classification": "برای مطالعه‌ی تحلیلی · گزارش احتمالات، نه توصیه",
        "masthead_publisher": "ناظر نزاع ایران و آمریکا ۲۰۲۶",
        "masthead_subline": "به‌روزرسانی هر روز ساعت ۷:۰۰ شرق آمریکا",
        "masthead_issue_prefix": "شماره",
        "issue_day": "روز",
        "translation_in_progress_notice": "متن پرسش‌ها در حال حاضر به انگلیسی نمایش داده می‌شود. ترجمه‌ی پرسش به پرسش در حال تکمیل است.",
        "banner_strong": "آزمایشی — کالیبره‌نشده",
        "banner_text": "هیچ‌یک از این پرسش‌ها هنوز قطعی نشده‌اند، پس احتمالات سابقه‌ی عملکردی ندارند. آن‌ها را به عنوان استدلال ساخت‌یافته‌ی سناریو در نظر بگیرید، نه پیش‌بینی.",
        "banner_legacy_link": "داشبورد قدیمی",
        "headline_eyebrow_today": "خوانش امروز",
        "headline_eyebrow_tagline": "تفسیر، نه پیش‌بینی",
        "headline_lead_template": "{day_phrase} از نزاع ایران و آمریکا ۲۰۲۶. پرسش‌های پایین بر پایه‌ی خوانش روزانه‌ی اخبار عمومی و قیمت بازارهای پیش‌بینی نمره‌گذاری شده‌اند. هیچ‌یک هنوز قطعی نشده‌اند، پس احتمالات سابقه‌ی عملکردی ندارند — آن‌ها را گمانه‌های ساخت‌یافته بدانید، نه پیش‌بینی.",
        "headline_body_intro": "سه پرسش با بیشترین اهمیت برای رصد در حال حاضر",
        "headline_body_outro_full": "پرسش‌های با برچسب «شخصی» پیامدهای کسب‌وکار خانوادگی را دنبال می‌کنند — ایران‌فرهنگ (توزیع محتوای فارسی به دانشگاه‌های آمریکا و بریتانیا) و کیپا (وارد‌کننده‌ی مواد شیمیایی تخصصی به ایران). هر کارت پایین احتمال جاری، بازه‌ی ۸۰٪ احتمالی و یک خط استدلال را نشان می‌دهد. هر صبح به‌روزرسانی می‌شود.",
        "headline_body_outro_public": "هر کارت پایین احتمال جاری، بازه‌ی ۸۰٪ احتمالی و یک خط استدلال را نشان می‌دهد. فهرست بر اساس موضوع گروه‌بندی شده و هر صبح به‌روزرسانی می‌شود.",
        "frame_eyebrow": "چرا این صفحه وجود دارد",
        "frame_map_label": "نگاشت پرسش‌ها",
        "basecase_eyebrow": "محتمل‌ترین مسیر پیش‌رو",
        "basecase_eyebrow_revised": "آخرین بازنگری",
        "basecase_h": "چه چیزی به‌احتمال زیاد همچنان درست خواهد بود",
        "basecase_foot": "هر موضوع پایین با پرسش‌هایی که به این خط پایه نزدیک‌ترند آغاز می‌شود، سپس سناریوهای کم‌احتمال‌تری را که می‌توانند آن را بشکنند نشان می‌دهد.",
        "diff_h": "چه تغییری از آخرین به‌روزرسانی رخ داد",
        "diff_first_msg": "اولین به‌روزرسانی — هنوز روز قبلی برای مقایسه وجود ندارد. از فردا، این بخش فقط احتمالاتی را که بیش از بازه‌ی عدم‌قطعیت خود تغییر کرده‌اند نشان خواهد داد. روزهای آرام نیز اعلام می‌شوند.",
        "diff_quiet_msg_template": "هیچ تغییر احتمالی روی کارت‌های پرسش از زمان {date} رخ نداده است. بخش «چه چیزی به‌احتمال زیاد همچنان درست خواهد بود» در بالا تازه‌ترین خوانش وضعیت را دارد؛ مقادیر کارت‌ها در زمان بازنگری رسمی پرسش‌ها به‌روز می‌شود.",
        "topq_eyebrow": "پرسش امروز",
        "topq_link": "خواندن زنجیره‌ی کامل شواهد ↓",
        "topq_delta_suffix": "از آخرین به‌روزرسانی",
        "topq_ci_label": "بازه‌ی ۸۰٪:",
        "qcard_ci_label": "بازه‌ی ۸۰٪:",
        "qcard_flag_humility": "فروتنی",
        "qcard_flag_humility_title": "این نوع رویداد از نظر تاریخی بسیار سخت‌قابل‌پیش‌بینی است — عدد را به‌عنوان یک جای‌نشان در نظر بگیرید و به استدلال نگاه کنید",
        "qcard_flag_personal": "شخصی",
        "qcard_flag_personal_title": "مستقیماً بر کسب‌وکار خانوادگی اثر می‌گذارد",
        "board_h_template": "مجموعه‌ی پرسش‌ها · {n} پرسش",
        "board_sub": "در هر موضوع، محتمل‌ترین نتایج ابتدا می‌آیند؛ سناریوهای کم‌احتمال‌تر زیر خط جداکننده. هر کارت احتمال جاری و بازه‌ی ۸۰٪ احتمالی را نشان می‌دهد.",
        "cluster_likely_h": "محتمل‌ترین نتایج",
        "cluster_tail_h": "سناریوهای کم‌احتمال‌تر برای رصد",
        "cat_count_template": "{n} پرسش",
        "method_h": "آنچه باید در نظر داشت",
        "method_b1": "<strong>پاراگراف «محتمل‌ترین سناریو» در بالا، لنگرگاه است.</strong> این تنها آینده‌ای است که پس از میانگین‌گیری بین پرسش‌ها، بیشترین وزن احتمالی را دریافت می‌کند. پرسش‌های پایین — به‌ویژه آن‌هایی که در خوشه‌ی «کم‌احتمال‌تر» هر موضوع قرار می‌گیرند — راه‌های نامبرده‌ای هستند که این خط پایه می‌تواند بشکند. اکثر آن کارت‌های ریسک دم به دلیلی پایین خوانده می‌شوند.",
        "method_b2": "<strong>آزمایشی — بدون سابقه.</strong> هیچ‌یک از این پرسش‌ها قطعی نشده، پس احتمالات نسبت به واقعیت نمره‌گذاری نشده‌اند. آن‌ها را گمانه‌های ساخت‌یافته بدانید.",
        "method_b3": "<strong>دو پرسش به‌عمد مبهم‌اند</strong> — هر چیزی مرتبط با زنده‌بودن، بیماری یا جانشینی یک رهبر (خامنه‌ای، مجتبی). مدل‌های پیش‌بینی از نظر تاریخی در این موارد ناکام می‌مانند. عدد جای‌نشان است؛ آنچه باید بخوانید استدلال است.",
        "method_b4": "<strong>چگونه احتمالات حرکت می‌کنند</strong>: هر صبح، اخبار عمومی و قیمت بازارهای پیش‌بینی دوباره خوانده می‌شود. اگر چیزی پرسشی را بیش از بازه‌ی ۸۰٪ آن جابه‌جا کند، در بالا در «چه تغییری از آخرین به‌روزرسانی رخ داد» نمایش داده می‌شود.",
        "method_b5": "<strong>این چه نیست.</strong> این مشاوره‌ی مالی یا سیاسی نیست. به هیچ‌کس گفته نمی‌شود بر اساس این اعداد عمل کند. احتمالات وزن‌دهی سناریو هستند، نه پیش‌بینی.",
        "footer_brand": "تحلیل‌گر پیش‌بینی نزاع ایران و آمریکا ۲۰۲۶",
        "footer_meta": "تحلیل سناریوی ساخت‌یافته‌ی روزانه · آزمایشی · بدون سابقه",
        "footer_legacy_link": "داشبورد قدیمی",
        "category_diplomatic_resolution": "حل دیپلماتیک",
        "category_military_escalation": "تشدید نظامی",
        "category_regime_leadership": "نظام / رهبری",
        "category_economic_structural": "اقتصادی / ساختاری",
        "category_us_side": "سمت آمریکا",
        "category_family_business_iranfarhang": "کسب‌وکار ایران‌فرهنگ",
        "category_family_business_kipa": "کسب‌وکار کیپا",
        "category_num_diplomatic_resolution": "بخش الف",
        "category_num_military_escalation": "بخش ب",
        "category_num_regime_leadership": "بخش ج",
        "category_num_economic_structural": "بخش د",
        "category_num_us_side": "بخش ه",
        "category_num_family_business_iranfarhang": "بخش و-۱",
        "category_num_family_business_kipa": "بخش و-۲",
        "icd_vanishing": "ناچیز",
        "icd_almost_no_chance": "تقریباً بی‌شانس",
        "icd_very_unlikely": "بسیار بعید",
        "icd_unlikely": "بعید",
        "icd_roughly_even_chance": "تقریباً مساوی",
        "icd_likely": "محتمل",
        "icd_very_likely": "بسیار محتمل",
        "icd_almost_certain": "تقریباً قطعی",
        "icd_near_certain": "نزدیک به قطعی",
    },
}


def _t(key: str, lang: str) -> str:
    """Translate a chrome string. Falls back to English if Persian missing."""
    return STRINGS.get(lang, {}).get(key) or STRINGS["en"].get(key, key)

# Hardcoded reference date for "war Day N" computation. D1 of conflict = 2026-02-28.
WAR_D1_ISO = "2026-02-28"
# Cease-fire start: 2026-04-07 (Day 39)
CEASEFIRE_START_ISO = "2026-04-07"
# Hormuz blockade start: 2026-04-15 (Day 47, est.)
BLOCKADE_START_ISO = "2026-04-15"


ICD203_BUCKETS = [
    (0.00, 0.01, "vanishing", "<1%"),
    (0.01, 0.05, "almost no chance", "1-5%"),
    (0.05, 0.20, "very unlikely", "5-20%"),
    (0.20, 0.45, "unlikely", "20-45%"),
    (0.45, 0.55, "roughly even chance", "45-55%"),
    (0.55, 0.80, "likely", "55-80%"),
    (0.80, 0.95, "very likely", "80-95%"),
    (0.95, 0.99, "almost certain", "95-99%"),
    (0.99, 1.001, "near certain", ">99%"),
]


def icd203(p: float, lang: str = "en") -> tuple[str, str, str]:
    """Returns (label, range_str, css_class). Label is translated via STRINGS."""
    p = max(0.0, min(1.0, p))
    for lo, hi, label_en, range_str in ICD203_BUCKETS:
        if lo <= p < hi:
            css = label_en.replace(" ", "-")
            label = _t("icd_" + label_en.replace(" ", "_"), lang)
            return label, range_str, css
    # p == exactly 1.0 hits the last bucket
    return _t("icd_near_certain", lang), ">99%", "near-certain"


# Mapping of category id → CSS class. The numeric label and human-readable
# title are looked up via STRINGS so they translate correctly per language.
CATEGORY_CSS = {
    "diplomatic_resolution": "cat-diplomacy",
    "military_escalation": "cat-military",
    "regime_leadership": "cat-regime",
    "economic_structural": "cat-economic",
    "us_side": "cat-us",
    "family_business_iranfarhang": "cat-iranfarhang",
    "family_business_kipa": "cat-kipa",
}
# Display order — public categories first, family-business last
CATEGORY_ORDER = list(CATEGORY_CSS.keys())


def category_label(cat_id: str, lang: str) -> tuple[str, str, str]:
    """Returns (numbering, title, css_class) for a category in the given language."""
    num = _t(f"category_num_{cat_id}", lang)
    title = _t(f"category_{cat_id}", lang)
    css = CATEGORY_CSS.get(cat_id, "cat-default")
    return num, title, css


def load_portfolio() -> dict:
    return yaml.safe_load(PORTFOLIO_PATH.read_text(encoding="utf-8"))


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _is_v02_snapshot(h: dict) -> bool:
    """v0.1 history entries (legacy engine) lack a `questions[]` array; they
    have keys like `scores`, `outcomeProbabilities`, `resolutionProbability`.
    Treating those as a v0.2 baseline produces silently-empty diffs that
    misleadingly read as 'no probability moves' instead of 'no comparable
    baseline'. Only consider snapshots that carry a v0.2 questions[] array."""
    qs = h.get("questions")
    return isinstance(qs, list) and len(qs) > 0


def compute_diffs_vs_yesterday(portfolio: dict, history: list[dict]) -> list[dict]:
    """Compare today's portfolio against the most recent snapshot whose date is
    BEFORE today. Avoids the today-vs-today degenerate-zero-diff bug."""
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    if not prior:
        return []
    last = prior[-1]
    last_qs = {q.get("id"): q for q in last.get("questions", [])}
    diffs = []
    for q in portfolio["questions"]:
        qid = q["id"]
        cur_p = q["current_probability"]
        last_q = last_qs.get(qid, {})
        last_p = last_q.get("probability", cur_p)
        delta = cur_p - last_p
        ci = q.get("current_credible_interval_80", [cur_p, cur_p])
        ci_halfwidth = (ci[1] - ci[0]) / 2.0
        # CI-aware noise suppression: only headline diffs > question's CI half-width
        if abs(delta) > ci_halfwidth and ci_halfwidth > 0:
            diffs.append({
                "id": qid,
                "question": q["question"],
                "old_p": last_p,
                "new_p": cur_p,
                "delta_pp": delta * 100,
            })
    return diffs


def war_day(today: datetime) -> int:
    """Days since 2026-02-28 (D1). Returns int >= 1."""
    d1 = datetime.fromisoformat(WAR_D1_ISO).replace(tzinfo=timezone.utc)
    return max(1, (today.date() - d1.date()).days + 1)


def cf_day(today: datetime) -> int:
    """Days since cease-fire start (2026-04-07). Returns 0 if before."""
    cf1 = datetime.fromisoformat(CEASEFIRE_START_ISO).replace(tzinfo=timezone.utc)
    delta = today.date() - cf1.date()
    return max(0, delta.days + 1) if delta.days >= 0 else 0


def blockade_day(today: datetime) -> int:
    """Days since Hormuz blockade start. 0 if before."""
    bs = datetime.fromisoformat(BLOCKADE_START_ISO).replace(tzinfo=timezone.utc)
    delta = today.date() - bs.date()
    return max(0, delta.days + 1) if delta.days >= 0 else 0


def esc(s: str) -> str:
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;")
                  .replace("<", "&lt;")
                  .replace(">", "&gt;")
                  .replace('"', "&quot;"))


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")


def first_sentence(text: str) -> str:
    """Return the first complete sentence (terminating punctuation included).
    Falls back to first line if no sentence boundary found."""
    if not text:
        return ""
    cleaned = " ".join(line.strip() for line in text.strip().splitlines() if line.strip())
    parts = _SENTENCE_SPLIT.split(cleaned, maxsplit=1)
    candidate = parts[0].strip()
    if not candidate:
        return ""
    # Cap at 220 chars even if no sentence boundary
    if len(candidate) > 220:
        candidate = candidate[:217].rstrip() + "…"
    return candidate


def _q_field(q: dict, key: str, lang: str) -> str:
    """Return the language-specific question field if present, else fall back to English.
    Looks up `{key}_fa` for Persian; uses `{key}` for English / fallback."""
    if lang == "fa":
        v = q.get(f"{key}_fa")
        if v:
            return str(v)
    return str(q.get(key, "") or "")


def render_question_card(q: dict, stripped: bool = False, lang: str = "en") -> str:
    p = q["current_probability"]
    label, range_str, label_css = icd203(p, lang=lang)
    ci = q["current_credible_interval_80"]
    humility = q.get("humility_flag", False)
    notes = first_sentence(_q_field(q, "notes", lang))
    deadline = q["deadline"]

    _, _, cat_css = category_label(q["category"], lang)

    pct = round(p * 100)
    ci_lo = round(ci[0] * 100)
    ci_hi = round(ci[1] * 100)

    flags = []
    if humility:
        flags.append(
            f'<span class="card-flag flag-humility" title="{esc(_t("qcard_flag_humility_title", lang))}">'
            f'{esc(_t("qcard_flag_humility", lang))}</span>'
        )
    # PERSONAL flag is operator-private — never shown on the stripped public deploy
    if not stripped:
        for tag in q.get("stakeholder_tags", []):
            if tag == "omid_personal":
                flags.append(
                    f'<span class="card-flag flag-personal" title="{esc(_t("qcard_flag_personal_title", lang))}">'
                    f'{esc(_t("qcard_flag_personal", lang))}</span>'
                )
                break

    # `dir="auto"` on user-content blocks so an English question on a Persian
    # page renders LTR without breaking the surrounding RTL chrome.
    # CI-label split: only the numeric range gets <bdi dir="ltr"> isolation.
    # The Persian "بازه‌ی ۸۰٪:" label stays in the document direction so the
    # colon attaches to the right side of the Persian chars (correct flow).
    ci_label_text = _t('qcard_ci_label', lang)
    ci_range = f'<bdi dir="ltr">{ci_lo}–{ci_hi}%</bdi>'
    return f"""
      <article class="qcard qcard-{cat_css} qcard-prob-{label_css}" id="q-{q['id']}">
        <header class="qcard-head">
          <span class="qcard-id">{esc(q['id'])}</span>
          <bdi class="qcard-deadline" dir="ltr">→ {esc(deadline)}</bdi>
          <span class="qcard-flags">{''.join(flags)}</span>
        </header>
        <h3 class="qcard-question" dir="auto">{esc(_q_field(q, 'question', lang))}</h3>
        <div class="qcard-numbers">
          <div class="qcard-prob">
            <span class="qcard-prob-num">{pct}<span class="qcard-prob-pct">%</span></span>
            <span class="qcard-prob-label">{esc(label)}</span>
          </div>
          <div class="qcard-ci">
            <span class="qcard-ci-bar" aria-label="{esc(ci_label_text)} {ci_lo}–{ci_hi}%">
              <span class="qcard-ci-track"></span>
              <span class="qcard-ci-fill" style="left: {ci_lo}%; width: {ci_hi - ci_lo}%"></span>
              <span class="qcard-ci-mark" style="left: {pct}%"></span>
            </span>
            <span class="qcard-ci-label">{esc(ci_label_text)} {ci_range}</span>
          </div>
        </div>
        <p class="qcard-note" dir="auto">{esc(notes)}</p>
      </article>
    """


_FA_MONTHS = ("ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
              "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر")
_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def _to_fa_digits(s: str) -> str:
    """Convert ASCII digits in a string to Persian (Farsi) digits."""
    return s.translate(_FA_DIGITS)


def _human_date(iso_date: str, lang: str = "en") -> str:
    """Render YYYY-MM-DD as a short human date in the chosen language.
    English: 'May 3'. Persian: '۳ مه'. Falls back to original on parse error."""
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return iso_date
    if lang == "fa":
        return f"{_to_fa_digits(str(d.day))} {_FA_MONTHS[d.month - 1]}"
    return d.strftime("%b %d").replace(" 0", " ")


def render_diff_panel(diffs: list[dict], history: list[dict], lang: str = "en") -> str:
    today_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    has_prior_baseline = bool(prior)
    diff_h = _t("diff_h", lang)

    if not has_prior_baseline:
        return f"""
        <section class="diff-panel diff-empty" role="region" aria-label="{esc(diff_h)}">
          <h2 class="diff-h">{esc(diff_h)}</h2>
          <p class="diff-empty-msg">{esc(_t("diff_first_msg", lang))}</p>
        </section>
        """
    if not diffs:
        last_date = _human_date(prior[-1]["date"], lang=lang)
        msg = _t("diff_quiet_msg_template", lang).format(date=last_date)
        return f"""
        <section class="diff-panel diff-empty" role="region" aria-label="{esc(diff_h)}">
          <h2 class="diff-h">{esc(diff_h)}</h2>
          <p class="diff-empty-msg">{esc(msg)}</p>
        </section>
        """
    items = []
    for d in diffs:
        arrow = "▲" if d["delta_pp"] > 0 else "▼"
        css_dir = "diff-up" if d["delta_pp"] > 0 else "diff-down"
        # Wrap the numeric old→new range in <bdi> so Unicode bidi keeps it
        # left-to-right inside an RTL paragraph (otherwise "(18% → 20%)" can
        # visually render as "(20% ← 18%)").
        items.append(f"""
          <li class="diff-item {css_dir}">
            <a href="#q-{d['id']}">
              <span class="diff-id">{esc(d['id'])}</span>
              <span class="diff-arrow">{arrow}</span>
              <span class="diff-delta">{d['delta_pp']:+.1f}pp</span>
              <bdi class="diff-from-to" dir="ltr">({d['old_p']*100:.0f}% → {d['new_p']*100:.0f}%)</bdi>
              <span class="diff-question" dir="auto">{esc(d['question'])}</span>
            </a>
          </li>
        """)
    return f"""
        <section class="diff-panel" role="region" aria-label="{esc(diff_h)}">
          <h2 class="diff-h">{esc(diff_h)}</h2>
          <ul class="diff-list">{"".join(items)}</ul>
        </section>
    """


def topness(q: dict, last_q_by_id: dict[str, dict], today: datetime | None = None) -> float:
    """Score for 'top question' selection.

    Picks "the question worth watching today" — biased toward questions that
    are actively in play (45-80% probability) rather than always surfacing the
    biggest tail-risk mover. A 70% question holding steady can still be the
    headline if it's high-stakes and the deadline is near.

    `today` is injected (not pulled from datetime.now()) so historical
    snapshot rendering is reproducible.
    """
    if today is None:
        today = datetime.now(timezone.utc)
    cur_p = q["current_probability"]
    qid = q["id"]
    last_q = last_q_by_id.get(qid, {})
    last_p = last_q.get("probability", cur_p)
    abs_delta = abs(cur_p - last_p)
    n_tags = len(q.get("stakeholder_tags", []))
    is_personal = "omid_personal" in q.get("stakeholder_tags", [])
    has_humility = bool(q.get("humility_flag"))
    # Stakes proxy: # stakeholder tags + personal-affects-Omid bonus
    stakes = n_tags * 0.10 + (0.30 if is_personal else 0.0)
    # Recency bonus: questions with deadlines closer to today carry slightly more weight.
    # YAML may parse date strings as datetime.date OR keep them as str — handle both.
    deadline = q["deadline"]
    if hasattr(deadline, "isoformat"):
        deadline_str = deadline.isoformat()
    else:
        deadline_str = str(deadline)
    try:
        d_dt = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_to_deadline = max(1, (d_dt.date() - today.date()).days)
        recency = max(0.0, 1.0 - min(days_to_deadline / 365.0, 1.0)) * 0.10
    except (ValueError, TypeError):
        recency = 0.0
    # Stability bias: a question sitting in the 45-80% band is "actively in play"
    # and more interesting to watch than a 12% tail-risk that just jumped 3pp.
    in_play_bonus = 0.15 if 0.45 <= cur_p < 0.80 else 0.0
    # Humility flags suppress (we shouldn't headline a question we admit we can't forecast)
    humility_penalty = -0.30 if has_humility else 0.0
    return abs_delta * 1.0 + stakes + recency + in_play_bonus + humility_penalty


def render_top_question(q: dict, last_q_by_id: dict, history_present: bool, lang: str = "en") -> str:
    label, _, css = icd203(q["current_probability"], lang=lang)
    pct = round(q["current_probability"] * 100)
    ci = q["current_credible_interval_80"]
    notes = first_sentence(_q_field(q, "notes", lang))
    delta_text = ""
    if history_present:
        last_q = last_q_by_id.get(q["id"], {})
        last_p = last_q.get("probability")
        if last_p is not None and abs(q["current_probability"] - last_p) > 0.001:
            d_pp = (q["current_probability"] - last_p) * 100
            arrow = "▲" if d_pp > 0 else "▼"
            delta_text = (
                f' · <span class="topq-delta">{arrow} {d_pp:+.1f}pp '
                f'{esc(_t("topq_delta_suffix", lang))}</span>'
            )

    eyebrow = _t("topq_eyebrow", lang)
    ci_label_text = _t("topq_ci_label", lang)
    ci_range = f'<bdi dir="ltr">{round(ci[0]*100)}–{round(ci[1]*100)}%</bdi>'
    return f"""
      <section class="topq topq-{css}" role="region" aria-label="{esc(eyebrow)}">
        <div class="topq-eyebrow">{esc(eyebrow)} · {esc(q['id'])} · <bdi dir="ltr">→ {esc(q['deadline'])}</bdi>{delta_text}</div>
        <h2 class="topq-question" dir="auto">{esc(_q_field(q, 'question', lang))}</h2>
        <div class="topq-row">
          <div class="topq-prob">
            <span class="topq-prob-num">{pct}<span class="topq-prob-pct">%</span></span>
            <span class="topq-prob-label">{esc(label)}</span>
            <span class="topq-prob-ci">{esc(ci_label_text)} {ci_range}</span>
          </div>
          <p class="topq-note" dir="auto">{esc(notes)}</p>
        </div>
        <a class="topq-link" href="#q-{q['id']}">{esc(_t("topq_link", lang))}</a>
      </section>
    """


def _human_date_lang(d: datetime, lang: str) -> str:
    """Date format suitable for the masthead eyebrow.
    English: 'May 5, 2026'. Persian: '۵ مه ۱۴۰۵' (Gregorian month rendered
    in Persian + Persian-digit Gregorian year — Jalali conversion is out of
    scope and would mismatch war_day())."""
    if lang == "fa":
        return f"{_to_fa_digits(str(d.day))} {_FA_MONTHS[d.month - 1]} {_to_fa_digits(str(d.year))}"
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def render_headline_narrative(today: datetime, portfolio: dict, stripped: bool = False, lang: str = "en") -> str:
    """Compose the headline paragraph dynamically from current date + portfolio."""
    d = war_day(today)
    today_str = _human_date_lang(today, lang)
    # Top 3 highest-stakes questions to anchor narrative
    high_stakes = sorted(
        portfolio["questions"],
        key=lambda q: -len(q.get("stakeholder_tags", [])),
    )[:3]
    bullets = []
    for q in high_stakes:
        label, _, _ = icd203(q["current_probability"], lang=lang)
        pct_int = round(q["current_probability"] * 100)
        # In RTL the bare percent string (`18%`) and the surrounding parens
        # would attach awkwardly to the Persian label. Wrap percent in <bdi>
        # so bidi recognizes the LTR boundary and the closing `)` mirrors
        # back to the Persian side correctly.
        pct_display = (
            f'<bdi dir="ltr">{_to_fa_digits(str(pct_int))}٪</bdi>'
            if lang == "fa"
            else f"{pct_int}%"
        )
        sep = "،" if lang == "fa" else ","
        bullets.append(
            f"<strong>{esc(q['id'])}</strong> ({esc(label)}{sep} {pct_display}) — "
            f"{esc(_q_field(q, 'question', lang))}"
        )

    intro = _t("headline_body_intro", lang)
    outro_key = "headline_body_outro_public" if stripped else "headline_body_outro_full"
    outro = _t(outro_key, lang)
    body = f"{intro}: {'; '.join(bullets)}. {outro}"

    day_phrase = f'<span class="dropcap">{esc(_t("issue_day", lang)[:1])}</span>{esc(_t("issue_day", lang)[1:])} {d}'
    lead = _t("headline_lead_template", lang).format(day_phrase=day_phrase)

    return f"""
      <section class="headline" role="region" aria-label="{esc(_t("headline_eyebrow_today", lang))}">
        <div class="headline-eyebrow">{esc(_t("headline_eyebrow_today", lang))} · {esc(today_str)} · {esc(_t("headline_eyebrow_tagline", lang))}</div>
        <p class="headline-lead">{lead}</p>
        <p class="headline-body">{body}</p>
      </section>
    """


def render_methodology(stripped: bool = False, lang: str = "en") -> str:
    bullets = "".join(
        f"<li>{_t(f'method_b{i}', lang)}</li>" for i in range(1, 6)
    )
    return f"""
      <section class="methodology" role="region" aria-label="{esc(_t("method_h", lang))}">
        <h2 class="meth-h">{esc(_t("method_h", lang))}</h2>
        <ul class="meth-list">
          {bullets}
        </ul>
      </section>
    """


def render_economic_war_frame(portfolio: dict, lang: str = "en") -> str:
    """Render the editorial framing section (the "why" of the page) above the
    base case. Reads `metadata.economic_war_frame.{en|fa}.{title, body, map_to_questions}`.
    Falls back to English if Persian variant missing. Returns empty string
    if the metadata field is absent."""
    md = portfolio.get("metadata", {}) or {}
    frame = md.get("economic_war_frame") or {}
    block = frame.get(lang) or frame.get("en") or {}
    title = (block.get("title") or "").strip()
    body = (block.get("body") or "").strip()
    if not title and not body:
        return ""
    paragraphs = [esc(p.strip()) for p in body.split("\n\n") if p.strip()]
    body_html = "".join(f'<p class="frame-body">{p}</p>' for p in paragraphs)
    map_text = (block.get("map_to_questions") or "").strip()
    map_html = (
        f'<div class="frame-map"><span class="frame-map-label">{esc(_t("frame_map_label", lang))}</span> '
        f'<span class="frame-map-text">{esc(map_text)}</span></div>'
        if map_text else ""
    )
    return f"""
      <section class="frame" role="region" aria-label="{esc(title)}">
        <div class="frame-eyebrow">{esc(_t("frame_eyebrow", lang))}</div>
        <h2 class="frame-h">{esc(title)}</h2>
        {body_html}
        {map_html}
      </section>
    """


def render_base_case(portfolio: dict, stripped: bool = False, lang: str = "en") -> str:
    """Render the modal-forecast paragraph. Reads `metadata.base_case`:
        base_case:
          en: { full: ..., public: ... }
          fa: { full: ..., public: ... }
          last_updated: YYYY-MM-DD
    Falls back to English if Persian variant missing. Renders nothing if absent.
    """
    md = portfolio.get("metadata", {}) or {}
    bc = md.get("base_case") or {}
    block = bc.get(lang) or bc.get("en") or {}
    key = "public" if stripped else "full"
    text = (block.get(key) or block.get("full") or "").strip()
    if not text and lang != "en":
        # final English fallback
        en_block = bc.get("en") or {}
        text = (en_block.get(key) or en_block.get("full") or "").strip()
    if not text:
        return ""

    last_updated = bc.get("last_updated")
    last_updated_str = ""
    if last_updated is not None:
        last_updated_str = last_updated.isoformat() if hasattr(last_updated, "isoformat") else str(last_updated)
    eyebrow_extra = (
        f" · {esc(_t('basecase_eyebrow_revised', lang))} {esc(_human_date(last_updated_str, lang=lang))}"
        if last_updated_str else ""
    )
    paragraphs = [esc(p.strip()) for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [esc(text)]
    body_html = "".join(f'<p class="basecase-body">{p}</p>' for p in paragraphs)
    return f"""
      <section class="basecase" role="region" aria-label="{esc(_t("basecase_h", lang))}">
        <div class="basecase-eyebrow">{esc(_t("basecase_eyebrow", lang))}{eyebrow_extra}</div>
        <h2 class="basecase-h">{esc(_t("basecase_h", lang))}</h2>
        {body_html}
        <p class="basecase-foot">{esc(_t("basecase_foot", lang))}</p>
      </section>
    """


def render_logs_section() -> str:
    # Intentionally empty — the rendered page does not surface internal log files
    # to visitors. The "What changed since last tick" panel covers the
    # visitor-relevant change history. The actual log files remain on disk for
    # operator review but are not linked from the page.
    return ""


# Probability boundary that splits "most-likely outcomes" from "lower-probability
# scenarios to watch". A card at exactly 45% is in the "roughly even" ICD-203
# bucket — close enough to coin-flip that we lead with it.
LIKELY_THRESHOLD = 0.45


def _split_likely_tail(questions: list[dict]) -> tuple[list[dict], list[dict]]:
    """Sort by current_probability descending, then partition at LIKELY_THRESHOLD.
    Returns (likely_cluster, tail_cluster)."""
    sorted_qs = sorted(questions, key=lambda q: -q["current_probability"])
    likely = [q for q in sorted_qs if q["current_probability"] >= LIKELY_THRESHOLD]
    tail = [q for q in sorted_qs if q["current_probability"] < LIKELY_THRESHOLD]
    return likely, tail


def render_question_board(by_cat: dict, stripped: bool = False, lang: str = "en") -> str:
    total = sum(len(qs) for qs in by_cat.values())
    n_display = _to_fa_digits(str(total)) if lang == "fa" else str(total)
    board_h = _t("board_h_template", lang).format(n=n_display)
    board_sub_html = f'<p class="board-sub">{_t("board_sub", lang)}</p>'
    notice = _t("translation_in_progress_notice", lang)
    # Only render the notice if there's actually missing translation in the
    # questions about to be shown (any visible Q without `question_fa` for fa).
    needs_notice = False
    if lang == "fa" and notice:
        for cat_qs in by_cat.values():
            for q in cat_qs:
                if not q.get("question_fa"):
                    needs_notice = True
                    break
            if needs_notice:
                break
    notice_html = f'<p class="board-translation-notice" dir="auto">{esc(notice)}</p>' if needs_notice else ""
    parts = [
        f'<section class="board" role="region" aria-label="{esc(board_h)}">'
        f'<h2 class="board-h">{esc(board_h)}</h2>',
        board_sub_html,
        notice_html,
    ]
    for cat_id in CATEGORY_ORDER:
        if cat_id not in by_cat:
            continue
        num, title, css = category_label(cat_id, lang)
        likely, tail = _split_likely_tail(by_cat[cat_id])
        cluster_blocks: list[str] = []
        if likely:
            cluster_blocks.append(f"""
              <div class="board-cluster board-cluster-likely">
                <h4 class="board-cluster-h">{esc(_t("cluster_likely_h", lang))}</h4>
                <div class="board-grid">
                  {"".join(render_question_card(q, stripped=stripped, lang=lang) for q in likely)}
                </div>
              </div>
            """)
        if tail:
            cluster_blocks.append(f"""
              <div class="board-cluster board-cluster-tail">
                <h4 class="board-cluster-h">{esc(_t("cluster_tail_h", lang))}</h4>
                <div class="board-grid">
                  {"".join(render_question_card(q, stripped=stripped, lang=lang) for q in tail)}
                </div>
              </div>
            """)
        cluster_html = '<hr class="board-cluster-divider" aria-hidden="true" />'.join(cluster_blocks) if len(cluster_blocks) > 1 else "".join(cluster_blocks)
        parts.append(f"""
          <div class="board-cat board-{css}">
            <header class="board-cat-head">
              <span class="board-cat-num">{esc(num)}</span>
              <h3 class="board-cat-title">{esc(title)}</h3>
              <span class="board-cat-count">{esc(_t("cat_count_template", lang).format(n=(_to_fa_digits(str(len(by_cat[cat_id]))) if lang == "fa" else str(len(by_cat[cat_id])))))}</span>
            </header>
            {cluster_html}
          </div>
        """)
    parts.append("</section>")
    return "\n".join(parts)


# Categories that contain personal/business content — stripped from public deploy
PRIVATE_CATEGORIES = {"family_business_iranfarhang", "family_business_kipa"}
# Stakeholder tags that mark a question as private — even if its category is generic.
# Defense-in-depth against a private question accidentally being placed in a generic
# category (e.g. economic_structural) but still tagged for personal channels.
PRIVATE_STAKEHOLDER_TAGS = {"omid_personal", "iranfarhang_business", "kipa_business"}


def _is_private_question(q: dict) -> bool:
    if q.get("category") in PRIVATE_CATEGORIES:
        return True
    return any(t in PRIVATE_STAKEHOLDER_TAGS for t in q.get("stakeholder_tags", []))


def _toggle_link(lang: str, stripped: bool) -> tuple[str, str]:
    """Returns (href, label) for the language-toggle link. Each rendered page
    points to its sibling-language file."""
    other = "fa" if lang == "en" else "en"
    if stripped:
        # On the public deploy, the file is served at root: index.html (en) or fa.html (fa).
        # build-public.py renames public.html → index.html and public.fa.html → fa.html.
        href = "/" if other == "en" else "/fa.html"
    else:
        # On the private deploy: index.html (en) or fa.html (fa) at repo root.
        href = "/" if other == "en" else "/fa.html"
    label = STRINGS[other]["lang_toggle_to_" + other] if other in STRINGS else other
    # lang_toggle_to_fa always shows فارسی and lang_toggle_to_en always shows English
    label = STRINGS["en"]["lang_toggle_to_" + other] if other == "fa" else STRINGS["fa"]["lang_toggle_to_" + other]
    return href, label


def render_html(portfolio: dict, diffs: list[dict], history: list[dict], stripped: bool = False, lang: str = "en") -> str:
    today = datetime.now(timezone.utc)
    today_iso = today.strftime("%Y-%m-%d")
    next_tick_local = _t("topbar_next_value", lang)

    # Stripped public deploy excludes private/personal/business questions entirely.
    # Filter applies BOTH category and stakeholder-tag rules so a Q tagged for
    # private channels but placed in a generic category still gets stripped.
    questions_for_view = [
        q for q in portfolio["questions"]
        if not stripped or not _is_private_question(q)
    ]
    # Stripped portfolio passed to renderers as if it were the full portfolio
    portfolio_view = {**portfolio, "questions": questions_for_view}

    # Stripped diffs: drop any diff whose Q is private — by category, by tag,
    # OR by ID-prefix `F` (covers a Q that was deleted/recategorized between
    # the snapshot and now and would otherwise leak via the diff payload).
    private_qids = {q["id"] for q in portfolio["questions"] if _is_private_question(q)}
    diffs_for_view = [
        d for d in diffs
        if not stripped or (
            d.get("id", "") not in private_qids
            and not str(d.get("id", "")).startswith("F")
        )
    ]

    by_cat: dict[str, list[dict]] = {}
    for q in questions_for_view:
        by_cat.setdefault(q["category"], []).append(q)

    # last_q_by_id: portfolio snapshot from yesterday-or-prior
    prior = [h for h in history if h.get("date") and h["date"] < today_iso and _is_v02_snapshot(h)]
    last_q_by_id = {q.get("id"): q for q in (prior[-1].get("questions", []) if prior else [])}

    # Top question: filtered to public set if stripped
    if questions_for_view:
        top_q = max(questions_for_view, key=lambda q: topness(q, last_q_by_id, today=today))
    else:
        top_q = portfolio["questions"][0]

    if lang == "fa":
        title_base = STRINGS["fa"]["site_eyebrow"] + " — " + STRINGS["fa"]["site_title"]
        public_suffix = " (عمومی)" if stripped else ""
    else:
        title_base = "2026 Iran Conflict — Predictive Agent"
        public_suffix = " (Public)" if stripped else ""
    title = title_base + public_suffix
    n_questions_visible = len(questions_for_view)
    if lang == "fa":
        description_text = f"گزارش احتمال روزانه‌ی {n_questions_visible} پرسش درباره‌ی نزاع ایران و آمریکا ۲۰۲۶. آزمایشی — بدون سابقه."
    else:
        description_text = f"Daily-updated probability brief on {n_questions_visible} questions about the 2026 Iran-US conflict. Experimental — no track record yet."

    toggle_href, toggle_label = _toggle_link(lang, stripped)
    is_rtl = (lang == "fa")
    html_dir = "rtl" if is_rtl else "ltr"

    d = war_day(today)
    day_num = _to_fa_digits(str(d)) if lang == "fa" else str(d)
    issue_subline = f"{_t('issue_day', lang)} {day_num}"
    # Cease-fire / blockade day counters were removed from the masthead — they
    # imply a steady-state count that's misleading once the situation shifts.
    # The "most-likely scenario" paragraph below carries the live read.

    methodology_html = render_methodology(stripped=stripped, lang=lang)
    logs_html = "" if stripped else render_logs_section()

    # Footer keeps only links a visitor would actually click.
    if stripped:
        footer_links_html = ""
    else:
        footer_links_html = f'<a href="/legacy">{esc(_t("footer_legacy_link", lang))}</a>'

    banner_link = (
        ""
        if stripped else
        f' <a href="/legacy">{esc(_t("banner_legacy_link", lang))}</a>'
    )

    canonical_base = "https://iran-war-public.vercel.app/" if stripped else "https://iran-war-dashboard-murex.vercel.app/"
    canonical_url = canonical_base + ("fa.html" if lang == "fa" else "")

    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}" dir="{esc(html_dir)}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#0b1322" />
  <title>{esc(title)}</title>
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description_text)}" />
  <meta property="og:type" content="article" />
  <meta name="description" content="{esc(description_text)}" />
  <link rel="stylesheet" href="dashboard.css" />
  {('<link rel="preconnect" href="https://fonts.googleapis.com" />' +
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />' +
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap" />')
   if is_rtl else ''}
  <link rel="canonical" href="{esc(canonical_url)}" />
  <link rel="alternate" hreflang="en" href="{esc(canonical_base)}" />
  <link rel="alternate" hreflang="fa" href="{esc(canonical_base + 'fa.html')}" />
</head>
<body class="agent-v2 lang-{esc(lang)}{' is-rtl' if is_rtl else ''}">

  <div class="topbar">
    <div class="topbar-inner">
      <div class="topbar-l">
        <span class="topbar-eyebrow">{esc(_t("site_eyebrow", lang))}</span>
        <span class="topbar-title">{esc(_t("site_title", lang))}</span>
      </div>
      <div class="topbar-r">
        <span class="topbar-meta">{esc(_to_fa_digits(today.strftime("%Y-%m-%d %H:%M")) if lang == "fa" else today.strftime("%Y-%m-%d %H:%M"))} UTC</span>
        <span class="topbar-meta">{esc(_t("topbar_next_label", lang))} {esc(next_tick_local)}</span>
        <a class="topbar-meta lang-toggle" href="{esc(toggle_href)}" hreflang="{'fa' if lang == 'en' else 'en'}" rel="alternate">{esc(toggle_label)}</a>
      </div>
    </div>
  </div>

  <div class="experimental-banner agent-banner">
    <strong>{esc(_t("banner_strong", lang))}</strong>
    <span>{_t("banner_text", lang)}{banner_link}</span>
  </div>

  <main class="agent-page" role="main" aria-label="{esc(_t("site_title", lang))}">

    <header class="agent-masthead" role="banner" aria-label="{esc(_t("masthead_publisher", lang))}">
      <div class="masthead-class">{esc(_t("masthead_classification", lang))}</div>
      <div class="masthead-row">
        <div class="masthead-l">
          <div class="masthead-eyebrow">{esc(_t("masthead_issue_prefix", lang))} · {esc(issue_subline)}</div>
          <h1 class="masthead-title">{esc(_t("site_title", lang))}</h1>
        </div>
        <div class="masthead-r">
          <div class="masthead-publisher">{esc(_t("masthead_publisher", lang))}</div>
          <div class="masthead-publisher-sub">{esc(_t("masthead_subline", lang))}</div>
        </div>
      </div>
      <div class="masthead-rule"></div>
    </header>

    {render_headline_narrative(today, portfolio_view, stripped=stripped, lang=lang)}

    {render_economic_war_frame(portfolio_view, lang=lang)}

    {render_base_case(portfolio_view, stripped=stripped, lang=lang)}

    {render_diff_panel(diffs_for_view, history, lang=lang)}

    {render_top_question(top_q, last_q_by_id, history_present=bool(prior), lang=lang)}

    {render_question_board(by_cat, stripped=stripped, lang=lang)}

    {logs_html}

    {methodology_html}

  </main>

  <footer class="agent-footer">
    <div class="agent-footer-inner">
      <div class="agent-footer-l">
        <div class="agent-footer-brand">{esc(_t("footer_brand", lang))}</div>
        <div class="agent-footer-meta">{esc(_t("footer_meta", lang))}</div>
      </div>
      <div class="agent-footer-r">
        {footer_links_html}
      </div>
    </div>
  </footer>

</body>
</html>
"""


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def main():
    import time
    t0 = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true", help="Also render public.html / public.fa.html (stripped)")
    args = parser.parse_args()

    portfolio = load_portfolio()
    history = load_history()
    diffs = compute_diffs_vs_yesterday(portfolio, history)

    targets: list[tuple[Path, bool, str]] = [
        (OUTPUT_INDEX, False, "en"),
        (OUTPUT_INDEX_FA, False, "fa"),
    ]
    if args.public:
        targets.append((OUTPUT_PUBLIC, True, "en"))
        targets.append((OUTPUT_PUBLIC_FA, True, "fa"))
    for out_path, stripped, lang in targets:
        html = render_html(portfolio, diffs, history, stripped=stripped, lang=lang)
        _atomic_write(out_path, html)
        print(f"wrote {out_path} ({len(html)} bytes, lang={lang}, stripped={stripped})")
    print(f"render took {time.monotonic() - t0:.2f}s")


if __name__ == "__main__":
    main()
