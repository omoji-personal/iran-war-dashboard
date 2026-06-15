"""One-shot, comment-preserving updater for the 2026-06-15 deal-era refresh.

Applies the full re-rate + resolutions + 2 new questions + rewritten editorial
prose + deal-tracker metadata to portfolio.yaml, grounded in the cited intel
sweep (agent/audit-update-workflow.mjs → /tmp/iwd_result.json). Idempotent-ish:
re-running overwrites the same fields. Validate with `pytest -q` after.
"""
from __future__ import annotations

from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString as LS

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO = ROOT / "portfolio.yaml"

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096  # don't wrap our long single-line strings
yaml.indent(mapping=2, sequence=4, offset=2)  # match the original list indentation

ICD = [
    (0.00, 0.01, "vanishing"), (0.01, 0.05, "almost_no_chance"),
    (0.05, 0.20, "very_unlikely"), (0.20, 0.45, "unlikely"),
    (0.45, 0.55, "roughly_even_chance"), (0.55, 0.80, "likely"),
    (0.80, 0.95, "very_likely"), (0.95, 0.99, "almost_certain"),
    (0.99, 1.001, "near_certain"),
]


def label_for(p: float) -> str:
    for lo, hi, name in ICD:
        if lo <= p < hi:
            return name
    return "near_certain"


# ---- Per-question updates: qid -> (prob, [ci_lo, ci_hi], notes_en, notes_fa,
#                                    status|None, resolution_date|None) --------
U = {}


def upd(qid, p, ci, en, fa, status=None, rdate=None):
    U[qid] = dict(p=p, ci=ci, en=en.strip(), fa=fa.strip(), status=status, rdate=rdate)


# ===== A. Diplomatic =====
upd("A1", 0.93, [0.85, 0.98],
    "Framework MOU reached June 14 (Trump declared the deal 'complete'); Iran's Deputy FM Gharibabadi confirmed it, with formal signing set for June 19 in Switzerland. Held just short of resolved-YES pending signature — prior 'complete' announcements had collapsed, and the written framework defers the sanctions-relief and nuclear-monitoring components to 60-day follow-on talks (NBC/Axios/Al Jazeera).",
    "توافق چارچوبی (تفاهم‌نامه) در ۱۴ ژوئن حاصل شد و ترامپ آن را «کامل» خواند؛ قریب‌آبادی معاون وزیر خارجه‌ی ایران تأیید کرد و امضای رسمی برای ۱۹ ژوئن در سوئیس تعیین شد. کمی پیش از قطعی‌شدنِ بله نگه داشته شد چون اجزای رفع تحریم و نظارت هسته‌ای به مذاکرات ۶۰ روزه موکول شده‌اند.")
upd("A2", 0.80, [0.62, 0.93],
    "Trump ordered the naval blockade lifted and Hormuz reopened toll-free (June 14); commercial transit was still only ~2-6 vessels/day pre-deal vs ~135 pre-war, and physical recovery is gated by mine-clearing (Polymarket prices year-end normalization ~88%). >50% pre-war (>67/day 7d-MA) by Dec 31 is now likely, not certain (CNBC/USNI).",
    "ترامپ در ۱۴ ژوئن دستور رفع محاصره‌ی دریایی و بازگشایی بدون‌عوارض هرمز را داد؛ تردد تجاری پیش از توافق هنوز حدود ۲ تا ۶ کشتی در روز بود (در برابر ۱۳۵ پیش‌از‌جنگ) و بازیابی فیزیکی به مین‌روبی بستگی دارد. عبور از ۵۰٪ سطح پیش‌از‌جنگ تا پایان سال محتمل ولی نه قطعی.")
upd("A3", 0.06, [0.02, 0.15],
    "A toll-free reopening plus blockade removal guts the rationale for a formal Earnest-Will-style reflagging; the US 'Project Freedom' posture is an escort-less 'guide' operation and CNN reported warships would not escort merchants. Down from 10%.",
    "بازگشایی بدون عوارض و رفع محاصره دلیل تغییر پرچم رسمی را از بین می‌برد؛ موضع «پروژه‌ی آزادی» آمریکا یک عملیات «هدایت» بدون اسکورت است. کاهش از ۱۰٪.")
upd("A4", 0.55, [0.35, 0.75],
    "The MOU's 60-day window is explicitly built around Iran's mid-May 14-point proposal (a two-month negotiating period), so the 14-point framework is functionally becoming the basis for working-level talks — plausibly with announced joint groups before Aug 31, though the US zero-enrichment demand could stall it (The Media Line/AP).",
    "پنجره‌ی ۶۰ روزه‌ی تفاهم‌نامه بر پایه‌ی پیشنهاد چهارده‌بندی میانه‌ی مه ایران بنا شده، پس این چارچوب عملاً به مبنای مذاکرات کارشناسی تبدیل می‌شود؛ ولی مطالبه‌ی توقف کامل غنی‌سازی از سوی آمریکا می‌تواند آن را متوقف کند.")
upd("A5", 0.02, [0.00, 0.05],
    "Premise void: Ali Khamenei was killed in the Feb 28 strikes and his son Mojtaba became Supreme Leader on March 8; the new leader steered negotiators toward a deal pragmatically, not via the 2013-era 'heroic flexibility' framing this question tracked. Resolved NO (un-resolvable for the original figure).",
    "پیش‌فرض باطل است: علی خامنه‌ای در حملات ۲۸ فوریه کشته شد و پسرش مجتبی در ۸ مارس رهبر شد؛ رهبر تازه مذاکره‌کنندگان را عمل‌گرایانه به‌سوی توافق سوق داد، نه با چارچوب «نرمش قهرمانانه». قطعیِ خیر.",
    status="resolved_no", rdate="2026-03-08")

# ===== B. Military =====
upd("B1", 0.99, [0.98, 1.0],
    "Resolved YES: the US struck Iranian sovereign territory repeatedly through the war — the Feb 28 opening strikes, the March Hormuz-reopening air campaign, the May 7 strikes on Bandar Abbas/Qeshm, and June 9-10 CENTCOM strikes (Al Jazeera/CNN/Wikipedia).",
    "قطعیِ بله: آمریکا بارها به خاک ایران حمله کرد — حملات آغازین ۲۸ فوریه، کارزار هوایی مارس برای بازگشایی هرمز، حملات ۷ مه به بندرعباس/قشم، و حملات ۹ تا ۱۰ ژوئن سنتکام.",
    status="resolved_yes", rdate="2026-02-28")
upd("B2", 0.99, [0.98, 1.0],
    "Resolved YES: Iran struck US bases — a ballistic missile hit Al Udeid (Qatar) on March 3 and Camp Arifjan (Kuwait) on ~March 1, killing US service members, plus NSA Bahrain; later missile/boat attacks targeted US destroyers in Hormuz (Critical Threats/Stars and Stripes).",
    "قطعیِ بله: ایران به پایگاه‌های آمریکا حمله کرد — موشک بالستیک به العدید (قطر) در ۳ مارس و کمپ ارفجان (کویت) در حدود ۱ مارس با کشته‌شدن نظامیان آمریکایی، به‌علاوه‌ی پایگاه دریایی بحرین.",
    status="resolved_yes", rdate="2026-03-03")
upd("B3", 0.99, [0.98, 1.0],
    "Resolved YES: Israel, with the US, struck Iran's Natanz enrichment complex in the war's opening phase (Feb 28 / early March, AEOI- and IAEA-confirmed, no off-site radiation) (Al Jazeera/Critical Threats).",
    "قطعیِ بله: اسرائیل به‌همراه آمریکا در فاز آغازین جنگ (۲۸ فوریه/اوایل مارس) به مجتمع غنی‌سازی نطنز حمله کرد؛ سازمان انرژی اتمی ایران و آژانس آن را تأیید کردند.",
    status="resolved_yes", rdate="2026-03-02")
upd("B4", 0.20, [0.08, 0.40],
    "The June 7 strike that reached >25km north (Ramat David airbase) was an Iranian ballistic-missile attack, not a Hezbollah-attributed strike on a population center, so the specific condition is unresolved; the June 14 deal calls for permanent termination of Lebanon operations, lowering residual odds. Down to ~20%.",
    "حمله‌ی ۷ ژوئن که به بیش از ۲۵ کیلومتر شمال رسید (پایگاه رامات داوید) حمله‌ی موشکی ایران بود، نه حمله‌ی منتسب به حزب‌الله به مرکز جمعیتی؛ توافق ۱۴ ژوئن خواستار پایان دائمی عملیات لبنان است. کاهش به حدود ۲۰٪.")
upd("B5", 0.99, [0.98, 1.0],
    "Resolved YES: Iran/IRGC seized at least 3-4 foreign-flagged commercial vessels well before the deadline — MSC Francesca and Epaminondas in April, plus the tanker Ocean Koi and a Fujairah-area vessel in May (Al Jazeera).",
    "قطعیِ بله: سپاه دست‌کم ۳ تا ۴ کشتی تجاری با پرچم خارجی را پیش از مهلت توقیف کرد — MSC Francesca و Epaminondas در آوریل و نفت‌کش Ocean Koi و یک کشتی نزدیک فجیره در مه.",
    status="resolved_yes", rdate="2026-05-08")

# ===== C. Regime =====
upd("C1", 0.99, [0.98, 1.0],
    "Resolved YES — the dashboard had carried a counterfactual: Ali Khamenei was killed in the Feb 28 US-Israeli strikes (Iran confirmed his death March 1; state funeral set for July 4-9). The 'recovering from burns' read was wrong (NPR/Caspian News/Al Jazeera/WaPo).",
    "قطعیِ بله — داشبورد یک خلاف‌واقع را حمل می‌کرد: علی خامنه‌ای در حملات ۲۸ فوریه کشته شد (ایران مرگ او را ۱ مارس تأیید کرد؛ مراسم تشییع ۴ تا ۹ ژوئیه). خوانش «بهبودی از سوختگی» اشتباه بود.",
    status="resolved_yes", rdate="2026-02-28")
upd("C2", 0.38, [0.20, 0.58],
    "The deadliest protest wave since 1979 (Dec 28-mid Jan; 210 cities/all 31 provinces) has largely subsided; May-June activity is real but lower-intensity (student/'resistance-unit' actions), the 88-day internet blackout lifted ~May 26 (~86%), and an imminent deal plus a firmer rial bleed off grievance. A fresh qualifying wave eases to ~38% (Iran Intl/NetBlocks/NCRI).",
    "مرگبارترین موج اعتراضی از ۱۹۷۹ (۲۸ دسامبر تا میانه‌ی ژانویه، ۲۱۰ شهر/همه‌ی ۳۱ استان) عمدتاً فروکش کرده؛ فعالیت مه-ژوئن کم‌شدت‌تر است، قطعی اینترنت ۸۸ روزه حدود ۲۶ مه برداشته شد، و توافق قریب‌الوقوع نارضایتی را کم می‌کند. موج تازه‌ی واجد شرایط حدود ۳۸٪.")
upd("C3", 0.99, [0.98, 1.0],
    "Resolved YES — overtaken by events: the Assembly of Experts named Mojtaba Khamenei Supreme Leader on March 8, far beyond 'heir-apparent.' He remains an invisible, contested leader (no verified public appearance), but the designation itself is settled (Al Jazeera/CNN/Iran Intl).",
    "قطعیِ بله — مجلس خبرگان در ۸ مارس مجتبی خامنه‌ای را رهبر کرد، فراتر از «جانشین تعیین‌شده». او رهبری نامرئی و مورد مناقشه است (بدون ظاهر علنی تأییدشده)، ولی خودِ انتصاب قطعی است.",
    status="resolved_yes", rdate="2026-03-08")
upd("C4", 0.22, [0.10, 0.42],
    "No fresh sustained Tehran Grand Bazaar shutdown documented in late May/June; with the internet partly restored, an imminent deal, and a firmer rial, near-term bazaari-strike pressure eased, though 68.9% inflation keeps it non-trivial. Down to ~22% (NCRI/IMF).",
    "هیچ تعطیلی پایدار تازه‌ای در بازار بزرگ تهران در اواخر مه/ژوئن ثبت نشد؛ با بازگشت نسبی اینترنت، توافق قریب‌الوقوع و ریال قوی‌تر، فشار اعتصاب بازاری کاهش یافت، هرچند تورم ۶۸.۹٪ آن را غیرناچیز نگه می‌دارد. کاهش به حدود ۲۲٪.")

# ===== D. Economic =====
upd("D1", 0.30, [0.16, 0.52],
    "The rial strengthened to ~1.62M IRR/USD by June 15 (from 1.842M on May 12) on deal optimism and never crossed 2,000,000 (365-day max ~1.925M); the trend is now away from the threshold, so a year-end >2M print falls sharply from 68% (Alanchand/Bonbast).",
    "ریال تا ۱۵ ژوئن به حدود ۱.۶۲ میلیون تقویت شد (از ۱.۸۴۲ میلیون در ۱۲ مه) و هرگز از ۲ میلیون عبور نکرد (سقف یک‌ساله حدود ۱.۹۲۵ میلیون)؛ روند اکنون از آستانه دور می‌شود، پس احتمال عبور تا پایان سال به‌شدت از ۶۸٪ کاهش می‌یابد.")
upd("D2", 0.99, [0.98, 1.0],
    "Resolved YES: Iran's seaborne crude+condensate exports fell below 300,000 bpd in May 2026 per Kpler — well under the 0.5M bpd threshold, the lowest in 6+ years, driven by the US naval blockade (Al Jazeera/Kpler).",
    "قطعیِ بله: صادرات نفت خام و میعانات دریایی ایران در مه ۲۰۲۶ طبق Kpler به زیر ۳۰۰٬۰۰۰ بشکه در روز رسید — بسیار کمتر از آستانه‌ی ۰.۵ میلیون، کمترین در بیش از ۶ سال، به‌دلیل محاصره‌ی دریایی آمریکا.",
    status="resolved_yes", rdate="2026-05-31")
upd("D3", 0.99, [0.98, 1.0],
    "Resolved YES: the AAA US national average sat above $4.50 from ~May 7 through late May, peaking at $4.564 on May 21 — far more than 7 consecutive days (it has since retraced to ~$4.07) (AAA Gas Prices/LendingTree).",
    "قطعیِ بله: میانگین ملی AAA از حدود ۷ مه تا اواخر مه بالای ۴.۵۰ دلار ماند و در ۲۱ مه به ۴.۵۶۴ دلار رسید — بسیار بیش از ۷ روز پیاپی (از آن پس به حدود ۴.۰۷ دلار بازگشته).",
    status="resolved_yes", rdate="2026-05-21")
upd("D4", 0.08, [0.03, 0.18],
    "Brent fell to ~$83-87 (lowest since early March, ~20% off the 2026 peak) on the deal, with Hormuz set to reopen and the blockade lifted; a >$130 year-end print now requires a major deal collapse. Down to ~8% (CNBC/TradingEconomics).",
    "برنت با توافق به حدود ۸۳ تا ۸۷ دلار افت کرد (کمترین از اوایل مارس، حدود ۲۰٪ پایین‌تر از سقف ۲۰۲۶)، با بازگشایی هرمز و رفع محاصره؛ عبور از ۱۳۰ دلار تا پایان سال اکنون نیازمند فروپاشی بزرگ توافق است. کاهش به حدود ۸٪.")

# ===== E. US side =====
upd("E1", 0.20, [0.10, 0.33],
    "No SecDef/NSA/SecState replacement in the window — Hegseth survived the April purge with Trump's backing (~98.8% on Polymarket to stay through June) and Rubio is stable as SecState/acting NSA; with the war winding down, shock risk falls. Down to ~20% (CBS/Polymarket).",
    "هیچ تعویض وزیر دفاع/مشاور امنیت ملی/وزیر خارجه در این بازه رخ نداد — هگست از پاکسازی آوریل با حمایت ترامپ جان به در برد (حدود ۹۸.۸٪ در پلی‌مارکت برای ماندن) و روبیو پایدار است؛ با فروکش جنگ، ریسک شوک کاهش می‌یابد. کاهش به حدود ۲۰٪.")
upd("E2", 0.83, [0.70, 0.92],
    "Market and fundamentals point to Democrats taking at least the House — generic ballot D+6.6 (near 2018), Polymarket ~83% Dem House (GOP ~56% to hold the Senate) — so 'GOP loses either chamber' is the clear favorite; the June 14 deal trims gas prices and war-fatigue but arrived too late to reverse the trend. Up to ~83% (Silver Bulletin/Polymarket).",
    "بازار و بنیان‌ها به پیروزی دموکرات‌ها دست‌کم در مجلس نمایندگان اشاره دارند — رأی عمومی D+6.6 (نزدیک ۲۰۱۸)، پلی‌مارکت حدود ۸۳٪ مجلس برای دموکرات‌ها — پس «از دست‌دادن یکی از دو مجلس» نامزد روشن است؛ توافق ۱۴ ژوئن دیر رسید. افزایش به حدود ۸۳٪.")

# ===== F.1 Iranfarhang =====
upd("F1", 0.15, [0.06, 0.30],
    "The general sanctions/cargo climate eased at the end of the window (the deal commits to lifting the blockade within 30 days and reopening Hormuz), modestly lowering institutional-political pause risk; FY27 approval-plan renewals still start ~Jul-Sep. Down to ~15%.",
    "فضای کلی تحریم/محموله در پایان بازه آرام شد (توافق متعهد به رفع محاصره ظرف ۳۰ روز و بازگشایی هرمز)، که ریسک توقف نهادی-سیاسی را اندکی کاهش می‌دهد؛ تمدیدهای سال مالی ۲۰۲۷ هنوز پیش‌رو. کاهش به حدود ۱۵٪.")
upd("F2", 0.35, [0.20, 0.52],
    "European/French correspondent banks kept de-risking Iran exposure through the window (and a foiled pro-Iran plot hit a BofA branch in Paris), keeping freeze risk elevated; the June 14 deal cuts forward risk but relief is unsigned/unimplemented as of June 15. Roughly held at ~35%.",
    "بانک‌های کارگزار اروپایی/فرانسوی در طول بازه به کاهش ریسک ایران ادامه دادند (و یک توطئه‌ی ناکام به شعبه‌ی BofA پاریس اصابت کرد)، که ریسک انجماد را بالا نگه داشت؛ توافق ۱۴ ژوئن ریسک آینده را کم می‌کند ولی تا ۱۵ ژوئن امضا/اجرا نشده. تقریباً ثابت در حدود ۳۵٪.")
upd("F3", 0.50, [0.30, 0.70],
    "Execution milestone unchanged at coin-flip; the ~May 26 restoration of Iranian internet (~86%) and the de-escalating war reduce the acute disaster-recovery driver, but the standby-server drill still awaits the open infrastructure answers. Held ~50%.",
    "نقطه‌عطف اجرایی در حد شیر-یا-خط بدون تغییر؛ بازگشت اینترنت ایران (~۸۶٪) حدود ۲۶ مه و فروکش جنگ محرک حاد بازیابی‌ازفاجعه را کم می‌کند، ولی تمرین سرور پشتیبان هنوز منتظر پاسخ‌های زیرساختی است. ثابت ~۵۰٪.")
upd("F4", 0.40, [0.22, 0.60],
    "Cargo/shipping risk improves on the deal — the blockade is to be lifted to full capacity within 30 days and Hormuz reopened 'permanently toll free' — versus the May-15 closed-Hormuz baseline; residual risk persists only because the MOU is unsigned as of June 15. Down to ~40%.",
    "ریسک محموله/کشتیرانی با توافق بهبود می‌یابد — محاصره قرار است ظرف ۳۰ روز به ظرفیت کامل برداشته شود و هرمز «دائماً بدون عوارض» باز شود — در برابر خط پایه‌ی بسته‌ی ۱۵ مه؛ ریسک باقی‌مانده فقط چون تفاهم‌نامه تا ۱۵ ژوئن امضا نشده. کاهش به حدود ۴۰٪.")
upd("F5", 0.07, [0.02, 0.15],
    "No OFAC/AUPresses/Federal Register signal of any Berman / 31 CFR 560.315 informational-materials narrowing appeared in the window; June OFAC activity was licensing (GLs U/V/W), not exemption restriction, and the trajectory is toward relief. Held low ~7%.",
    "هیچ نشانه‌ای از محدودسازی معافیت مواد اطلاعاتی (۳۱ CFR 560.315) برمن در این بازه ظاهر نشد؛ فعالیت ژوئن OFAC صدور مجوز بود، نه محدودسازی، و مسیر به‌سوی تسهیل است. پایین نگه‌داشته ~۷٪.")
upd("F6", 0.40, [0.22, 0.60],
    "Iran's internet was ~86% restored on ~May 26 after an 88-day blackout and the war is de-escalating, cutting the single-largest communication-loss driver; major social platforms stay blocked. Down to ~40% (NetBlocks/Iran Intl).",
    "اینترنت ایران حدود ۲۶ مه پس از ۸۸ روز قطعی تا حدود ۸۶٪ بازگشت و جنگ در حال فروکش است، که بزرگ‌ترین محرک قطع ارتباط را کم می‌کند؛ شبکه‌های اجتماعی بزرگ همچنان مسدودند. کاهش به حدود ۴۰٪.")

# ===== F.2 Kipa =====
upd("F7", 0.22, [0.10, 0.45],
    "Deadline June 30: the MOU signs June 19 and Hormuz is reopening, but physical normalization is gated by mine-clearing (up to ~6 months; Polymarket prices end-June normalization ~25%), so a sustained 7-day >50% pre-war recovery by June 30 is unlikely even as the political reopening helps. ~22%.",
    "مهلت ۳۰ ژوئن: تفاهم‌نامه ۱۹ ژوئن امضا می‌شود و هرمز در حال بازگشایی است، ولی عادی‌سازی فیزیکی به مین‌روبی بستگی دارد (تا حدود ۶ ماه؛ پلی‌مارکت عادی‌سازی پایان ژوئن را ~۲۵٪ می‌داند)، پس بازیابی پایدار ۷ روزه‌ی بیش از ۵۰٪ تا ۳۰ ژوئن بعید است. ~۲۲٪.")
upd("F8", 0.28, [0.14, 0.48],
    "The free-market rial strengthened to ~1.62M and never approached 2M (365-day max ~1.925M); the more-managed ICE/official rate is even less likely to print >2M by Aug 31. Down to ~28% (Alanchand).",
    "ریال آزاد به حدود ۱.۶۲ میلیون تقویت شد و هرگز به ۲ میلیون نزدیک نشد (سقف یک‌ساله ~۱.۹۲۵ میلیون)؛ نرخ مدیریت‌شده‌ی ICE حتی کمتر احتمال دارد تا ۳۱ اوت از ۲ میلیون عبور کند. کاهش به حدود ۲۸٪.")
upd("F9", 0.40, [0.20, 0.62],
    "Sanctions-invariant domestic execution milestone; the de-escalation marginally helps the domestic capex climate but the bet remains pure execution-tracking. Held ~40%.",
    "نقطه‌عطف اجرایی داخلیِ ضدتحریم؛ فروکش جنگ اندکی به فضای سرمایه‌گذاری داخلی کمک می‌کند ولی شرط، خالصاً ردیابی اجرایی می‌ماند. ثابت ~۴۰٪.")
upd("F10", 0.10, [0.03, 0.20],
    "Iran's MIMT moved the OPPOSITE direction — a May 20 directive LOOSENED rules to let petrochemical/polymer makers import raw materials via informal channels after war damage — so a manufacturer-end-user import RESTRICTION by year-end looks less likely. Down to ~10%.",
    "وزارت صمت ایران در جهت مخالف حرکت کرد — دستور ۲۰ مه قواعد را شل کرد تا تولیدکنندگان پتروشیمی/پلیمر پس از آسیب جنگ مواد اولیه را از مجاری غیررسمی وارد کنند — پس محدودسازی واردات به مصرف‌کننده‌ی تولیدکننده تا پایان سال کمتر محتمل است. کاهش به حدود ۱۰٪.")
upd("F11", 0.40, [0.26, 0.56],
    "OFAC's May 1 and May 11 'Economic Fury' tranches explicitly designated UAE-based petroleum/petrochemical intermediaries (e.g. Universal Fortune Trading LLC), showing active targeting of Dubai-structured FZCO/FZE entities; partly offset by the June 14 relief pivot. Up to ~40%.",
    "تراش‌های ۱ و ۱۱ مه OFAC («خشم اقتصادی») صراحتاً واسطه‌های نفتی/پتروشیمی مستقر در امارات را تحریم کرد، که هدف‌گیری فعال نهادهای FZCO/FZE دبی را نشان می‌دهد؛ تا حدی با چرخش تسهیل ۱۴ ژوئن جبران می‌شود. افزایش به حدود ۴۰٪.")
upd("F12", 0.45, [0.26, 0.62],
    "The polymer war premium is already compressing — LDPE/PE prices that spiked to records are correcting lower as China re-enters export markets and the Hormuz premium decays ahead of the deal — making a >25% compression from the April anchor more likely by Aug 31. Up to ~45% (ChemOrbis).",
    "حق بیمه‌ی جنگ پلیمر در حال فشردگی است — قیمت‌های LDPE/PE که به رکورد رسیده بودند با بازگشت چین به بازار صادرات و فروکش حق بیمه‌ی هرمز در حال تصحیح‌اند — که فشردگی بیش از ۲۵٪ از لنگر آوریل را تا ۳۱ اوت محتمل‌تر می‌کند. افزایش به حدود ۴۵٪.")


# ---- New questions A6 + B6 -------------------------------------------------
def cm(d):
    """Build an ordered CommentedMap from a plain dict (preserves key order)."""
    from ruamel.yaml.comments import CommentedMap
    m = CommentedMap()
    for k, v in d.items():
        if isinstance(v, list):
            from ruamel.yaml.comments import CommentedSeq
            s = CommentedSeq()
            s.extend(v)
            m[k] = s
        else:
            m[k] = v
    return m


A6 = cm({
    "id": "A6",
    "category": "diplomatic_resolution",
    "question": "Comprehensive/final US-Iran settlement concluded by 2026-09-30",
    "resolution_criterion": LS(
        "YES on a publicly announced comprehensive/final US-Iran settlement (signed agreement or "
        "joint readout) that addresses BOTH nuclear-enrichment limits AND sanctions relief, "
        "concluding the 60-day post-framework negotiation, by 2026-09-30.\n"),
    "deadline": "2026-09-30",
    "baseline_class": "polymarket_or_broad_reference_class",
    "reference_class_strict": "A1_iran_us_framework_strict",
    "reference_class_broad": "A1_bilateral_nuclear_framework_broad",
    "expiration_policy": "agent_judgment_at_deadline",
    "stakeholder_tags": ["us_foreign_policy", "iran_regime_survival", "oil_energy_markets"],
    "current_probability": 0.50,
    "current_credible_interval_80": [0.30, 0.70],
    "current_icd203_label": "roughly_even_chance",
    "last_updated": "2026-06-15",
    "notes": LS(
        "The June 14 MOU is a framework, not the permanent settlement: it defers enrichment, Iran's "
        "~440.9kg 60%-enriched stockpile, sanctions relief, and frozen assets ($24B disputed; the US "
        "calls it pay-for-performance) to a 60-day window ending ~mid-August. Polymarket prices a "
        "permanent peace deal by Aug 31 at ~98% but 'Iran ends enrichment by July 31' at only ~43% — "
        "so a comprehensive final settlement by Sep 30 is roughly a coin-flip.\n"),
    "question_fa": "تسویه‌ی جامع/نهایی ایران و آمریکا تا ۳۰ سپتامبر ۲۰۲۶ منعقد شود",
    "notes_fa": LS(
        "تفاهم‌نامه‌ی ۱۴ ژوئن یک چارچوب است، نه تسویه‌ی دائمی: غنی‌سازی، ذخیره‌ی حدود ۴۴۰.۹ کیلوگرمی "
        "اورانیوم ۶۰٪، رفع تحریم و دارایی‌های مسدود (۲۴ میلیارد دلار مورد مناقشه) را به پنجره‌ی ۶۰ روزه‌ی "
        "پایان‌یابنده در میانه‌ی اوت موکول می‌کند. پلی‌مارکت صلح دائمی تا ۳۱ اوت را ~۹۸٪ ولی «پایان "
        "غنی‌سازی تا ۳۱ ژوئیه» را تنها ~۴۳٪ می‌داند — پس تسویه‌ی جامع تا ۳۰ سپتامبر تقریباً شیر-یا-خط است.\n"),
    "successors_on_resolve_yes": [
        "Does Iran's enrichment stay capped per the settlement through 2026-12-31?",
        "Does the US lift the first sanctions tranche by the stated deadline?",
    ],
})

B6 = cm({
    "id": "B6",
    "category": "military_escalation",
    "question": "2026 Iran-US ceasefire holds (no major kinetic resumption) through 2026-08-31",
    "resolution_criterion": LS(
        "YES if no major kinetic resumption — a US/Israel strike on Iranian territory, OR an Iranian "
        "strike on US/Israeli targets, attributed and confirmed by >=2 Tier-1 sources — occurs between "
        "2026-06-15 and 2026-08-31. Resolves NO on the first such event.\n"),
    "deadline": "2026-08-31",
    "baseline_class": "reference_class",
    "reference_class_strict": None,
    "reference_class_broad": None,
    "expiration_policy": "agent_judgment_at_deadline",
    "stakeholder_tags": ["regional_security", "us_foreign_policy", "oil_energy_markets"],
    "current_probability": 0.70,
    "current_credible_interval_80": [0.50, 0.85],
    "current_icd203_label": "likely",
    "last_updated": "2026-06-15",
    "notes": LS(
        "Trump announced a 60-day ceasefire extension June 11 and the June 14 MOU pledges 'immediate "
        "and permanent termination of military operations on all fronts, including Lebanon'; the truce "
        "has held since, but the May-June record (the June 7-8 Iran-Israel missile exchange) shows "
        "fragility, and Iran still holds its HEU stockpile. Likely to hold through the window (~70%).\n"),
    "question_fa": "آتش‌بس ایران و آمریکا (بدون از‌سرگیری بزرگ نظامی) تا ۳۱ اوت ۲۰۲۶ دوام بیاورد",
    "notes_fa": LS(
        "ترامپ در ۱۱ ژوئن تمدید ۶۰ روزه‌ی آتش‌بس را اعلام کرد و تفاهم‌نامه‌ی ۱۴ ژوئن «پایان فوری و دائمی "
        "عملیات نظامی در همه‌ی جبهه‌ها از جمله لبنان» را تعهد می‌کند؛ آتش‌بس از آن زمان برقرار مانده ولی "
        "کارنامه‌ی مه-ژوئن (تبادل موشکی ۷ تا ۸ ژوئن ایران و اسرائیل) شکنندگی را نشان می‌دهد. احتمالاً تا "
        "پایان پنجره دوام می‌آورد (~۷۰٪).\n"),
    "successors_on_resolve_no": [
        "Does the framework deal formally collapse within 14d of a kinetic resumption?",
    ],
})


# ---------------------------------------------------------------------------
def apply():
    data = yaml.load(PORTFOLIO.read_text(encoding="utf-8"))
    questions = data["questions"]

    # 1) Update existing questions in place
    by_id = {q["id"]: q for q in questions}
    for qid, u in U.items():
        q = by_id[qid]
        q["current_probability"] = u["p"]
        q["current_credible_interval_80"] = list(u["ci"])
        q["current_icd203_label"] = label_for(u["p"])
        q["last_updated"] = "2026-06-15"
        q["notes"] = LS(u["en"] + "\n")
        q["notes_fa"] = LS(u["fa"] + "\n")
        if u["status"]:
            q["status"] = u["status"]
            q["resolution_date"] = u["rdate"]

    # 2) Insert A6 after A5, B6 after B5
    def index_of(qid):
        for i, q in enumerate(questions):
            if q["id"] == qid:
                return i
        raise KeyError(qid)
    questions.insert(index_of("A5") + 1, A6)
    questions.insert(index_of("B5") + 1, B6)

    # 3) Metadata: counts + review dates
    md = data["metadata"]
    md["last_full_review"] = "2026-06-15"
    md["next_review"] = "2026-07-15"
    md["total_questions"] = len(questions)
    md["by_category"]["diplomatic_resolution"] = 6
    md["by_category"]["military_escalation"] = 6

    # 4) Editorial frame (deal-era)
    md["economic_war_frame"]["en"]["title"] = "The frame: a negotiated off-ramp — political deal first, physical and nuclear normalization later"
    md["economic_war_frame"]["en"]["body"] = LS(FRAME_EN_BODY)
    md["economic_war_frame"]["en"]["map_to_questions"] = LS(FRAME_EN_MAP)
    md["economic_war_frame"]["fa"]["title"] = "چارچوب: یک خروج مذاکره‌شده — اول توافق سیاسی، سپس عادی‌سازی فیزیکی و هسته‌ای"
    md["economic_war_frame"]["fa"]["body"] = LS(FRAME_FA_BODY)
    md["economic_war_frame"]["fa"]["map_to_questions"] = LS(FRAME_FA_MAP)

    # 5) Base case (deal-era), full + public, EN + FA
    md["base_case"]["en"]["full"] = LS(BASECASE_EN_FULL)
    md["base_case"]["en"]["public"] = LS(BASECASE_EN_PUBLIC)
    md["base_case"]["fa"]["full"] = LS(BASECASE_FA_FULL)
    md["base_case"]["fa"]["public"] = LS(BASECASE_FA_PUBLIC)
    md["base_case"]["last_updated"] = "2026-06-15"

    # 6) Deal tracker (new metadata block)
    md["deal_tracker"] = DEAL_TRACKER

    yaml.dump(data, PORTFOLIO.open("w", encoding="utf-8"))
    print(f"applied: {len(U)} updates, +A6/+B6 → {len(questions)} questions")


# ---- Long-form prose (kept at bottom for readability) ---------------------
FRAME_EN_BODY = """After 100-plus days, the 2026 Iran-US war is ending by deal, not by exhaustion. On June 14 Trump declared a framework "complete"; Iran's Deputy FM Gharibabadi confirmed it, with a formal signing set for June 19 in Switzerland. The agreement immediately halts the fighting "on all fronts, including Lebanon," lifts the US naval blockade, and reopens the Strait of Hormuz toll-free — with a 60-day window to negotiate a permanent settlement. The economic-war frame that defined the spring (Iran's Hormuz closure versus Washington's blockade and sanctions) didn't end in a knockout; it ended at the table.

But "deal" is doing a lot of work. Three clocks now run at different speeds. The political deal is fastest — signing, blockade-lift, a declared ceasefire. Physical normalization is slower: Hormuz transit was still a trickle (~2-6 ships/day versus ~135 pre-war) in mid-June, and mine-clearing could take up to six months, so the shipping recovery lags the announcement. Slowest is the nuclear-and-sanctions file: enrichment, Iran's ~440kg 60%-enriched stockpile, sanctions relief, and a disputed $24B in frozen assets were all deferred to the 60-day talks — and the US zero-enrichment demand is exactly the rock the spring's diplomacy kept hitting.

So the live risk is no longer "does the economic war escalate to a shooting war" — that already happened and then stopped. It is "does the framework convert into a durable settlement, or relapse." The war's hardest fact is now fixed: Ali Khamenei was killed on Feb 28 and his son Mojtaba runs Iran as an invisible, contested Supreme Leader. The questions below are re-sorted around the new phase: what has resolved, what the 60-day window decides, and where the off-ramp could still break.
"""

FRAME_EN_MAP = """The diplomatic cards (A) now measure whether the framework hardens into a permanent deal. The military cards (B) are mostly resolved — they record what the war already did — with B6 tracking whether the ceasefire holds. The economic cards (D) unwound their war premium. The regime cards (C) recorded a forced succession. The US-side cards (E) measure Trump's standing into the midterms.
"""

FRAME_FA_BODY = """پس از بیش از صد روز، جنگ ۲۰۲۶ ایران و آمریکا با توافق پایان می‌یابد، نه با فرسایش. در ۱۴ ژوئن ترامپ یک چارچوب را «کامل» اعلام کرد؛ قریب‌آبادی معاون وزیر خارجه‌ی ایران آن را تأیید کرد و امضای رسمی برای ۱۹ ژوئن در سوئیس تعیین شد. توافق بی‌درنگ جنگ را «در همه‌ی جبهه‌ها از جمله لبنان» متوقف می‌کند، محاصره‌ی دریایی آمریکا را برمی‌دارد، و تنگه‌ی هرمز را بدون عوارض بازمی‌گشاید — با پنجره‌ی ۶۰ روزه برای مذاکره‌ی یک تسویه‌ی دائمی. چارچوب جنگ اقتصادیِ بهار با ضربه‌ی فنی پایان نیافت؛ سرِ میز پایان یافت.

اما «توافق» بار زیادی بر دوش دارد. اکنون سه ساعت با سرعت‌های متفاوت کار می‌کنند. توافق سیاسی سریع‌ترین است — امضا، رفع محاصره، آتش‌بس اعلام‌شده. عادی‌سازی فیزیکی کندتر است: تردد هرمز در میانه‌ی ژوئن هنوز ناچیز بود (حدود ۲ تا ۶ کشتی در روز در برابر ۱۳۵ پیش‌از‌جنگ) و مین‌روبی می‌تواند تا شش ماه طول بکشد. کندترین، پرونده‌ی هسته‌ای و تحریم است: غنی‌سازی، ذخیره‌ی حدود ۴۴۰ کیلوگرمی اورانیوم ۶۰٪، رفع تحریم و ۲۴ میلیارد دلار دارایی مسدودِ مورد مناقشه، همه به مذاکرات ۶۰ روزه موکول شدند — و مطالبه‌ی توقف کامل غنی‌سازیِ آمریکا همان سنگی است که دیپلماسیِ بهار مدام به آن می‌خورد.

پس ریسک زنده دیگر «آیا جنگ اقتصادی به جنگ نظامی تشدید می‌شود» نیست — این رخ داد و سپس متوقف شد. ریسک این است که «آیا چارچوب به تسویه‌ی پایدار تبدیل می‌شود یا عود می‌کند». سخت‌ترین واقعیت جنگ اکنون تثبیت شده: علی خامنه‌ای در ۲۸ فوریه کشته شد و پسرش مجتبی ایران را به‌عنوان رهبری نامرئی و مورد مناقشه اداره می‌کند. پرسش‌های پایین حول فاز تازه بازچینش شده‌اند: چه چیزی قطعی شده، پنجره‌ی ۶۰ روزه چه تصمیمی می‌گیرد، و خروج کجا هنوز می‌تواند بشکند.
"""

FRAME_FA_MAP = """کارت‌های دیپلماتیک (الف) اکنون می‌سنجند که آیا چارچوب به توافق دائمی سفت می‌شود. کارت‌های نظامی (ب) عمدتاً قطعی شده‌اند — آنچه جنگ انجام داد را ثبت می‌کنند — و B6 دوام آتش‌بس را دنبال می‌کند. کارت‌های اقتصادی (د) حق بیمه‌ی جنگ خود را باز کردند. کارت‌های نظام (ج) یک جانشینی اجباری را ثبت کردند. کارت‌های سمت آمریکا (ه) جایگاه ترامپ را تا انتخابات میان‌دوره‌ای می‌سنجند.
"""

BASECASE_EN_FULL = """The war is ending by agreement. On June 14 the US and Iran reached a framework (an MOU Trump called the deal "complete"); Iran's Deputy FM Gharibabadi confirmed it and a formal signing is set for June 19 in Switzerland. The deal halts fighting on all fronts including Lebanon, lifts the US naval blockade, reopens the Strait of Hormuz toll-free, and opens a 60-day window to negotiate a permanent settlement — with enrichment, Iran's ~440kg 60%-enriched stockpile, sanctions relief, and a disputed ~$24B in frozen assets all deferred to those talks. Markets have already priced the off-ramp: Brent fell ~20% off its 2026 peak to ~$84, US gas retraced from a $4.564 May peak to ~$4.07, and the rial strengthened to ~1.62M (it never crossed 2M). Base case for the next 60 days: the signing holds, the ceasefire holds (fragile but intact since the June 11 extension), Hormuz physically reopens on a weeks-to-months mine-clearing timeline rather than instantly, and the nuclear talks grind — with the US zero-enrichment demand the most likely thing to stall a permanent deal. The regime story is settled the hard way: Ali Khamenei was killed Feb 28 and his son Mojtaba leads Iran, unseen in public. On the family-business side: Iranfarhang books keep clearing under the Berman Amendment as the sanctions climate eases; KEMCO SARL payment risk falls but isn't gone until relief is signed and implemented; Kipa's Hormuz-dependent Iran-UAE corridor should reopen on the mine-clearing timeline.
"""

BASECASE_EN_PUBLIC = """The war is ending by agreement. On June 14 the US and Iran reached a framework (an MOU Trump called the deal "complete"); Iran's Deputy FM Gharibabadi confirmed it and a formal signing is set for June 19 in Switzerland. The deal halts fighting on all fronts including Lebanon, lifts the US naval blockade, reopens the Strait of Hormuz toll-free, and opens a 60-day window to negotiate a permanent settlement — with enrichment, Iran's ~440kg 60%-enriched stockpile, sanctions relief, and a disputed ~$24B in frozen assets all deferred to those talks. Markets have already priced the off-ramp: Brent fell ~20% off its 2026 peak to ~$84, US gas retraced from a $4.564 May peak to ~$4.07, and the rial strengthened to ~1.62M (it never crossed 2M). Base case for the next 60 days: the signing holds, the ceasefire holds (fragile but intact since the June 11 extension), Hormuz physically reopens on a weeks-to-months mine-clearing timeline rather than instantly, and the nuclear talks grind — with the US zero-enrichment demand the most likely thing to stall a permanent deal. The regime story is settled the hard way: Ali Khamenei was killed Feb 28 and his son Mojtaba leads Iran, unseen in public.
"""

BASECASE_FA_FULL = """جنگ با توافق پایان می‌یابد. در ۱۴ ژوئن آمریکا و ایران به یک چارچوب رسیدند (تفاهم‌نامه‌ای که ترامپ آن را «کامل» خواند)؛ قریب‌آبادی معاون وزیر خارجه‌ی ایران تأیید کرد و امضای رسمی برای ۱۹ ژوئن در سوئیس تعیین شد. توافق جنگ را در همه‌ی جبهه‌ها از جمله لبنان متوقف می‌کند، محاصره‌ی دریایی آمریکا را برمی‌دارد، هرمز را بدون عوارض بازمی‌گشاید، و پنجره‌ی ۶۰ روزه‌ای برای مذاکره‌ی تسویه‌ی دائمی می‌گشاید — با موکول‌شدن غنی‌سازی، ذخیره‌ی حدود ۴۴۰ کیلوگرمی اورانیوم ۶۰٪، رفع تحریم و حدود ۲۴ میلیارد دلار دارایی مسدودِ مورد مناقشه به آن مذاکرات. بازارها خروج را قیمت‌گذاری کرده‌اند: برنت حدود ۲۰٪ از سقف ۲۰۲۶ افت کرد به حدود ۸۴ دلار، بنزین آمریکا از سقف ۴.۵۶۴ دلاری مه به حدود ۴.۰۷ دلار بازگشت، و ریال به حدود ۱.۶۲ میلیون تقویت شد (هرگز از ۲ میلیون عبور نکرد). خط پایه برای ۶۰ روز آینده: امضا برقرار می‌ماند، آتش‌بس (شکننده ولی پابرجا از تمدید ۱۱ ژوئن) دوام می‌آورد، هرمز به‌جای آنی در بازه‌ی هفته‌تا‌ماهِ مین‌روبی فیزیکی بازمی‌شود، و مذاکرات هسته‌ای کند پیش می‌رود — با مطالبه‌ی توقف غنی‌سازیِ آمریکا محتمل‌ترین مانعِ توافق دائمی. داستان نظام به سخت‌ترین شکل تثبیت شده: علی خامنه‌ای در ۲۸ فوریه کشته شد و پسرش مجتبی ایران را رهبری می‌کند، نادیده در ملأ عام. در سمت کسب‌وکار خانوادگی: کتاب‌های ایران‌فرهنگ ذیل متمم برمن همچنان ترخیص می‌شوند؛ ریسک پرداخت Kemco SARL کاهش می‌یابد ولی تا امضا و اجرای تسهیل از بین نمی‌رود؛ کریدور ایران-اماراتِ کیپا وابسته به هرمز باید در بازه‌ی مین‌روبی بازگشایی شود.
"""

BASECASE_FA_PUBLIC = """جنگ با توافق پایان می‌یابد. در ۱۴ ژوئن آمریکا و ایران به یک چارچوب رسیدند (تفاهم‌نامه‌ای که ترامپ آن را «کامل» خواند)؛ قریب‌آبادی معاون وزیر خارجه‌ی ایران تأیید کرد و امضای رسمی برای ۱۹ ژوئن در سوئیس تعیین شد. توافق جنگ را در همه‌ی جبهه‌ها از جمله لبنان متوقف می‌کند، محاصره‌ی دریایی آمریکا را برمی‌دارد، هرمز را بدون عوارض بازمی‌گشاید، و پنجره‌ی ۶۰ روزه‌ای برای مذاکره‌ی تسویه‌ی دائمی می‌گشاید — با موکول‌شدن غنی‌سازی، ذخیره‌ی حدود ۴۴۰ کیلوگرمی اورانیوم ۶۰٪، رفع تحریم و حدود ۲۴ میلیارد دلار دارایی مسدودِ مورد مناقشه به آن مذاکرات. بازارها خروج را قیمت‌گذاری کرده‌اند: برنت حدود ۲۰٪ افت کرد به حدود ۸۴ دلار، بنزین آمریکا از سقف ۴.۵۶۴ دلاری مه به حدود ۴.۰۷ دلار بازگشت، و ریال به حدود ۱.۶۲ میلیون تقویت شد (هرگز از ۲ میلیون عبور نکرد). خط پایه برای ۶۰ روز آینده: امضا و آتش‌بس (شکننده ولی پابرجا) دوام می‌آورند، هرمز در بازه‌ی هفته‌تا‌ماهِ مین‌روبی بازمی‌شود، و مذاکرات هسته‌ای کند پیش می‌رود. علی خامنه‌ای در ۲۸ فوریه کشته شد و پسرش مجتبی ایران را رهبری می‌کند، نادیده در ملأ عام.
"""


def _deal_items_en():
    return [
        dict(label="Framework MOU reached", status="done", date="2026-06-14",
             detail="Trump declared the deal 'complete'; Iran's Deputy FM Gharibabadi confirmed."),
        dict(label="Formal signing — Switzerland", status="pending", date="2026-06-19",
             detail="Electronic signing ceremony; MOU text to be published on signing."),
        dict(label="US naval blockade lifted", status="progress", date="2026-06-14",
             detail="Trump authorized immediate removal; full lift staged over ~30 days."),
        dict(label="Strait of Hormuz reopened toll-free", status="progress", date=None,
             detail="Political reopening ordered; physical traffic recovery gated by mine-clearing (up to ~6 months)."),
        dict(label="Ceasefire on all fronts (incl. Lebanon)", status="progress", date="2026-06-11",
             detail="60-day extension announced June 11; truce fragile but holding."),
        dict(label="60-day window → permanent settlement", status="pending", date=None,
             detail="Targets ~mid-August; success hinges on the enrichment dispute."),
        dict(label="Nuclear file: enrichment & ~440kg 60% HEU", status="deferred", date=None,
             detail="Deferred to follow-on talks; IAEA re-engagement and stockpile accounting unresolved."),
        dict(label="Sanctions relief & frozen assets", status="deferred", date=None,
             detail="Crude-export waivers promised on signing; $24B asset release disputed (US: pay-for-performance)."),
    ]


def _deal_items_fa():
    return [
        dict(label="حصول تفاهم‌نامه‌ی چارچوبی", status="done", date="2026-06-14",
             detail="ترامپ توافق را «کامل» خواند؛ قریب‌آبادی معاون وزیر خارجه‌ی ایران تأیید کرد."),
        dict(label="امضای رسمی — سوئیس", status="pending", date="2026-06-19",
             detail="مراسم امضای الکترونیکی؛ متن تفاهم‌نامه هنگام امضا منتشر می‌شود."),
        dict(label="رفع محاصره‌ی دریایی آمریکا", status="progress", date="2026-06-14",
             detail="ترامپ دستور حذف فوری داد؛ رفع کامل طی حدود ۳۰ روز."),
        dict(label="بازگشایی بدون‌عوارض تنگه‌ی هرمز", status="progress", date=None,
             detail="بازگشایی سیاسی صادر شد؛ بازیابی تردد فیزیکی منوط به مین‌روبی (تا حدود ۶ ماه)."),
        dict(label="آتش‌بس در همه‌ی جبهه‌ها (با لبنان)", status="progress", date="2026-06-11",
             detail="تمدید ۶۰ روزه در ۱۱ ژوئن اعلام شد؛ آتش‌بس شکننده ولی پابرجا."),
        dict(label="پنجره‌ی ۶۰ روزه ← تسویه‌ی دائمی", status="pending", date=None,
             detail="هدف حدود میانه‌ی اوت؛ موفقیت به اختلاف غنی‌سازی بستگی دارد."),
        dict(label="پرونده‌ی هسته‌ای: غنی‌سازی و ~۴۴۰ کیلوگرم اورانیوم ۶۰٪", status="deferred", date=None,
             detail="موکول به مذاکرات بعدی؛ بازگشت آژانس و شمارش ذخیره حل‌نشده."),
        dict(label="رفع تحریم و دارایی‌های مسدود", status="deferred", date=None,
             detail="معافیت صادرات نفت هنگام امضا وعده داده شد؛ آزادسازی ۲۴ میلیارد دلار مورد مناقشه."),
    ]


def _items_seq(items):
    from ruamel.yaml.comments import CommentedSeq
    s = CommentedSeq()
    for it in items:
        s.append(cm(it))
    return s


DEAL_TRACKER = cm({
    "en": cm({
        "title": "June 14 framework — implementation tracker",
        "as_of": "2026-06-15",
        "items": _items_seq(_deal_items_en()),
    }),
    "fa": cm({
        "title": "توافق چارچوبی ۱۴ ژوئن — رصد اجرا",
        "as_of": "2026-06-15",
        "items": _items_seq(_deal_items_fa()),
    }),
})


if __name__ == "__main__":
    apply()
