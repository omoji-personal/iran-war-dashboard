/* ============================================================
   Iran War Dashboard v2 — dashboard.js
   ============================================================ */

/* ---------- UI Dictionary (en + fa) ---------- */
const UI = {
  en: {
    title: "Iran War Dashboard",
    subtitle: "Predictive conflict analysis: capability models, convergence vectors, oil shock, and business impact.",
    chipUpdate: "Last data update:",
    chipFresh: "Freshness:",
    chipWindow: "Data window:",
    langLabel: "فارسی",
    kickerTheory: "Working theory",
    hSitrep: "Situation Report",
    subSitrep: "",
    hMissile: "Daily ballistic missile launches",
    subMissile: "Daily counts, not cumulative. Trend line included.",
    hDrone: "Daily drone launches",
    subDrone: "Daily counts, not cumulative.",
    hCombo: "Combined launch tempo",
    subCombo: "Missiles and drones together — converging or diverging?",
    hCumul: "Cumulative strikes",
    subCumul: "Running total of all projectiles launched since Day 1.",
    hOil: "Oil shock monitor",
    subOil: "Brent and WTI benchmark pressure.",
    hPressure: "Attrition vs cost pressure",
    subPressure: "Strategic hinge — operational degradation vs economic/political cost.",
    hTargetM: "Latest daily missile strikes by target",
    subTarget: "Latest daily slice — who's being hit?",
    hTargetD: "Latest daily drone strikes by target",
    subTargetD: "Theater narrowing or spreading?",
    hCasualties: "Casualty tracker",
    subCasualties: "Multi-source figures — discrepancies noted.",
    hHumanitarian: "Humanitarian crisis",
    subHumanitarian: "Infrastructure, displacement, and civilian impact.",
    hDiplomacy: "Diplomacy & negotiations",
    subDiplomacy: "Peace proposals, intermediaries, and positions.",
    hPublicOpinion: "Public opinion",
    subPublicOpinion: "US polling and international reaction.",
    hHormuz: "Hormuz Strait & safe passage",
    subHormuz: "Blockade status, mine fields, and transit frameworks.",
    hKeyActors: "Key actors & alliances",
    subKeyActors: "Who's involved and their roles.",
    hImpact: "Impact",
    hPrep: "Preparation priorities",
    hSignals: "Signals to watch",
    hPublishing: "Iranian publishing industry status",
    hLog: "Event log",
    subLog: "Newest first.",
    thDate: "Date",
    thMissiles: "Daily ballistic missiles",
    thDrones: "Daily drones",
    thPrimary: "Primary target distribution",
    thCap: "Capability read",
    thCost: "Cost / escalation read",
    thAssess: "Assessment",
    hTimeline: "Projected timeline",
    hScenario: "Scenario probabilities",
    hTheoryEval: "Working theory evaluation",
    // New v2 keys
    kickerPrediction: "War outcome forecast",
    convergence: "Resolution pressure:",
    kickerThesis: "Capability thesis",
    hThesis: "Depleted or Rationing?",
    subThesis: "Two models of Iran's launch tempo — each implies a different war outcome. Dashed lines = 14-day forecast.",
    kickerVectors: "Resolution pressure",
    hVectors: "War-Ending Pressure Index",
    subVectors: "All vectors normalized: higher = more pressure to end the war. Resolution likely when 3+ vectors exceed 7.",
    hOilOverlay: "Oil price vs conflict intensity",
    subOilOverlay: "Dual axis: are markets responding to military tempo or diplomatic signals?",
    hGeoSpread: "Geographic spread index",
    subGeoSpread: "Countries targeted per day — is the theater expanding or contracting?",
    hMDRatio: "Missile-to-drone ratio",
    subMDRatio: "Ratio shift signals stockpile depletion — below 0.5 = drone-dominant warfare.",
    hIntercept: "Intercept rate trends",
    subIntercept: "Defense degradation signal — are allied air defenses holding?",
    hScenarioTrend: "Scenario probability trends",
    subScenarioTrend: "How outcome probabilities have shifted since Day 1.",
    hSupplyTimeline: "Supply chain recovery timeline",
    hRoutes: "Route viability",
    hPublishingDeep: "Publishing deep dive",
    hAltHubs: "Alternative hub comparison",
    hHormuzTimeline: "Hormuz reopening timeline",
    hInsurance: "Insurance cost index",
    vecMilitary: "Military Exhaustion",
    vecEconomic: "Economic Pain",
    vecDiplomatic: "Diplomatic Momentum",
    vecPolitical: "US Domestic Pressure",
    vecEscalation: "Escalation Risk"
  },
  fa: {
    title: "داشبورد جنگ ایران",
    subtitle: "تحلیل پیش‌بینی: مدل‌های توانمندی، بردارهای همگرایی، بحران نفت، و تأثیر بر کسب‌وکار.",
    chipUpdate: "آخرین به‌روزرسانی:",
    chipFresh: "تازگی:",
    chipWindow: "بازه داده:",
    langLabel: "English",
    kickerTheory: "فرضیه فعلی",
    hSitrep: "گزارش وضعیت",
    subSitrep: "مختصر و مستند.",
    hMissile: "پرتاب روزانه موشک بالستیک",
    subMissile: "شمارش روزانه، نه تجمعی. خط روند شامل.",
    hDrone: "پرتاب روزانه پهپاد",
    subDrone: "شمارش روزانه، نه تجمعی.",
    hCombo: "شدت ترکیبی پرتاب",
    subCombo: "موشک و پهپاد — همگرا یا واگرا؟",
    hCumul: "حملات تجمعی",
    subCumul: "مجموع کل پرتاب‌ها از روز اول.",
    hOil: "مانیتور بحران نفت",
    subOil: "فشار بنچمارک برنت و WTI.",
    hPressure: "فرسایش در برابر فشار هزینه",
    subPressure: "لولای راهبردی — تخریب عملیاتی در برابر هزینه اقتصادی/سیاسی.",
    hTargetM: "حملات موشکی روزانه بر حسب هدف",
    subTarget: "آخرین برش روزانه — چه کسی هدف است؟",
    hTargetD: "حملات پهپادی روزانه بر حسب هدف",
    subTargetD: "صحنه جنگ تنگ‌تر یا گسترده‌تر؟",
    hCasualties: "ردیاب تلفات",
    subCasualties: "ارقام چند منبعی — اختلافات ذکر شده.",
    hHumanitarian: "بحران انسانی",
    subHumanitarian: "زیرساخت، آوارگی و تأثیر بر غیرنظامیان.",
    hDiplomacy: "دیپلماسی و مذاکرات",
    subDiplomacy: "پیشنهادات صلح، میانجی‌ها و مواضع.",
    hPublicOpinion: "افکار عمومی",
    subPublicOpinion: "نظرسنجی آمریکا و واکنش بین‌المللی.",
    hHormuz: "تنگه هرمز و عبور امن",
    subHormuz: "وضعیت محاصره، میدان مین و چارچوب ترانزیت.",
    hKeyActors: "بازیگران کلیدی و اتحادها",
    subKeyActors: "چه کسانی دخیل‌اند و نقش آنها.",
    hImpact: "تأثیر",
    hPrep: "اولویت‌های آمادگی",
    hSignals: "سیگنال‌های رصد",
    hPublishing: "وضعیت صنعت نشر ایران",
    hLog: "گزارش رویدادها",
    subLog: "جدیدترین ابتدا.",
    thDate: "تاریخ",
    thMissiles: "موشک بالستیک روزانه",
    thDrones: "پهپاد روزانه",
    thPrimary: "توزیع هدف اصلی",
    thCap: "خوانش توانمندی",
    thCost: "خوانش هزینه / تشدید",
    thAssess: "ارزیابی",
    hTimeline: "جدول زمانی پیش‌بینی",
    hScenario: "احتمال سناریوها",
    hTheoryEval: "ارزیابی فرضیه فعلی",
    // New v2 keys
    kickerPrediction: "پیش‌بینی نتیجه جنگ",
    convergence: "همگرایی:",
    kickerThesis: "فرضیه توانمندی",
    hThesis: "اتمام یا جیره‌بندی؟",
    subThesis: "دو مدل شدت پرتاب ایران — هر کدام نتیجه متفاوت. خطوط خط‌چین = پیش‌بینی ۱۴ روزه.",
    kickerVectors: "بردارهای پیش‌بینی",
    hVectors: "همگرایی ۵ بردار",
    subVectors: "جنگ وقتی تمام می‌شود که ۳+ بردار همزمان از آستانه عبور کنند. هر کدام ۰-۱۰.",
    hOilOverlay: "نفت در برابر شدت درگیری",
    subOilOverlay: "محور دوگانه: بازارها به شدت نظامی واکنش نشان می‌دهند یا سیگنال‌های دیپلماتیک؟",
    hGeoSpread: "شاخص گسترش جغرافیایی",
    subGeoSpread: "کشورهای هدف در روز — صحنه جنگ گسترش یا انقباض؟",
    hMDRatio: "نسبت موشک به پهپاد",
    subMDRatio: "تغییر نسبت = اتمام ذخیره — زیر ۰.۵ = جنگ پهپاد‌محور.",
    hIntercept: "روند نرخ رهگیری",
    subIntercept: "سیگنال فرسایش دفاعی — آیا پدافند متحدین دوام دارد؟",
    hScenarioTrend: "روند احتمال سناریوها",
    subScenarioTrend: "چگونه احتمال‌ها از روز اول تغییر کرده‌اند.",
    hSupplyTimeline: "جدول زمانی بازیابی زنجیره تأمین",
    hRoutes: "قابلیت مسیرها",
    hPublishingDeep: "تحلیل عمیق نشر",
    hAltHubs: "مقایسه هاب‌های جایگزین",
    hHormuzTimeline: "جدول بازگشایی هرمز",
    hInsurance: "شاخص هزینه بیمه",
    vecMilitary: "فرسایش نظامی",
    vecEconomic: "فشار اقتصادی",
    vecDiplomatic: "شتاب دیپلماتیک",
    vecPolitical: "پایداری سیاسی آمریکا",
    vecEscalation: "فاصله سقف تشدید"
  }
};

/* ---------- State Management & Utilities ---------- */
let currentLang = 'en';
let currentMode = 'ceasefire';
const CEASEFIRE_START_IDX = 39; // 1-indexed war day where ceasefire begins (Apr 7)
let dashboardMounted = false;
let state = {};
const charts = {};

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('.mode-btn').forEach(function(b) {
    b.classList.toggle('active', b.getAttribute('data-mode') === mode);
  });
  document.body.classList.toggle('ceasefire-mode', mode === 'ceasefire');
  document.body.classList.toggle('war-mode', mode === 'war');
  // Destroy ceasefire charts when leaving ceasefire mode to prevent memory leak
  if (mode === 'war') {
    kill('cfViolation'); kill('cfHormuzRecovery'); kill('cfOilRecovery');
  }
  render();
}
window.setMode = setMode;

const DEFAULT_DATA = {
  meta: { lastUpdated: '', notes: [] },
  theoryBox: '', theoryBox_fa: '',
  metrics: [], metrics_fa: [],
  sitrep: [], sitrep_fa: [],
  dailySeries: { labels: [], missiles: [], drones: [], sourceLabel: '', throughDate: '' },
  oil: { labels: [], brent: [], wti: [], note: '' },
  pressure: { labels: [], attrition: [], cost: [] },
  latestTargetBreakdown: { note: '', missiles: {}, drones: {} },
  dailyRows: [],
  timeline: [], timeline_fa: [],
  scenarioProbabilities: [], scenarioProbabilities_fa: [],
  theoryEvaluation: [], theoryEvaluation_fa: [],
  endstate: [], endstate_fa: [],
  shippingRoutes: [], shippingRoutes_fa: [],
  publishingStatus: [], publishingStatus_fa: [],
  impactIranfarhang: [], impactIranfarhang_fa: [],
  prepIranfarhang: [], prepIranfarhang_fa: [],
  signalsIranfarhang: [], signalsIranfarhang_fa: [],
  impactKIP: [], impactKIP_fa: [],
  prepKIP: [], prepKIP_fa: [],
  signalsKIP: [], signalsKIP_fa: [],
  humanitarian: [], humanitarian_fa: [],
  diplomacy: [], diplomacy_fa: [],
  publicOpinion: [], publicOpinion_fa: [],
  hormuz: [], hormuz_fa: [],
  keyActors: [], keyActors_fa: [],
  predictive: {},
  additionalCharts: {},
  iranfarhangExpanded: {},
  kipExpanded: {},
  ceasefireStartIdx: 39,
  ceasefireMode: { enabled: false },
  ceasefireViolations: [],
  ceasefireNegotiations: [],
  ceasefireEconomicRecovery: { labels: [], hormuzDaily: [], hormuzPreWar: 135, brentPreCeasefire: 109, brentDaily: [] },
  ceasefirePostConflictTree: { branchExtend: [], branchDeal: [], branchCollapse: [], branchStalled: [] }
};

function toggleLang() {
  currentLang = currentLang === 'en' ? 'fa' : 'en';
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'fa' ? 'rtl' : 'ltr';
  var btn = document.getElementById('langToggle');
  if (btn) btn.textContent = UI[currentLang].langLabel;
  render();
}

function applyI18n() {
  var s = UI[currentLang];
  document.querySelectorAll('[data-i18n]').forEach(function(el) {
    var key = el.getAttribute('data-i18n');
    if (s[key] !== undefined) el.textContent = s[key];
  });
  document.querySelectorAll('[data-i18n-html]').forEach(function(el) {
    var key = el.getAttribute('data-i18n-html');
    if (s[key] !== undefined) el.innerHTML = sanitizeHTML(s[key]);
  });
}

function computeFreshness() {
  var ts = state.meta && state.meta.lastUpdated;
  if (!ts) return { label: '—', cls: 'warn' };
  var diff = (Date.now() - new Date(ts).getTime()) / 36e5;
  if (diff <= 12) return { label: currentLang === 'fa' ? 'به\u200cروز' : 'Current', cls: 'good' };
  if (diff <= 48) return { label: currentLang === 'fa' ? 'کمی قدیمی' : 'Aging', cls: 'warn' };
  return { label: currentLang === 'fa' ? 'قدیمی' : 'Stale', cls: 'bad' };
}

function parseLogDate(d) {
  if (!d) return 0;
  var months = {Jan:0,Feb:1,Mar:2,Apr:3,May:4,Jun:5,Jul:6,Aug:7,Sep:8,Oct:9,Nov:10,Dec:11};
  var parts = String(d).trim().split(/\s+/);
  if (parts.length >= 2 && months[parts[0]] !== undefined) {
    // Prefer the year encoded in meta.lastUpdated; fall back to current year.
    var stamp = (state.meta && state.meta.lastUpdated) ? new Date(state.meta.lastUpdated) : new Date();
    var year = isNaN(stamp.getTime()) ? new Date().getFullYear() : stamp.getFullYear();
    return new Date(year, months[parts[0]], parseInt(parts[1], 10) || 1).getTime();
  }
  if (/^\d{4}-\d{2}-\d{2}/.test(d)) return new Date(d).getTime();
  return 0;
}

function kill(key) {
  if (charts[key]) { charts[key].destroy(); charts[key] = null; }
}

// Safe text escaping — prevent XSS from data-driven content
function esc(str) {
  if (str == null) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Sanitize HTML: allowlist of safe tags for formatted data-driven content
function sanitizeHTML(str) {
  if (str == null) return '';
  // Allow only: <strong>, <br>, <span style="...">, <em>
  return String(str)
    .replace(/<(?!\/?(?:strong|br|em|span)\b)[^>]*>/gi, '')
    .replace(/on\w+\s*=/gi, '');
}

function L(key) {
  var faKey = key + '_fa';
  if (currentLang === 'fa' && state[faKey] && state[faKey].length) return state[faKey];
  return state[key] || [];
}

function $(id) { return document.getElementById(id); }

function renderList(id, items) {
  var el = $(id);
  if (!el) return;
  if (!items || !items.length) { el.innerHTML = ''; return; }
  el.innerHTML = items.map(function(t) { return '<li>' + sanitizeHTML(t) + '</li>'; }).join('');
}

function deepClone(obj) { return JSON.parse(JSON.stringify(obj)); }

function lastRealIndex(arr) {
  for (var i = arr.length - 1; i >= 0; i--) {
    if (arr[i] !== null && arr[i] !== undefined) return i;
  }
  return -1;
}

function trendLineUpToLastReal(data) {
  var last = lastRealIndex(data);
  if (last < 1) return data.map(function() { return null; });
  // Use only last 14 days for regression to show CURRENT trend, not war-long trend
  var windowSize = 14;
  var start = Math.max(0, last - windowSize + 1);
  var out = [];
  var sum = 0, sumX = 0, sumXY = 0, sumX2 = 0, n = 0;
  for (var i = start; i <= last; i++) {
    if (data[i] !== null && data[i] !== undefined) {
      sum += data[i]; sumX += i; sumXY += i * data[i]; sumX2 += i * i; n++;
    }
  }
  if (n < 2) return data.map(function() { return null; });
  var slope = (n * sumXY - sumX * sum) / (n * sumX2 - sumX * sumX);
  var intercept = (sum - slope * sumX) / n;
  // Only draw trend line for the window period
  for (var j = 0; j < data.length; j++) {
    out.push(j >= start && j <= last ? Math.max(0, Math.round((slope * j + intercept) * 10) / 10) : null);
  }
  return out;
}

const BASE_OPTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#eef5fc', font: { size: 11 } } },
    tooltip: { mode: 'index', intersect: false }
  },
  scales: {
    x: { ticks: { color: '#9eb5d0', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,.04)' } },
    y: { ticks: { color: '#9eb5d0', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,.06)' } }
  }
};

/* ---------- Mount Dashboard from Template ---------- */
function mountDashboard() {
  if (dashboardMounted) return;
  var tpl = $('dashboardTemplate');
  var shell = $('mainShell');
  if (!tpl || !shell) return;
  var loadMsg = $('loadingMsg');
  if (loadMsg) loadMsg.remove();
  shell.appendChild(tpl.content.cloneNode(true));
  dashboardMounted = true;
}

/* ---------- setText() — populate all text/list sections ---------- */
function setText() {
  // Last updated chip
  var ts = state.meta && state.meta.lastUpdated;
  if ($('lastUpdated') && ts) {
    var d = new Date(ts);
    var est = d.toLocaleString('en-US', { timeZone: 'America/New_York', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
    var teh = d.toLocaleString('en-US', { timeZone: 'Asia/Tehran', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true });
    $('lastUpdated').innerHTML = est + ' <span style="color:var(--muted)">ET</span> / ' + teh + ' <span style="color:var(--muted)">Tehran</span>';
  } else if ($('lastUpdated')) {
    $('lastUpdated').textContent = '\u2014';
  }
  var fr = computeFreshness();
  if ($('freshnessStatus')) {
    $('freshnessStatus').innerHTML = '<span class="tag ' + fr.cls + '">' + fr.label + '</span>';
  }
  if ($('seriesThrough')) $('seriesThrough').textContent = state.dailySeries.throughDate || '—';

  // About-panel ceasefire date range — derived from data, not hardcoded
  var rangeEl = $('cfAboutRange');
  if (rangeEl) {
    var cfLabels = (state.dailySeries || {}).labels || [];
    var startLabel = cfLabels[(state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1];
    var endIso = (state.ceasefireDeadline || {}).deadline;
    var endLabel = '';
    if (endIso) {
      var ed = new Date(endIso);
      if (!isNaN(ed.getTime())) {
        endLabel = ed.toLocaleString('en-US', { month: 'short', day: 'numeric' });
      }
    }
    if (startLabel && endLabel) rangeEl.textContent = startLabel + '–' + endLabel;
  }

  // Theory box
  var theory = currentLang === 'fa' ? (state.theoryBox_fa || state.theoryBox) : state.theoryBox;
  if ($('theoryBox')) $('theoryBox').innerHTML = sanitizeHTML(theory || '');

  // Metrics grid — first 4 computed from data, rest from JSON
  var metricsArr = currentLang === 'fa' ? (state.metrics_fa && state.metrics_fa.length ? state.metrics_fa : state.metrics) : state.metrics;
  if ($('metrics') && metricsArr) {
    var ds = state.dailySeries || {};
    var missiles = ds.missiles || [];
    var drones = ds.drones || [];
    var totalM = missiles.reduce(function(a,b){return a+b;}, 0);
    var totalD = drones.reduce(function(a,b){return a+b;}, 0);
    var latestBrent = (state.oil.brent || []).slice(-1)[0] || 0;

    // Override first 4 metric values with computed data
    var computed = metricsArr.map(function(m, i) {
      var copy = { label: m.label, value: m.value, desc: m.desc };
      if (i === 0) copy.value = String(missiles.length); // Day count
      if (i === 1) copy.value = '~' + totalM.toLocaleString(); // Cumul missiles
      if (i === 2) copy.value = '~' + totalD.toLocaleString(); // Cumul drones
      if (i === 3) copy.value = '$' + latestBrent; // Oil
      return copy;
    });

    $('metrics').innerHTML = computed.map(function(m) {
      return '<div class="metric"><div class="label">' + m.label + '</div>' +
        '<div class="value">' + m.value + '</div>' +
        '<div class="desc">' + m.desc + '</div></div>';
    }).join('');
  }

  // SITREP
  renderList('sitrep', L('sitrep'));

  // Source notes — compact: just show first note (date/source line)
  if ($('sourceNotes') && state.meta && state.meta.notes && state.meta.notes.length) {
    var firstNote = state.meta.notes[0];
    // Truncate to first sentence or 200 chars
    var short = firstNote.length > 200 ? firstNote.substring(0, 200) + '...' : firstNote;
    $('sourceNotes').innerHTML = '<div>' + esc(short) + '</div>';
  }

  // Footnotes
  if ($('missileFoot')) $('missileFoot').textContent = state.dailySeries.sourceLabel || '';
  if ($('droneFoot')) $('droneFoot').textContent = state.dailySeries.sourceLabel || '';
  if ($('oilFoot')) $('oilFoot').textContent = state.oil.note || '';

  // Target breakdown footnotes
  if ($('targetMissileFoot')) $('targetMissileFoot').textContent = (state.latestTargetBreakdown && state.latestTargetBreakdown.note) || '';
  if ($('targetDroneFoot')) $('targetDroneFoot').textContent = (state.latestTargetBreakdown && state.latestTargetBreakdown.note) || '';

  // Humanitarian, diplomacy, public opinion, hormuz, key actors
  renderList('humanitarianBox', L('humanitarian'));
  renderList('diplomacyBox', L('diplomacy'));
  renderList('publicOpinionBox', L('publicOpinion'));
  renderList('hormuzBox', L('hormuz'));
  renderList('keyActorsBox', L('keyActors'));

  // Shipping routes (standalone in Hormuz section) — render as route cards
  var routes = L('shippingRoutes');
  if ($('shippingRoutesStandalone') && routes.length) {
    $('shippingRoutesStandalone').innerHTML = routes.map(function(r) {
      if (typeof r === 'string') return '<div class="route-card"><div class="route-detail">' + esc(r) + '</div></div>';
      return '<div class="route-card"><div class="route-header"><div class="route-name">' + esc(r.route || '') + '</div>' +
        '<span class="route-status ' + esc(r.statusColor || 'yellow') + '">' + esc(r.status || '') + '</span></div>' +
        '<div class="route-detail">' + esc(r.detail || '') + '</div>' +
        '<div class="route-meta"><span>' + (currentLang === 'fa' ? 'قابلیت: ' : 'Viability: ') + '<strong>' + esc(r.viability || '') + '</strong></span>' +
        '<span>' + (currentLang === 'fa' ? 'زمان: ' : 'ETA: ') + '<strong>' + esc(r.eta || '') + '</strong></span></div></div>';
    }).join('');
  }

  // Business impact lists
  renderList('impactIranfarhang', L('impactIranfarhang'));
  renderList('prepIranfarhang', L('prepIranfarhang'));
  renderList('signalsIranfarhang', L('signalsIranfarhang'));
  renderList('publishingStatusBox', L('publishingStatus'));
  renderList('impactKIP', L('impactKIP'));
  renderList('prepKIP', L('prepKIP'));
  renderList('signalsKIP', L('signalsKIP'));

  // Daily rows (event log table)
  if ($('dailyRows') && state.dailyRows) {
    var rows = state.dailyRows.slice().sort(function(a, b) { return parseLogDate(b.date) - parseLogDate(a.date); });
    var tbody = $('dailyRows');
    tbody.innerHTML = rows.map(function(r) {
      var p = r.primary || '\u2014', c = r.capability || '\u2014', co = r.cost || '\u2014', a = r.assessment || '\u2014';
      return '<tr><td>' + esc(r.date) + '</td><td><span class="pill missile">' + (r.missiles != null ? esc(r.missiles) : '\u2014') + '</span></td><td><span class="pill drone">' + (r.drones != null ? esc(r.drones) : '\u2014') + '</span></td>' +
        '<td title="' + esc(p) + '">' + sanitizeHTML(p) + '</td>' +
        '<td title="' + esc(c) + '">' + sanitizeHTML(c) + '</td>' +
        '<td title="' + esc(co) + '">' + sanitizeHTML(co) + '</td>' +
        '<td title="' + esc(a) + '">' + sanitizeHTML(a) + '</td></tr>';
    }).join('');
    // Bind click-to-expand once (re-renders preserve the binding via dataset flag)
    if (!tbody.dataset.expandBound) {
      tbody.addEventListener('click', function(e) {
        var tr = e.target && e.target.closest('tr');
        if (tr && tbody.contains(tr)) tr.classList.toggle('expanded');
      });
      tbody.dataset.expandBound = '1';
    }
  }

  // Timeline (array of {title, body} objects)
  var tl = L('timeline');
  if ($('timeline') && tl.length) {
    $('timeline').innerHTML = tl.map(function(t) {
      if (typeof t === 'string') return '<li>' + sanitizeHTML(t) + '</li>';
      return '<li><strong>' + esc(t.title || '') + ':</strong> ' + sanitizeHTML(t.body || '') + '</li>';
    }).join('');
  }

  // Scenario probabilities
  var sp = L('scenarioProbabilities');
  if ($('scenarioProbs') && sp.length) {
    $('scenarioProbs').innerHTML = sp.map(function(s) {
      return '<div class="scenario"><div><strong>' + esc(s.name) + '</strong><div style="font-size:12px;color:var(--soft);margin-top:4px;line-height:1.45">' + sanitizeHTML(s.body) + '</div></div><div class="prob">' + esc(s.prob) + '</div></div>';
    }).join('');
  }

  // Theory evaluation (array of {title, body} objects)
  var te = L('theoryEvaluation');
  if ($('theoryEval') && te.length) {
    $('theoryEval').innerHTML = te.map(function(t) {
      if (typeof t === 'string') return '<li>' + sanitizeHTML(t) + '</li>';
      return '<li><strong>' + esc(t.title || '') + ':</strong> ' + sanitizeHTML(t.body || '') + '</li>';
    }).join('');
  }
}

/* ---------- renderCharts() — 8 original charts ---------- */
function renderCharts() {
  var ds = state.dailySeries;
  var labels = ds.labels || [];
  var missiles = ds.missiles || [];
  var drones = ds.drones || [];

  // 1. Missile chart
  kill('missile');
  if ($('missileChart')) {
    var mOpts = deepClone(BASE_OPTS);
    mOpts.scales.y.beginAtZero = true;
    charts.missile = new Chart($('missileChart'), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          { label: currentLang === 'fa' ? 'موشک بالستیک' : 'Ballistic missiles', data: missiles, backgroundColor: 'rgba(255,107,107,.5)', borderColor: '#ff6b6b', borderWidth: 1, borderRadius: 4 },
          { label: currentLang === 'fa' ? 'خط روند' : 'Trend', data: trendLineUpToLastReal(missiles), type: 'line', borderColor: '#ffd166', borderWidth: 2, pointRadius: 0, tension: .3 }
        ]
      },
      options: mOpts
    });
  }

  // 2. Drone chart
  kill('drone');
  if ($('droneChart')) {
    var dOpts = deepClone(BASE_OPTS);
    dOpts.scales.y.beginAtZero = true;
    charts.drone = new Chart($('droneChart'), {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: drones, backgroundColor: 'rgba(255,159,67,.5)', borderColor: '#ff9f43', borderWidth: 1, borderRadius: 4 },
          { label: currentLang === 'fa' ? 'خط روند' : 'Trend', data: trendLineUpToLastReal(drones), type: 'line', borderColor: '#ffd166', borderWidth: 2, pointRadius: 0, tension: .3 }
        ]
      },
      options: dOpts
    });
  }

  // 3. Combo chart
  kill('combo');
  if ($('comboChart')) {
    var cOpts = deepClone(BASE_OPTS);
    cOpts.scales.y.beginAtZero = true;
    charts.combo = new Chart($('comboChart'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: currentLang === 'fa' ? 'موشک' : 'Missiles', data: missiles, borderColor: '#ff6b6b', backgroundColor: 'rgba(255,107,107,.08)', fill: true, tension: .22, borderWidth: 2.5, pointRadius: 3 },
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: drones, borderColor: '#ff9f43', backgroundColor: 'rgba(255,159,67,.08)', fill: true, tension: .22, borderWidth: 2.5, pointRadius: 3 }
        ]
      },
      options: cOpts
    });
  }

  // 4. Cumulative chart
  kill('cumul');
  if ($('cumulChart')) {
    var cumM = [], cumD = [], runM = 0, runD = 0;
    for (var i = 0; i < missiles.length; i++) { runM += missiles[i]; cumM.push(runM); }
    for (var j = 0; j < drones.length; j++) { runD += drones[j]; cumD.push(runD); }
    var cuOpts = deepClone(BASE_OPTS);
    cuOpts.scales.y.beginAtZero = true;
    charts.cumul = new Chart($('cumulChart'), {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          { label: currentLang === 'fa' ? 'موشک تجمعی' : 'Cumul. missiles', data: cumM, borderColor: '#ff6b6b', borderWidth: 2.5, tension: .22, pointRadius: 2 },
          { label: currentLang === 'fa' ? 'پهپاد تجمعی' : 'Cumul. drones', data: cumD, borderColor: '#ff9f43', borderWidth: 2.5, tension: .22, pointRadius: 2 }
        ]
      },
      options: cuOpts
    });
  }

  // 5. Oil chart
  kill('oil');
  if ($('oilChart') && state.oil.labels) {
    var oOpts = deepClone(BASE_OPTS);
    oOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) { return '$' + v; } };
    charts.oil = new Chart($('oilChart'), {
      type: 'line',
      data: {
        labels: state.oil.labels,
        datasets: [
          { label: 'Brent', data: state.oil.brent, borderColor: '#63b3ff', borderWidth: 2.5, tension: .22, pointRadius: 3 },
          { label: 'WTI', data: state.oil.wti, borderColor: '#ffd166', borderWidth: 2.5, tension: .22, pointRadius: 3 }
        ]
      },
      options: oOpts
    });
  }

  // 6. Target breakdown — missiles (horizontal bar)
  kill('targetMissile');
  if ($('targetMissileChart') && state.latestTargetBreakdown && state.latestTargetBreakdown.missiles) {
    var tm = state.latestTargetBreakdown.missiles;
    var tmEntries = Object.entries(tm).sort(function(a, b) { return b[1] - a[1]; });
    var barOpts = deepClone(BASE_OPTS);
    barOpts.indexAxis = 'y';
    barOpts.plugins.legend = { display: false };
    barOpts.scales = { x: { ticks: { color: '#9eb5d0', precision: 0 }, grid: { color: 'rgba(255,255,255,.05)' }, beginAtZero: true }, y: { ticks: { color: '#9eb5d0' }, grid: { display: false } } };
    charts.targetMissile = new Chart($('targetMissileChart'), {
      type: 'bar',
      data: {
        labels: tmEntries.map(function(e) { return e[0]; }),
        datasets: [{ label: currentLang === 'fa' ? 'موشک' : 'Missiles', data: tmEntries.map(function(e) { return e[1]; }), backgroundColor: 'rgba(255,107,107,.72)', borderRadius: 8, barThickness: 18 }]
      },
      options: barOpts
    });
  }

  // 8. Target breakdown — drones (horizontal bar)
  kill('targetDrone');
  if ($('targetDroneChart') && state.latestTargetBreakdown && state.latestTargetBreakdown.drones) {
    var td = state.latestTargetBreakdown.drones;
    var tdEntries = Object.entries(td).sort(function(a, b) { return b[1] - a[1]; });
    var barOpts2 = deepClone(BASE_OPTS);
    barOpts2.indexAxis = 'y';
    barOpts2.plugins.legend = { display: false };
    barOpts2.scales = { x: { ticks: { color: '#9eb5d0', precision: 0 }, grid: { color: 'rgba(255,255,255,.05)' }, beginAtZero: true }, y: { ticks: { color: '#9eb5d0' }, grid: { display: false } } };
    charts.targetDrone = new Chart($('targetDroneChart'), {
      type: 'bar',
      data: {
        labels: tdEntries.map(function(e) { return e[0]; }),
        datasets: [{ label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: tdEntries.map(function(e) { return e[1]; }), backgroundColor: 'rgba(255,159,67,.72)', borderRadius: 8, barThickness: 18 }]
      },
      options: barOpts2
    });
  }
}

/* ============================================================
   DECISION ENGINE — Algorithmic computation from raw indicators
   ============================================================ */

// Compute all 3 decision conditions from raw indicators for a given day index
// overrides: optional object to override per-day indicator values for scenario simulation
function computeEngineForDay(dayIdx, overrides) {
  var de = state.decisionEngine || {};
  var di = de.dailyIndicators || {};
  var ds = state.dailySeries || {};
  if (!di.labels || dayIdx < 0 || dayIdx >= di.labels.length) return null;
  var ov = overrides || {};

  var baselines = ((state.meta || {}).preWarBaselines) || {};
  var d1Missiles = ds.missiles[0] || baselines.d1Missiles || 480;
  var preWarOil = baselines.preWarOil || 65;
  var preWarHormuz = baselines.preWarHormuz || 62;
  var preWarGas = baselines.preWarGas || 3;

  // Raw inputs for this day (overrides take precedence)
  var launchRate = ov.launchRate !== undefined ? ov.launchRate : (di.launchRate[dayIdx] || 0);
  var brent = ov.oilBrent !== undefined ? ov.oilBrent : (di.oilBrent[dayIdx] || 65);
  var hormuz = ov.hormuzVessels !== undefined ? ov.hormuzVessels : (di.hormuzVessels[dayIdx] || 0);
  var kia = ov.usKIA !== undefined ? ov.usKIA : (di.usKIA[dayIdx] || 0);
  var gas = ov.gasPrice !== undefined ? ov.gasPrice : (di.gasPrice[dayIdx] || preWarGas);
  var approval = ov.approvalWrong !== undefined ? ov.approvalWrong : (di.approvalWrong[dayIdx] || 35);
  var mediators = ov.mediatorMeetings !== undefined ? ov.mediatorMeetings : (di.mediatorMeetings[dayIdx] || 0);
  var coalition = ov.coalitionScore !== undefined ? ov.coalitionScore : (di.coalitionScore[dayIdx] || 9);
  var day = dayIdx + 1;

  // === DEAL AVAILABILITY (0-1) ===
  var mediatorScore = Math.min(mediators / 5, 1);
  // Use per-day indicators if available, fallback to static
  var proposalsRejected = ov.proposalsRejected !== undefined ? ov.proposalsRejected : (di.proposalsRejected ? di.proposalsRejected[dayIdx] : ((de.indicators || {}).formalProposalsRejected || 0));
  var proposalScore = proposalsRejected > 1 ? 0.05 : proposalsRejected > 0 ? 0.15 : 0.4;
  var faceSaving = mediators >= 4 ? 0.3 : mediators >= 2 ? 0.15 : 0.05; // More mediators = more likely face-saving deal emerges
  var dealScore = mediatorScore * 0.35 + proposalScore * 0.3 + faceSaving * 0.35;
  dealScore = Math.max(0.02, Math.min(dealScore, 0.95));

  // === TRUMP FOLLOW-THROUGH (needed by exitNarrative) ===
  var tp = de.trumpPattern || {};
  var trumpFollows = tp.posteriorFollowThrough || 0.30;

  // === US EXIT PRESSURE (0-1) ===
  var approvalPressure = Math.min((approval - 30) / 40, 1);
  var kiaPressure = Math.min(kia / 30, 1);
  var gasPressure = Math.min((gas - preWarGas) / 3, 1);
  var durationFatigue = Math.min(day / 60, 1);
  // Exit narrative: mediators active + Trump signaling a deal pathway
  var exitNarrative = mediators >= 3 ? 0.4 : 0.2;
  if (trumpFollows > 0.3) exitNarrative += 0.05;
  exitNarrative = Math.min(exitNarrative, 0.5);
  // Coalition contribution: (coalition-7)/3 * 0.1, so 9->0.067, 3->-0.133
  var coalitionPressure = ((coalition - 7) / 3) * 0.1;
  var usExitScore = approvalPressure * 0.25 + kiaPressure * 0.2 + gasPressure * 0.2 + durationFatigue * 0.15 + exitNarrative * 0.1 - coalitionPressure;
  usExitScore = Math.max(0.05, Math.min(usExitScore, 0.95));

  // === IRAN ACCEPTANCE (0-1) ===
  var rateDrop = 1 - (launchRate / d1Missiles);
  var hormuzLeverage = 1 - (hormuz / preWarHormuz);
  var regimePressure = Math.min((kia > 0 ? 0.3 : 0) + rateDrop * 0.3, 0.6);
  // Per-day rejection with recovery: rejected today = 0.05; rejected in last 5 days = stay low;
  // no rejection in last 5 days = recover toward 0.2; never rejected = 0.3
  var iranRejectedArr = di.iranRejectedCeasefire;
  var iranRejected = 0;
  var recentRejection = false;
  if (ov.iranRejectedCeasefire !== undefined) {
    iranRejected = ov.iranRejectedCeasefire ? 1 : 0;
    recentRejection = !!iranRejected;
  } else if (iranRejectedArr && iranRejectedArr.length) {
    iranRejected = iranRejectedArr[dayIdx] ? 1 : 0;
    for (var rk = Math.max(0, dayIdx - 5); rk <= dayIdx; rk++) {
      if (iranRejectedArr[rk]) { recentRejection = true; break; }
    }
  } else {
    iranRejected = ((de.indicators || {}).iranRejectedCeasefire) ? 1 : 0;
    recentRejection = !!iranRejected;
  }
  var rejectedFactor;
  if (iranRejected) rejectedFactor = 0.05;
  else if (recentRejection) rejectedFactor = 0.1; // still cooling off
  else rejectedFactor = 0.3;
  // Recovery path: if no rejection in last 5 days, recover toward 0.2
  if (!iranRejected && !recentRejection) rejectedFactor = 0.2;
  var iranScore = rejectedFactor * 0.4 + regimePressure * 0.3 + (1 - hormuzLeverage) * 0.2 + dealScore * 0.1;
  iranScore = Math.max(0.02, Math.min(iranScore, 0.95));

  // === ESCALATION PROXIMITY (0-1) ===
  var deadlineDays = ov.deadlineDays !== undefined ? ov.deadlineDays : (di.deadlineDays ? di.deadlineDays[dayIdx] : ((de.indicators || {}).daysToDeadline));
  if (deadlineDays === undefined || deadlineDays === null) {
    // Try computing from actual deadline timestamp in meta
    var deadlineIso = (state.meta || {}).deadlineIso || (de.indicators || {}).deadlineIso;
    if (deadlineIso) {
      var delta = (new Date(deadlineIso).getTime() - Date.now()) / 86400000;
      deadlineDays = delta < 0 ? 0 : delta;
    } else {
      deadlineDays = 30;
    }
  }
  // If deadline is in the past, max pressure (powerGridProx = 0.9)
  var powerGridProx;
  if (deadlineDays <= 0) {
    powerGridProx = 0.9;
  } else {
    powerGridProx = Math.max(0, 1 - deadlineDays / 7);
  }
  var nuclearProx = ((de.indicators || {}).nuclearFacilitiesStruck || 0) / ((de.indicators || {}).nuclearFacilitiesTotal || 6);
  var groundProx = Math.min(((de.indicators || {}).groundTroopsDeployed || 0) / 15000, 1);
  var chokeProx = (de.indicators || {}).babAlMandabThreatened ? 0.6 : 0;
  var escScore = Math.max(powerGridProx, nuclearProx, groundProx, chokeProx);

  // === OUTCOME PROBABILITIES ===
  var pNegotiated = dealScore * usExitScore * iranScore;
  // Escalation = P(deadline passes) × P(trump follows through) × P(no deal)
  var pEscalation = escScore * trumpFollows * (1 - pNegotiated);
  var pProtracted = Math.max(0, 1 - pNegotiated - pEscalation - 0.17);
  var pIntervention = 0.10;
  var pOther = Math.max(0, 1 - pNegotiated - pEscalation - pProtracted - pIntervention);

  // Normalize to 100%
  var total = pNegotiated + pEscalation + pProtracted + pIntervention + pOther;
  if (total > 0) {
    pNegotiated /= total; pEscalation /= total; pProtracted /= total; pIntervention /= total; pOther /= total;
  }

  // === ENSEMBLE ===
  var modelProb = Math.round(pNegotiated * 100);
  var cal = de.calibration || {};
  var marketProb = cal.polymarketCeasefire || modelProb;
  var baseRate = (cal.historicalBaseRate || {}).value || 35;
  var ensemble = Math.round(modelProb * 0.4 + marketProb * 0.3 + baseRate * 0.3);

  return {
    dealScore: dealScore,
    usExitScore: usExitScore,
    iranScore: iranScore,
    escScore: escScore,
    trumpFollows: trumpFollows,
    pNegotiated: pNegotiated,
    pEscalation: pEscalation,
    pProtracted: pProtracted,
    pIntervention: pIntervention,
    pOther: pOther,
    modelProb: modelProb,
    marketProb: marketProb,
    baseRate: baseRate,
    ensemble: ensemble,
    day: day
  };
}

/* ============================================================
   Ceasefire Engine — computeCeasefireForDay(dayIdx)
   ============================================================ */
function parseDayDate(dayIdx) {
  var labels = (state.dailySeries || {}).labels || [];
  var label = labels[dayIdx] || '';
  if (!label) return Date.now();
  return new Date(label + ' 2026').getTime();
}

function getCeasefireDay(dayIdx) {
  var startIdx = (state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1; // 0-indexed
  return dayIdx - startIdx + 1; // Apr 7 (idx 38) = CF Day 1
}

/* Single source of truth: derive cfDay from a "Mon DD" label string,
   ignoring any stored cfDay field on the JSON entry (they drift). */
function cfDayFromLabel(label) {
  var labels = (state.dailySeries || {}).labels || [];
  var idx = labels.indexOf(label);
  if (idx < 0) return null;
  return getCeasefireDay(idx);
}

// Smooth sigmoid for continuous thresholds (replaces binary cliff effects)
function cfSigmoid(x, midpoint, steepness) {
  return 1 / (1 + Math.exp(-steepness * (x - midpoint)));
}

function computeCeasefireForDay(dayIdx) {
  var de = state.decisionEngine || {};
  var di = de.dailyIndicators || {};
  var cd = state.ceasefireDeadline || {};
  var startIdx = (state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1;
  if (dayIdx < startIdx) return null;

  var cfDay = dayIdx - startIdx + 1; // Apr 7 = CF Day 1

  // Raw inputs
  var violations = (di.cfViolations || [])[dayIdx] || 0;
  var severity = (di.cfViolationSeverity || [])[dayIdx] || 0;
  var mediator = (di.cfMediatorScore || [])[dayIdx] || 0;
  var hormuzPct = (di.cfHormuzPct || [])[dayIdx] || 0;
  var oilDelta = (di.cfOilDelta || [])[dayIdx] || 0;
  var diplomatic = (di.cfDiplomaticScore || [])[dayIdx] || 0;
  var usPolitical = (di.cfUsPoliticalScore || [])[dayIdx] || 0;
  var iranPolitical = (di.cfIranPoliticalScore || [])[dayIdx] || 0;
  var proxyEsc = (di.cfProxyEscalation || [])[dayIdx] || 0;

  // Days remaining to expiry
  var deadlineMs = new Date(cd.deadline || '2026-04-21T20:00:00-04:00').getTime();
  var dayDate = parseDayDate(dayIdx);
  var daysRemaining = Math.max(0, (deadlineMs - dayDate) / 86400000);

  // === STABILITY SCORE — P(ceasefire holds through expiry) ===
  var violationPenalty = Math.min(violations * 0.08 + severity * 0.05, 0.6);
  var mediatorBoost = mediator / 10 * 0.25;
  var hormuzSignal = hormuzPct / 100 * 0.2;
  var oilSignal = oilDelta < -10 ? 0.15 : oilDelta < 0 ? 0.08 : 0;
  var diplomaticBoost = diplomatic / 10 * 0.2;
  var proxyPenalty = proxyEsc / 10 * 0.15;
  // Smooth time pressure: ramps from 0 at 7+ days to 0.15 at 0 days
  var timeDecay = Math.max(0, 0.15 * cfSigmoid(7 - daysRemaining, 3, 1.0));

  var stabilityBase = 0.5 + mediatorBoost + hormuzSignal + oilSignal + diplomaticBoost
                      - violationPenalty - proxyPenalty - timeDecay;
  var pHolds = Math.max(0.05, Math.min(0.95, stabilityBase));

  // === P(EXTENDED) — smooth sigmoid thresholds ===
  var extensionSignals = cfSigmoid(mediator, 7, 1.5) * 0.2
                       + cfSigmoid(diplomatic, 6, 1.5) * 0.15
                       + cfSigmoid(hormuzPct, 30, 0.1) * 0.1
                       + cfSigmoid(usPolitical, 6, 1.5) * 0.1;
  var pExtended = pHolds * Math.min(0.7, extensionSignals + 0.15);

  // === P(PERMANENT DEAL) — smooth sigmoid thresholds ===
  var dealSignals = cfSigmoid(diplomatic, 8, 1.5) * 0.15
                  + cfSigmoid(mediator, 8, 1.5) * 0.1
                  + cfSigmoid(iranPolitical, 6, 1.5) * 0.15
                  + cfSigmoid(usPolitical, 7, 1.5) * 0.1
                  + cfSigmoid(hormuzPct, 50, 0.08) * 0.1;
  var pDeal = pHolds * Math.min(0.5, dealSignals + 0.05);

  // === P(COLLAPSE) ===
  var pCollapse = 1 - pHolds;

  // Normalize: collapse + holdsNoProgress + extended + deal = 1
  var pHoldsNoProgress = Math.max(0, pHolds - pExtended - pDeal);
  var total = pCollapse + pHoldsNoProgress + pExtended + pDeal;
  if (total > 0) {
    pCollapse /= total; pHoldsNoProgress /= total; pExtended /= total; pDeal /= total;
  }

  // Ensemble with market data
  var cal = de.ceasefireCalibration || {};
  var modelStability = Math.round(pHolds * 100);
  var marketStability = cal.polymarketCeasefireHolds || modelStability;
  var baseRateCf = cal.historicalCeasefireBaseRate || 50;
  var ensemble = Math.round(modelStability * 0.5 + marketStability * 0.3 + baseRateCf * 0.2);

  // === BOTTLENECK: single factor most responsible for stability ===
  var factorImpacts = [
    { name: 'violations', impact: -violationPenalty, label: 'ceasefire violations' },
    { name: 'proxy', impact: -proxyPenalty, label: 'proxy escalation (Israel-Lebanon)' },
    { name: 'timeDecay', impact: -timeDecay, label: 'expiry deadline pressure' },
    { name: 'mediator', impact: mediatorBoost, label: 'mediator engagement' },
    { name: 'diplomatic', impact: diplomaticBoost, label: 'diplomatic signals' },
    { name: 'hormuz', impact: hormuzSignal, label: 'Hormuz reopening progress' },
    { name: 'oil', impact: oilSignal, label: 'oil price normalization' }
  ];
  factorImpacts.sort(function(a, b) { return Math.abs(b.impact) - Math.abs(a.impact); });
  var bnf = factorImpacts[0];
  var bottleneck = bnf.impact < 0
    ? bnf.label + ' is the biggest drag on stability'
    : bnf.label + ' is the primary pillar holding the ceasefire';

  // === NARRATIVE: 1-sentence explanation ===
  var stabPctStr = Math.round(pHolds * 100) + '%';
  var narrative;
  if (pHolds >= 0.6) {
    narrative = 'Ceasefire is holding at ' + stabPctStr + ' stability. ' + bnf.label.charAt(0).toUpperCase() + bnf.label.slice(1) + ' is the key stabilizing factor.';
  } else if (pHolds >= 0.4) {
    narrative = 'Ceasefire is fragile at ' + stabPctStr + ' — ' + bottleneck + '. Collapse risk rising.';
  } else {
    narrative = 'Ceasefire at risk (' + stabPctStr + ') — ' + bottleneck + '. Collapse is the most likely outcome.';
  }

  // === CONFIDENCE BOUNDS: widen when model-market diverge ===
  var modelMarketGap = Math.abs(modelStability - marketStability);
  var halfWidth = Math.max(8, Math.round(modelMarketGap * 0.6 + 6));
  var confidenceLow = Math.max(2, ensemble - halfWidth);
  var confidenceHigh = Math.min(98, ensemble + halfWidth);

  return {
    cfDay: cfDay,
    daysRemaining: daysRemaining,
    pHolds: pHolds,
    pExtended: pExtended,
    pDeal: pDeal,
    pCollapse: pCollapse,
    pHoldsNoProgress: pHoldsNoProgress,
    stabilityScore: ensemble,
    modelStability: modelStability,
    marketStability: marketStability,
    violationPenalty: violationPenalty,
    mediatorBoost: mediatorBoost,
    hormuzSignal: hormuzSignal,
    oilSignal: oilSignal,
    diplomaticBoost: diplomaticBoost,
    proxyPenalty: proxyPenalty,
    timeDecay: timeDecay,
    bottleneck: bottleneck,
    bottleneckFactor: bnf.name,
    narrative: narrative,
    confidenceLow: confidenceLow,
    confidenceHigh: confidenceHigh,
    rawViolations: violations,
    rawSeverity: severity,
    rawMediator: mediator,
    rawDiplomatic: diplomatic,
    rawHormuzPct: hormuzPct
  };
}

/* ============================================================
   CEASEFIRE RENDER FUNCTIONS
   ============================================================ */

function renderCeasefireHero(dayOverride) {
  var labels = (state.dailySeries || {}).labels || [];
  var maxDay = labels.length;
  var dayIdx = (typeof dayOverride === 'number') ? dayOverride : maxDay - 1;
  var eng = computeCeasefireForDay(dayIdx);
  if (!eng) {
    // Pre-ceasefire day — show placeholder
    var heroEl = $('cfStatusDisplay');
    if (heroEl) heroEl.innerHTML = '<div style="font-size:18px;color:var(--muted)">Pre-ceasefire period — switch to War Mode or scrub forward</div>';
    return;
  }

  // Status display — with collapse detection
  var statusEl = $('cfStatusDisplay');
  if (statusEl) {
    // Detect de-facto collapse: ANY non-zero attack OR severity-9 violation
    // in the post-ceasefire-start window that isn't already marked as such.
    var ds = state.dailySeries || {};
    var startIdx = (state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1;
    var postCfAttacks = 0;
    for (var ai = startIdx; ai <= dayIdx; ai++) {
      postCfAttacks += ((ds.missiles || [])[ai] || 0) + ((ds.drones || [])[ai] || 0);
    }
    var severeViolations = (state.ceasefireViolations || []).filter(function(d) {
      return d && d.maxSeverity >= 9;
    }).length;
    var deFactoCollapsed = postCfAttacks > 0 || severeViolations > 0;

    var statusText, statusColor;
    if (deFactoCollapsed) {
      statusText = 'Ceasefire broken';
      statusColor = 'var(--red)';
    } else if (eng.pHolds >= 0.6) { statusText = 'Ceasefire holding'; statusColor = 'var(--cyan)'; }
    else if (eng.pHolds >= 0.4) { statusText = 'Ceasefire fragile'; statusColor = 'var(--gold)'; }
    else { statusText = 'Ceasefire at risk'; statusColor = 'var(--red)'; }

    var collapseBadge = deFactoCollapsed
      ? '<div class="cf-collapse-banner">⚠ De-facto collapse — ' + postCfAttacks + ' post-ceasefire attacks logged; severity-9 violations: ' + severeViolations + '</div>'
      : '';

    statusEl.innerHTML = collapseBadge +
      '<div style="font-size:24px;font-weight:900;color:' + statusColor + '">' + statusText + '</div>' +
      '<div style="font-size:14px;color:var(--muted);margin-top:8px;line-height:1.5">' + esc(eng.narrative) + '</div>';
  }

  // Ensemble probability
  if ($('cfStabilityScore')) $('cfStabilityScore').textContent = eng.stabilityScore + '%';
  if ($('cfStabilityRaw')) {
    var modelColor = eng.modelStability >= 50 ? 'var(--cyan)' : 'var(--red)';
    var marketColor = eng.marketStability >= 50 ? 'var(--cyan)' : 'var(--red)';
    var gap = Math.abs(eng.modelStability - eng.marketStability);
    var convText = gap <= 5 ? ' <span style="color:var(--cyan)">(converging)</span>' : gap >= 15 ? ' <span style="color:var(--red)">(DIVERGING)</span>' : '';
    $('cfStabilityRaw').innerHTML = 'Model: <span style="color:' + modelColor + ';font-weight:700">' + eng.modelStability + '%</span> | Market: <span style="color:' + marketColor + ';font-weight:700">' + eng.marketStability + '%</span> | Historical: 50%' + convText;
  }
  if ($('cfConfidenceRange')) {
    $('cfConfidenceRange').textContent = eng.confidenceLow + '% \u2013 ' + eng.confidenceHigh + '% range';
  }
  if ($('cfProbBar')) {
    $('cfProbBar').style.width = eng.stabilityScore + '%';
    $('cfProbBar').style.background = eng.stabilityScore >= 60 ? 'var(--cyan)' : eng.stabilityScore >= 40 ? 'var(--gold)' : 'var(--red)';
  }

  // Stability factors
  var factorsEl = $('cfStabilityFactors');
  if (factorsEl) {
    var factors = [
      { label: 'Mediator engagement', val: eng.mediatorBoost, max: 0.25, color: 'var(--cyan)', positive: true },
      { label: 'Diplomatic signals', val: eng.diplomaticBoost, max: 0.2, color: 'var(--blue)', positive: true },
      { label: 'Hormuz reopening', val: eng.hormuzSignal, max: 0.2, color: 'var(--gold)', positive: true },
      { label: 'Violation penalty', val: eng.violationPenalty, max: 0.6, color: 'var(--red)', positive: false },
      { label: 'Proxy escalation', val: eng.proxyPenalty, max: 0.15, color: 'var(--orange)', positive: false }
    ];
    var html = '';
    factors.forEach(function(f) {
      var pct = Math.round(f.val / f.max * 100);
      var sign = f.positive ? '+' : '-';
      html += '<div class="cond-row" style="margin-bottom:8px">' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">' +
        '<span>' + f.label + '</span><span style="color:' + f.color + '">' + sign + Math.round(f.val * 100) + '%</span></div>' +
        '<div class="prob-track" style="height:6px"><div class="prob-bar" style="width:' + pct + '%;background:' + f.color + ';height:6px;border-radius:3px"></div></div></div>';
    });
    factorsEl.innerHTML = html;
  }

  // 3-condition breakdown
  var condEl = $('cfConditions');
  if (condEl) {
    var conds = [
      { label: 'Violations stay low', met: eng.violationPenalty < 0.15, detail: esc(eng.rawViolations) + ' violations, severity ' + esc(eng.rawSeverity) + '/10' },
      { label: 'Mediators stay engaged', met: eng.mediatorBoost > 0.12, detail: 'Score ' + esc(eng.rawMediator) + '/10' },
      { label: 'Economic recovery continues', met: eng.hormuzSignal > 0.05, detail: 'Hormuz at ' + esc(eng.rawHormuzPct) + '% of pre-war' }
    ];
    var condHtml = '';
    conds.forEach(function(c) {
      var icon = c.met ? '<span style="color:var(--cyan)">&#x2714;</span>' : '<span style="color:var(--red)">&#x2718;</span>';
      condHtml += '<div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:13px">' +
        icon + '<div><strong>' + esc(c.label) + '</strong><div style="font-size:11px;color:var(--muted)">' + c.detail + '</div></div></div>';
    });
    condEl.innerHTML = condHtml;
  }

  // Outcome breakdown
  var outcomeEl = $('cfOutcomeBreakdown');
  if (outcomeEl) {
    var outcomes = [
      { label: 'Ceasefire extended', pct: Math.round(eng.pExtended * 100), color: 'var(--cyan)' },
      { label: 'Permanent deal', pct: Math.round(eng.pDeal * 100), color: 'var(--blue)' },
      { label: 'Holds but stalled', pct: Math.round(eng.pHoldsNoProgress * 100), color: 'var(--gold)' },
      { label: 'Collapse to war', pct: Math.round(eng.pCollapse * 100), color: 'var(--red)' }
    ];
    var html2 = '';
    outcomes.forEach(function(o) {
      html2 += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:13px">' +
        '<div style="width:36px;text-align:right;font-weight:700;color:' + o.color + '">' + o.pct + '%</div>' +
        '<div class="prob-track" style="flex:1;height:6px"><div class="prob-bar" style="width:' + o.pct + '%;background:' + o.color + ';height:6px;border-radius:3px"></div></div>' +
        '<span>' + o.label + '</span></div>';
    });
    outcomeEl.innerHTML = html2;
  }

  // Metrics
  var metricsEl = $('cfMetrics');
  if (metricsEl) {
    var cfDay = eng.cfDay;
    var di = (state.decisionEngine || {}).dailyIndicators || {};
    var violations = (di.cfViolations || [])[maxDay - 1] || 0;
    var hormuzPct = (di.cfHormuzPct || [])[maxDay - 1] || 0;
    var oilVal = (state.oil || {}).brent || [];
    var latestOil = oilVal[oilVal.length - 1] || 0;
    var items = [
      { label: 'Ceasefire day', value: cfDay + ' / 14', desc: 'Day ' + cfDay + ' of 14-day ceasefire' },
      { label: 'Violations today', value: violations, desc: 'Ceasefire violations reported' },
      { label: 'Hormuz traffic', value: hormuzPct + '%', desc: 'Of pre-war 135 vessels/day' },
      { label: 'Brent crude', value: '$' + latestOil.toFixed(2), desc: 'Pre-ceasefire: $109' }
    ];
    var html3 = '';
    items.forEach(function(m) {
      html3 += '<div class="metric-card"><div class="metric-value">' + m.value + '</div><div class="metric-label">' + m.label + '</div><div class="metric-desc">' + m.desc + '</div></div>';
    });
    metricsEl.innerHTML = html3;
  }
}

var cfDeadlineInterval = null;

// dayOverride: 0-indexed. If provided, show static historical snapshot. If omitted, live ticker.
function renderCeasefireCountdown(dayOverride) {
  var cd = state.ceasefireDeadline || {};
  if (!cd.deadline) return;
  var startIdx = (state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1;
  var labels = (state.dailySeries || {}).labels || [];
  var isHistorical = typeof dayOverride === 'number';
  var refIdx = isHistorical ? dayOverride : labels.length - 1;
  var cfDay = refIdx - startIdx + 1;

  // Countdown display
  var deadline = new Date(cd.deadline);
  if (isHistorical) {
    // Historical: show static remaining time from that day
    if (cfDeadlineInterval) { clearInterval(cfDeadlineInterval); cfDeadlineInterval = null; }
    var dayDate = new Date(parseDayDate(refIdx));
    var diff = deadline - dayDate;
    var el = $('cfCountdown');
    if (el) {
      if (diff <= 0) {
        el.innerHTML = '<span style="color:var(--red)">CEASEFIRE EXPIRED</span>';
      } else {
        var d = Math.floor(diff / 864e5);
        el.textContent = d + 'd remaining (historical)';
      }
    }
  } else {
    // Live: ticking countdown
    function tickCf() {
      var now = new Date();
      var diff = deadline - now;
      var el = $('cfCountdown');
      if (!el) return;
      if (diff <= 0) {
        el.innerHTML = '<span style="color:var(--red)">CEASEFIRE EXPIRED</span>';
        return;
      }
      var days = Math.floor(diff / 864e5);
      var hours = Math.floor((diff % 864e5) / 36e5);
      var mins = Math.floor((diff % 36e5) / 6e4);
      var secs = Math.floor((diff % 6e4) / 1e3);
      el.textContent = days + 'd ' + hours + 'h ' + mins + 'm ' + secs + 's';
    }
    if (cfDeadlineInterval) clearInterval(cfDeadlineInterval);
    tickCf();
    cfDeadlineInterval = setInterval(tickCf, 1000);
  }

  // Compute total ceasefire days dynamically
  var cfStartDate = new Date(parseDayDate(startIdx));
  var totalCfDays = Math.round((deadline - cfStartDate) / 864e5);
  var extensions = cd.extensions || 0;
  if (extensions > 0) totalCfDays += extensions;
  if (totalCfDays < 1) totalCfDays = 14; // fallback

  // Day counter + progress
  if ($('cfDayNum')) $('cfDayNum').textContent = cfDay;
  if ($('cfTotalDays')) $('cfTotalDays').textContent = totalCfDays;
  if ($('cfExtensionNote')) {
    $('cfExtensionNote').innerHTML = extensions > 0 ? ' <span style="color:var(--cyan);font-size:11px">(+' + extensions + ' extension)</span>' : '';
  }
  if ($('cfProgressBar')) $('cfProgressBar').style.width = Math.round(Math.min(cfDay, totalCfDays) / totalCfDays * 100) + '%';

  // Context
  if ($('cfCountdownContext')) {
    var ctx = cd.context || '';
    if (currentLang === 'fa' && cd.context_fa) ctx = cd.context_fa;
    $('cfCountdownContext').innerHTML = sanitizeHTML(ctx);
  }
}

function renderPostConflictTree(dayOverride) {
  var tree = state.ceasefirePostConflictTree || {};
  var labels = (state.dailySeries || {}).labels || [];
  var maxDay = labels.length;
  var dayIdx = (typeof dayOverride === 'number') ? dayOverride : maxDay - 1;

  var eng = computeCeasefireForDay(dayIdx);
  var prevEng = dayIdx > 0 ? computeCeasefireForDay(dayIdx - 1) : null;

  // Branch config: key, element id, engine-prob getter, prob-header id
  var branches = [
    { key: 'branchExtend',   elId: 'cfBranchExtend',   probId: 'cfProbExtend',   getP: function(e){ return e.pExtended; } },
    { key: 'branchDeal',     elId: 'cfBranchDeal',     probId: 'cfProbDeal',     getP: function(e){ return e.pDeal; } },
    { key: 'branchStalled',  elId: 'cfBranchStalled',  probId: 'cfProbStalled',  getP: function(e){ return e.pHoldsNoProgress; } },
    { key: 'branchCollapse', elId: 'cfBranchCollapse', probId: 'cfProbCollapse', getP: function(e){ return e.pCollapse; } }
  ];

  // Compute current + previous probabilities + identify max
  var maxProb = -1, maxKey = '';
  branches.forEach(function(b) {
    b.prob = eng ? Math.round(b.getP(eng) * 100) : null;
    b.prev = prevEng ? Math.round(b.getP(prevEng) * 100) : null;
    if (b.prob != null && b.prob > maxProb) { maxProb = b.prob; maxKey = b.key; }
  });

  // Render header prob + delta + leading-branch highlight
  branches.forEach(function(b) {
    var headEl = document.getElementById(b.probId);
    if (headEl) {
      var probStr = b.prob != null ? b.prob + '%' : '—';
      var deltaHtml = '';
      if (b.prob != null && b.prev != null) {
        var d = b.prob - b.prev;
        if (d > 0) deltaHtml = ' <span class="cf-scenario-delta up">\u2191' + d + 'pp</span>';
        else if (d < 0) deltaHtml = ' <span class="cf-scenario-delta down">\u2193' + Math.abs(d) + 'pp</span>';
      }
      headEl.innerHTML = esc(probStr) + deltaHtml;
    }
    var scenarioEl = document.querySelector('.cf-scenario[data-branch="' + b.key.replace('branch','').toLowerCase() + '"]');
    if (scenarioEl) {
      scenarioEl.classList.toggle('leading', b.key === maxKey);
    }

    // Render body items
    var bodyEl = document.getElementById(b.elId);
    if (!bodyEl) return;
    var items = tree[b.key] || [];
    if (!items.length) {
      bodyEl.innerHTML = '<div class="tl-item partial" style="color:var(--muted);font-style:italic">No scenario path defined yet.</div>';
      return;
    }
    bodyEl.innerHTML = items.map(function(item) {
      return '<div class="tl-item partial"><strong>' + esc(item.step) + '</strong>' +
        '<br><span style="color:var(--muted);font-size:12px">' + esc(item.timeline) + '</span>' +
        '<br><span style="font-size:12px">' + esc(item.detail) + '</span></div>';
    }).join('');
  });
}

function renderViolationTracker() {
  var violations = state.ceasefireViolations || [];
  var di = (state.decisionEngine || {}).dailyIndicators || {};
  var cfViolations = di.cfViolations || [];
  var cfSeverity = di.cfViolationSeverity || [];
  var startIdx = (state.ceasefireStartIdx || CEASEFIRE_START_IDX) - 1;

  // Scope summary
  var summaryEl = $('cfViolationSummary');
  if (summaryEl) {
    var scopeCounts = { yes: 0, disputed: 0, other: 0 };
    violations.forEach(function(day) {
      (day.incidents || []).forEach(function(inc) {
        var s = (inc.withinScope || 'other').toLowerCase();
        if (s === 'yes') scopeCounts.yes++;
        else if (s === 'disputed') scopeCounts.disputed++;
        else scopeCounts.other++;
      });
    });
    // Trend: compare last 2-3 days of violation counts
    var recentCounts = [];
    for (var t = Math.max(startIdx, cfViolations.length - 3); t < cfViolations.length; t++) {
      if (cfViolations[t] != null) recentCounts.push(cfViolations[t]);
    }
    var trendStr = '';
    if (recentCounts.length >= 2) {
      var last = recentCounts[recentCounts.length - 1];
      var prev = recentCounts[recentCounts.length - 2];
      if (last > prev) trendStr = ' <span style="color:var(--red)">\u2191 Rising</span>';
      else if (last < prev) trendStr = ' <span style="color:var(--cyan)">\u2193 Declining</span>';
      else trendStr = ' <span style="color:var(--gold)">\u2192 Stable</span>';
    }
    summaryEl.innerHTML = '<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--muted)">' +
      '<span title="Incidents explicitly covered by the original ceasefire terms (direct fire, Hormuz interference, etc.)">Within scope: <strong style="color:var(--cyan)">' + scopeCounts.yes + '</strong></span>' +
      '<span title="Incidents where parties disagree whether they fall under the ceasefire (e.g. Israel–Lebanon strikes while Iran is technically at truce)">Disputed: <strong style="color:var(--gold)">' + scopeCounts.disputed + '</strong></span>' +
      '<span title="Incidents outside the ceasefire scope (civilian protests, rhetorical threats, 3rd-party actions)">Other: <strong style="color:var(--red)">' + scopeCounts.other + '</strong></span>' +
      '<span>Trend:' + trendStr + '</span></div>';
  }

  // Chart
  kill('cfViolation');
  var canvas = $('cfViolationChart');
  if (canvas) {
    var labels = [];
    var counts = [];
    var colors = [];
    var cumSeverity = [];
    var runningSum = 0;
    for (var i = startIdx; i < cfViolations.length; i++) {
      if (cfViolations[i] === null) continue;
      labels.push('CF Day ' + (i - startIdx + 1));
      counts.push(cfViolations[i] || 0);
      var sev = cfSeverity[i] || 0;
      runningSum += sev;
      cumSeverity.push(runningSum);
      colors.push(sev >= 7 ? '#ff6b6b' : sev >= 4 ? '#ff9f43' : sev > 0 ? '#ffd166' : '#46d7b0');
    }
    charts.cfViolation = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Violations (bar color = max severity)',
          data: counts,
          backgroundColor: colors,
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, ticks: { color: '#9eb5d0', precision: 0 }, grid: { color: 'rgba(41,65,95,.3)' }, title: { display: true, text: 'Incidents per day', color: '#9eb5d0', font: { size: 11 } } },
          x: { ticks: { color: '#9eb5d0' }, grid: { display: false } }
        },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: function(ctx) {
            var sev = cfSeverity[startIdx + ctx.dataIndex] || 0;
            return ctx.parsed.y + ' incident' + (ctx.parsed.y === 1 ? '' : 's') + ' · max severity ' + sev;
          }}}
        }
      }
    });
  }

  // List — grouped by day (one header per day, incidents nested)
  var listEl = $('cfViolationList');
  if (listEl) {
    var html = '';
    // Newest first
    var sortedDays = violations.slice().sort(function(a, b) {
      return parseLogDate(b.day) - parseLogDate(a.day);
    });
    sortedDays.forEach(function(day) {
      var cfD = cfDayFromLabel(day.day);
      var headCfDay = cfD ? ' (CF Day ' + cfD + ')' : '';
      if (!day.incidents || !day.incidents.length) {
        html += '<div class="vday vday-quiet">' +
          '<div class="vday-head"><span class="vday-date">' + esc(day.day) + headCfDay + '</span>' +
          '<span class="vday-count">No violations</span></div></div>';
        return;
      }
      var incCount = day.incidents.length;
      var maxSev = day.incidents.reduce(function(m, i) { return Math.max(m, i.severity || 0); }, 0);
      var dayTone = maxSev >= 7 ? 'severe' : maxSev >= 4 ? 'moderate' : 'minor';
      html += '<div class="vday ' + dayTone + '">' +
        '<div class="vday-head">' +
          '<span class="vday-date">' + esc(day.day) + headCfDay + '</span>' +
          '<span class="vday-count">' + incCount + ' incident' + (incCount === 1 ? '' : 's') + ' · max sev ' + maxSev + '</span>' +
        '</div>' +
        '<div class="vday-body">' +
          day.incidents.map(function(inc) {
            var sevClass = inc.severity >= 7 ? 'severe' : inc.severity >= 4 ? 'moderate' : 'minor';
            var sevLabel = inc.severity >= 7 ? 'SEVERE' : inc.severity >= 4 ? 'MOD' : 'MINOR';
            var desc = currentLang === 'fa' && inc.description_fa ? inc.description_fa : inc.description;
            return '<div class="vincident ' + sevClass + '">' +
              '<div class="vincident-head">' +
                '<span class="vincident-sev">' + sevLabel + '</span>' +
                '<span class="vincident-target"><strong>' + esc(inc.actor) + '</strong> → ' + esc(inc.target) + '</span>' +
                (inc.withinScope ? '<span class="vincident-scope" title="Whether this incident falls under the original ceasefire agreement\'s scope: yes / disputed / no">[' + esc(inc.withinScope) + ']</span>' : '') +
              '</div>' +
              '<div class="vincident-desc">' + esc(desc) + '</div>' +
            '</div>';
          }).join('') +
        '</div>' +
      '</div>';
    });
    if (!html) html = '<div style="color:var(--muted);font-style:italic">No violations recorded yet.</div>';
    listEl.innerHTML = html;
  }
}

function renderNegotiationTracker() {
  var negotiations = state.ceasefireNegotiations || [];
  var el = $('cfNegotiationTimeline');
  if (!el) return;

  var roleMap = {
    'Trump': 'US President',
    'VP Vance': 'US VP/Lead',
    'Witkoff': 'US Envoy',
    'Kushner': 'US Advisor',
    'Ghalibaf': 'Iran Speaker',
    'Araghchi': 'Iran FM',
    'Pakistan PM Sharif': 'Mediator',
    'FM Munir': 'Mediator'
  };

  // Summary card: show latest event status
  var summaryHtml = '';
  if (negotiations.length) {
    var latest = negotiations[negotiations.length - 1];
    var statusBadge = (latest.outcome || 'scheduled').toUpperCase().replace(/_/g, ' ');
    var badgeColor = 'var(--gold)';
    var oc = (latest.outcome || '').toLowerCase();
    if (oc === 'collapsed' || oc === 'negative') badgeColor = 'var(--red)';
    else if (oc === 'breakthrough') badgeColor = 'var(--cyan)';
    else if (oc === 'in_progress') badgeColor = 'var(--blue)';
    var keyGap = latest.keyGap || '';
    summaryHtml = '<div style="border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:14px;background:rgba(255,255,255,.02)">' +
      '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
      '<span style="font-weight:700;font-size:14px">Latest: ' + esc(latest.date) + '</span>' +
      '<span style="background:' + badgeColor + ';color:#fff;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:800">' + esc(statusBadge) + '</span></div>' +
      (keyGap ? '<div style="font-size:12px;color:var(--muted)">Key gap: ' + esc(keyGap) + '</div>' : '') +
      '</div>';
  }

  var html = summaryHtml;
  negotiations.forEach(function(evt) {
    var dotClass = evt.outcome || 'scheduled';
    var eventText = currentLang === 'fa' && evt.event_fa ? evt.event_fa : evt.event;
    // Coerce participants: accept array, comma-separated string, or missing
    var partsArr = Array.isArray(evt.participants)
      ? evt.participants
      : (typeof evt.participants === 'string'
          ? evt.participants.split(/,\s*/).filter(Boolean)
          : []);
    var partDisplay = partsArr.map(function(p) {
      var role = roleMap[p];
      return role ? esc(p) + ' <span style="color:var(--soft);font-size:10px">(' + esc(role) + ')</span>' : esc(p);
    }).join(', ');
    var dateLabel = evt.date || evt.day || '';
    var cfDn = cfDayFromLabel(dateLabel);
    html += '<div class="nego-event">' +
      '<div class="nego-dot ' + esc(dotClass) + '"></div>' +
      '<div style="flex:1">' +
      '<div style="display:flex;justify-content:space-between;align-items:baseline">' +
      '<strong style="font-size:13px">' + esc(dateLabel) + (cfDn ? ' (CF Day ' + cfDn + ')' : '') + '</strong>' +
      '<span style="font-size:11px;color:var(--muted)">' + partDisplay + '</span></div>' +
      '<div style="font-size:13px;margin-top:4px">' + esc(eventText) + '</div>' +
      '</div></div>';
  });
  if (!negotiations.length) html += '<div style="color:var(--muted);font-style:italic">No events recorded yet.</div>';
  el.innerHTML = html;
}

function renderCeasefireRecovery() {
  var rec = state.ceasefireEconomicRecovery || {};
  var labels = rec.labels || [];
  if (!labels.length) return;

  // Recovery metrics summary
  var sumEl = $('cfRecoverySummary');
  if (sumEl) {
    var hormuzData = rec.hormuzDaily || [];
    var preWar = rec.hormuzPreWar || 135;
    var latestVessels = hormuzData.length ? hormuzData[hormuzData.length - 1] : 0;
    var prevVessels = hormuzData.length >= 2 ? hormuzData[hormuzData.length - 2] : latestVessels;
    var recoveryRate = latestVessels - prevVessels;
    var rateStr = (recoveryRate >= 0 ? '+' : '') + recoveryRate.toFixed(1);
    var daysToNormal = recoveryRate > 0 ? Math.ceil((preWar - latestVessels) / recoveryRate) : 0;
    var daysToNormalStr = daysToNormal > 0 && daysToNormal < 999 ? esc(daysToNormal) + ' days' : 'N/A';
    var stranded = rec.shipsStranded || 0;
    sumEl.innerHTML = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px">' +
      '<div style="border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(255,255,255,.02);text-align:center">' +
        '<div style="font-size:22px;font-weight:800;color:var(--cyan)">' + esc(latestVessels) + '</div>' +
        '<div style="font-size:11px;color:var(--muted)">Vessels/day</div></div>' +
      '<div style="border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(255,255,255,.02);text-align:center">' +
        '<div style="font-size:22px;font-weight:800;color:' + (recoveryRate >= 0 ? 'var(--cyan)' : 'var(--red)') + '">' + esc(rateStr) + '</div>' +
        '<div style="font-size:11px;color:var(--muted)">Recovery rate/day</div></div>' +
      '<div style="border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(255,255,255,.02);text-align:center">' +
        '<div style="font-size:22px;font-weight:800;color:var(--gold)">' + daysToNormalStr + '</div>' +
        '<div style="font-size:11px;color:var(--muted)">To normalization</div></div>' +
      '<div style="border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(255,255,255,.02);text-align:center">' +
        '<div style="font-size:22px;font-weight:800;color:var(--orange)">' + esc(stranded) + '</div>' +
        '<div style="font-size:11px;color:var(--muted)">Ships stranded</div></div>' +
      '</div>';
  }

  // Hormuz recovery chart
  kill('cfHormuzRecovery');
  var hCanvas = $('cfHormuzRecoveryChart');
  if (hCanvas) {
    charts.cfHormuzRecovery = new Chart(hCanvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Vessels/day',
            data: rec.hormuzDaily || [],
            borderColor: '#46d7b0', backgroundColor: 'rgba(70,215,176,.1)',
            fill: true, tension: 0.3, pointRadius: 4
          },
          {
            label: 'Pre-war baseline (135)',
            data: labels.map(function() { return rec.hormuzPreWar || 135; }),
            borderColor: 'rgba(158,181,208,.4)', borderDash: [6, 4],
            pointRadius: 0, fill: false
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, max: 150, ticks: { color: '#9eb5d0' }, grid: { color: 'rgba(41,65,95,.3)' } }, x: { ticks: { color: '#9eb5d0' }, grid: { display: false } } },
        plugins: { legend: { labels: { color: '#9eb5d0', font: { size: 11 } } } }
      }
    });
  }

  // Oil recovery chart
  kill('cfOilRecovery');
  var oCanvas = $('cfOilRecoveryChart');
  if (oCanvas) {
    charts.cfOilRecovery = new Chart(oCanvas, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Brent ($/bbl)',
            data: rec.brentDaily || [],
            borderColor: '#63b3ff', backgroundColor: 'rgba(99,179,255,.1)',
            fill: true, tension: 0.3, pointRadius: 4
          },
          {
            label: 'Pre-ceasefire ($109)',
            data: labels.map(function() { return rec.brentPreCeasefire || 109; }),
            borderColor: 'rgba(255,107,107,.4)', borderDash: [6, 4],
            pointRadius: 0, fill: false
          },
          {
            label: 'Pre-war ($65)',
            data: labels.map(function() { return 65; }),
            borderColor: 'rgba(158,181,208,.3)', borderDash: [3, 3],
            pointRadius: 0, fill: false
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { y: { ticks: { color: '#9eb5d0' }, grid: { color: 'rgba(41,65,95,.3)' } }, x: { ticks: { color: '#9eb5d0' }, grid: { display: false } } },
        plugins: { legend: { labels: { color: '#9eb5d0', font: { size: 11 } } } }
      }
    });
  }
}

/* ============================================================
   NEW RENDER FUNCTIONS — Predictive Section
   ============================================================ */

function renderPredictiveSection() {
  var p = state.predictive || {};
  var outcome = p.warOutcome || {};
  var models = p.models || {};
  var vectors = p.vectors || {};
  var de = state.decisionEngine || {};

  // War outcome forecast — generated from engine state
  var maxDay = (state.dailySeries.labels || []).length;
  var eng = computeEngineForDay(maxDay - 1);
  if ($('outcomeForecast') && eng) {
    // Find highest-probability outcome
    var outcomes = [
      { name: 'Escalation', pct: Math.round(eng.pEscalation * 100) },
      { name: 'Protracted continuation', pct: Math.round(eng.pProtracted * 100) },
      { name: 'Negotiated resolution', pct: Math.round(eng.pNegotiated * 100) },
      { name: 'International intervention', pct: Math.round(eng.pIntervention * 100) }
    ];
    outcomes.sort(function(a, b) { return b.pct - a.pct; });
    var top = outcomes[0];
    var second = outcomes[1];

    // Build bottleneck description
    var bottleneck = eng.dealScore < eng.iranScore && eng.dealScore < eng.usExitScore ? 'no viable deal exists' :
      eng.iranScore < eng.dealScore && eng.iranScore < eng.usExitScore ? 'Iran is unwilling to accept terms' :
      'US has not committed to an exit';

    var forecast = '<strong>' + top.name + ' is the most likely outcome (' + top.pct + '%).</strong> ' +
      second.name + ' is second at ' + second.pct + '%. ' +
      'Negotiated resolution is only ' + Math.round(eng.pNegotiated * 100) + '% because ' + bottleneck + '. ' +
      'The combined probability of a deal is ' + eng.modelProb + '% (our model) to ' + eng.ensemble + '% (with market and historical data). ' +
      'Day ' + maxDay + ' of the conflict.';
    $('outcomeForecast').innerHTML = forecast;
  } else if ($('outcomeForecast')) {
    var forecastText = currentLang === 'fa' ? (outcome.prediction_fa || outcome.prediction || '') : (outcome.prediction || '');
    $('outcomeForecast').innerHTML = sanitizeHTML(forecastText);
  }

  // Decision Engine probability display
  renderDecisionEngine(de);

  // Model cards
  renderModelCards(models);

  // Thesis chart (two-model comparison)
  renderThesisChart(models);

  // Vector chart
  renderVectorChart(vectors);

  // Vector cards
  renderVectorCards(p.vectorNotes || {}, vectors);
}

function renderDecisionEngine(de) {
  // Compute from algorithmic engine
  var maxDay = (state.dailySeries.labels || []).length;
  var eng = computeEngineForDay(maxDay - 1);
  if (!eng) return;

  var ensembleProb = eng.ensemble;
  var modelProb = eng.modelProb;
  var marketProb = eng.marketProb;
  var baseRate = eng.baseRate;
  var conf = (de || {}).confidence || {};
  var low = (conf.resolutionProbability || {}).low || Math.max(ensembleProb - 12, 2);
  var high = (conf.resolutionProbability || {}).high || Math.min(ensembleProb + 12, 95);

  // Main probability display
  if ($('convergenceScore')) $('convergenceScore').textContent = ensembleProb + '%';
  if ($('probBar')) {
    $('probBar').style.width = ensembleProb + '%';
    $('probBar').style.background = ensembleProb >= 50 ? 'var(--cyan)' : ensembleProb >= 25 ? 'var(--gold)' : 'var(--red)';
  }
  if ($('convergenceRaw')) $('convergenceRaw').textContent = low + '% – ' + high + '% range';

  // Decision conditions breakdown (from computed engine)
  if ($('decisionConditions')) {
    function condBar(label, score) {
      var pct = Math.round((score || 0) * 100);
      var color = pct >= 60 ? 'var(--cyan)' : pct >= 30 ? 'var(--gold)' : 'var(--red)';
      return '<div class="cond-row">' +
        '<div class="cond-header"><span class="cond-label">' + label + '</span><span class="cond-pct" style="color:' + color + '">' + pct + '%</span></div>' +
        '<div class="prob-track" style="margin:4px 0"><div class="prob-bar" style="width:' + pct + '%;background:' + color + '"></div></div>' +
        '</div>';
    }

    $('decisionConditions').innerHTML =
      condBar('A deal both sides can accept', eng.dealScore) +
      condBar('US decides to take the deal', eng.usExitScore) +
      condBar('Iran agrees to the terms', eng.iranScore) +
      '<div class="cond-formula" style="margin-top:8px">' +
        'Combined: ' + Math.round(eng.dealScore*100) + '% × ' + Math.round(eng.usExitScore*100) + '% × ' + Math.round(eng.iranScore*100) + '% = <strong>' + modelProb + '% chance of negotiated end</strong>' +
      '</div>';
  }

  // Outcome breakdown bars (from computed engine)
  if ($('outcomeBreakdown')) {
    var outcomes = [
      { label: currentLang === 'fa' ? 'تشدید (نیروگاه ۶ آوریل)' : 'Escalation (Apr 6 power grid)', pct: Math.round(eng.pEscalation*100), color: 'var(--red)' },
      { label: currentLang === 'fa' ? 'ادامه فرسایشی' : 'Protracted continuation', pct: Math.round(eng.pProtracted*100), color: 'var(--orange)' },
      { label: currentLang === 'fa' ? 'حل‌وفصل مذاکره‌ای' : 'Negotiated resolution', pct: Math.round(eng.pNegotiated*100), color: 'var(--cyan)' },
      { label: currentLang === 'fa' ? 'مداخله بین‌المللی' : 'International intervention', pct: Math.round(eng.pIntervention*100), color: 'var(--blue)' },
      { label: currentLang === 'fa' ? 'سایر' : 'Other', pct: Math.round(eng.pOther*100), color: 'var(--muted)' }
    ];
    outcomes.sort(function(a, b) { return b.pct - a.pct; });
    $('outcomeBreakdown').innerHTML = outcomes.map(function(o) {
      return '<div class="outcome-row"><div class="outcome-header"><span>' + o.label + '</span><strong style="color:' + o.color + '">' + o.pct + '%</strong></div>' +
        '<div class="prob-track" style="margin:2px 0 6px"><div class="prob-bar" style="width:' + o.pct + '%;background:' + o.color + '"></div></div></div>';
    }).join('');
  }

  // Calibration anchors
  if ($('calibrationAnchors')) {
    $('calibrationAnchors').innerHTML =
      '<div class="cal-row"><span class="cal-label">Our model says</span><strong>' + modelProb + '%</strong></div>' +
      '<div class="cal-row"><span class="cal-label">Betting markets say</span><strong>' + marketProb + '%</strong></div>' +
      '<div class="cal-row"><span class="cal-label">Similar wars in history</span><strong>' + baseRate + '%</strong></div>' +
      '<div class="cal-row cal-ensemble"><span class="cal-label">Combined estimate</span><strong style="color:var(--gold)">' + ensembleProb + '%</strong></div>';
  }
}

function renderThesisChart(models) {
  kill('thesis');
  if (!$('thesisChart') || !models.projectionLabels) return;

  var labels = models.projectionLabels;
  var actualLen = (state.dailySeries.missiles || []).length;

  // Actual missile data (padded with null for forecast days)
  var actual = (state.dailySeries.missiles || []).concat(
    Array(labels.length - actualLen).fill(null)
  );

  var thesisOpts = deepClone(BASE_OPTS);
  thesisOpts.scales.y.beginAtZero = true;

  charts.thesis = new Chart($('thesisChart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: currentLang === 'fa' ? '\u0648\u0627\u0642\u0639\u06CC' : 'Actual launches',
          data: actual,
          borderColor: '#ff6b6b',
          backgroundColor: 'rgba(255,107,107,.08)',
          fill: true,
          tension: .24,
          borderWidth: 3,
          pointRadius: 3,
          spanGaps: false
        },
        {
          label: currentLang === 'fa' ? (models.exponentialDecay && models.exponentialDecay.label_fa || '\u0645\u062F\u0644 \u0627\u062A\u0645\u0627\u0645') : (models.exponentialDecay && models.exponentialDecay.label || 'Depletion Model'),
          data: models.decayProjection || [],
          borderColor: '#46d7b0',
          borderDash: [8, 5],
          borderWidth: 2,
          pointRadius: 0,
          tension: .3,
          spanGaps: true
        },
        {
          label: currentLang === 'fa' ? (models.plateauRationing && models.plateauRationing.label_fa || '\u0645\u062F\u0644 \u062C\u06CC\u0631\u0647\u200C\u0628\u0646\u062F\u06CC') : (models.plateauRationing && models.plateauRationing.label || 'Rationing Model'),
          data: models.plateauProjection || [],
          borderColor: '#63b3ff',
          borderDash: [8, 5],
          borderWidth: 2,
          pointRadius: 0,
          tension: .3,
          spanGaps: true
        }
      ]
    },
    options: thesisOpts
  });
}

function renderModelCards(models) {
  if (!$('modelCards')) return;
  var decay = models.exponentialDecay || {};
  var plateau = models.plateauRationing || {};

  var decayConf = (decay.confidence || 0);
  var platConf = (plateau.confidence || 0);
  var decayLeading = decayConf > platConf;

  function confClass(c) { return c >= 0.6 ? 'high' : c >= 0.35 ? 'medium' : 'low'; }

  function cardHTML(model, isLeading) {
    var label = currentLang === 'fa' ? (model.label_fa || model.label) : model.label;
    var desc = currentLang === 'fa' ? (model.description_fa || model.description) : model.description;
    var outcome = currentLang === 'fa' ? (model.projectedOutcome_fa || model.projectedOutcome) : model.projectedOutcome;
    var conf = model.confidence || 0;
    return '<div class="model-card' + (isLeading ? ' leading' : '') + '">' +
      '<h4>' + (label || '') + '</h4>' +
      '<div class="detail">' + (desc || '') + '</div>' +
      '<div class="confidence ' + confClass(conf) + '">' + Math.round(conf * 100) + '% fit</div>' +
      '<div class="detail">' + (outcome || '') + '</div>' +
      (model.projectedZeroDay ? '<div class="detail"><strong>' + (currentLang === 'fa' ? '\u0631\u0648\u0632 \u0635\u0641\u0631: ' : 'Zero day: ') + '</strong>' + model.projectedZeroDay + '</div>' : '') +
      (model.plateauRate ? '<div class="detail"><strong>' + (currentLang === 'fa' ? '\u0646\u0631\u062E \u0633\u06A9\u0648: ' : 'Sustained rate: ') + '</strong>' + model.plateauRate + '/day for ' + (model.projectedDuration_weeks || '?') + ' weeks</div>' : '') +
      '<div class="falsify">' + (model.falsifiedBy || '') + '</div>' +
    '</div>';
  }

  $('modelCards').innerHTML = cardHTML(decay, decayLeading) + cardHTML(plateau, !decayLeading);
}

function renderVectorChart(vectors) {
  kill('vector');
  if (!$('vectorChart') || !vectors.labels) return;

  // Invert vectors where LOW value = MORE pressure (so all lines UP = more pressure to end war)
  function invert(arr) { return (arr || []).map(function(v) { return 10 - v; }); }

  var vecOpts = deepClone(BASE_OPTS);
  vecOpts.scales.y.beginAtZero = true;
  vecOpts.scales.y.suggestedMax = 10;
  vecOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) {
    var sem = {0:'Low',5:'Med',10:'High'};
    return sem[v] !== undefined ? sem[v] : '';
  }};

  var s = UI[currentLang];

  charts.vector = new Chart($('vectorChart'), {
    type: 'line',
    data: {
      labels: vectors.labels,
      datasets: [
        { label: s.vecMilitary || 'Military Exhaustion', data: vectors.militaryExhaustion || [], borderColor: '#ff6b6b', borderWidth: 2.5, pointRadius: 3, tension: .25 },
        { label: s.vecEconomic || 'Economic Pain', data: vectors.economicPain || [], borderColor: '#ffd166', borderWidth: 2.5, pointRadius: 3, tension: .25 },
        { label: s.vecDiplomatic || 'Diplomatic Momentum', data: vectors.diplomaticMomentum || [], borderColor: '#46d7b0', borderWidth: 2.5, pointRadius: 3, tension: .25 },
        { label: s.vecPolitical || 'US Domestic Pressure', data: invert(vectors.usPoliticalSustainability), borderColor: '#63b3ff', borderWidth: 2.5, pointRadius: 3, tension: .25 },
        { label: s.vecEscalation || 'Escalation Risk', data: invert(vectors.escalationCeilingDistance), borderColor: '#b084ff', borderWidth: 2.5, pointRadius: 3, tension: .25 }
      ]
    },
    options: vecOpts
  });
}

function renderVectorCards(notes, vectors) {
  if (!$('vectorCards')) return;

  var configs = [
    { key: 'militaryExhaustion', noteKey: 'militaryExhaustion', label: UI[currentLang].vecMilitary || 'Military Exhaustion', color: '#ff6b6b', invert: false },
    { key: 'economicPain', noteKey: 'economicPain', label: UI[currentLang].vecEconomic || 'Economic Pain', color: '#ffd166', invert: false },
    { key: 'diplomaticMomentum', noteKey: 'diplomaticMomentum', label: UI[currentLang].vecDiplomatic || 'Diplomatic Momentum', color: '#46d7b0', invert: false },
    { key: 'usPoliticalSustainability', noteKey: 'usPoliticalSustainability', label: 'US Domestic Pressure', color: '#63b3ff', invert: true },
    { key: 'escalationCeilingDistance', noteKey: 'escalationCeilingDistance', label: 'Escalation Risk', color: '#b084ff', invert: true }
  ];

  $('vectorCards').innerHTML = configs.map(function(c) {
    var vals = vectors[c.key] || [];
    var raw = vals.length > 0 ? vals[vals.length - 1] : '\u2014';
    var latest = (c.invert && typeof raw === 'number') ? (10 - raw) : raw;
    var noteText = currentLang === 'fa' ? (notes[c.noteKey + '_fa'] || notes[c.noteKey] || '') : (notes[c.noteKey] || '');
    return '<div class="vector-card">' +
      '<div class="vec-label">' + c.label + '</div>' +
      '<div class="vec-score" style="color:' + c.color + '">' + latest + '<span style="font-size:12px;color:var(--muted)">/10</span></div>' +
      '<div class="vec-note">' + noteText + '</div>' +
    '</div>';
  }).join('');
}

/* ============================================================
   NEW RENDER FUNCTIONS — Additional Charts
   ============================================================ */

function renderAdditionalCharts() {
  var ac = state.additionalCharts || {};

  // Oil vs Conflict Intensity (dual axis)
  kill('oilOverlay');
  if ($('oilOverlayChart') && ac.conflictIntensity) {
    var dualOpts = deepClone(BASE_OPTS);
    dualOpts.scales.y = { type: 'linear', position: 'left', ticks: { color: '#63b3ff', font: { size: 10 }, callback: function(v) { return '$' + v; } }, grid: { color: 'rgba(255,255,255,.05)' } };
    dualOpts.scales.y1 = { type: 'linear', position: 'right', ticks: { color: '#ff9f43', font: { size: 10 } }, grid: { drawOnChartArea: false } };

    charts.oilOverlay = new Chart($('oilOverlayChart'), {
      type: 'line',
      data: {
        labels: state.oil.labels || [],
        datasets: [
          { label: 'Brent', data: state.oil.brent || [], borderColor: '#63b3ff', borderWidth: 2.5, pointRadius: 3, tension: .22, yAxisID: 'y' },
          { label: currentLang === 'fa' ? '\u0634\u062F\u062A \u062F\u0631\u06AF\u06CC\u0631\u06CC' : 'Conflict intensity', data: ac.conflictIntensity, borderColor: '#ff9f43', borderWidth: 2.5, pointRadius: 3, tension: .22, yAxisID: 'y1' }
        ]
      },
      options: dualOpts
    });
  }

  // Scenario Probability Trends (NOT stacked — individual lines)
  kill('scenarioTrend');
  if ($('scenarioTrendChart') && ac.scenarioHistory) {
    var sh = ac.scenarioHistory;
    var stackOpts = deepClone(BASE_OPTS);
    stackOpts.scales.y.beginAtZero = true;
    stackOpts.scales.y.suggestedMax = 35;
    stackOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) { return v + '%'; } };

    charts.scenarioTrend = new Chart($('scenarioTrendChart'), {
      type: 'line',
      data: {
        labels: sh.labels || [],
        datasets: [
          { label: currentLang === 'fa' ? '\u0645\u0627\u0631\u067E\u06CC\u0686 \u062A\u0634\u062F\u06CC\u062F' : 'Escalation spiral', data: sh.escalationSpiral, borderColor: '#ff6b6b', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0641\u0631\u0633\u0627\u06CC\u0634\u06CC' : 'Protracted attrition', data: sh.protractedAttrition, borderColor: '#ff9f43', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0627\u0639\u0644\u0627\u0645 \u067E\u06CC\u0631\u0648\u0632\u06CC' : 'Declared victory', data: sh.declaredVictory, borderColor: '#63b3ff', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0645\u0639\u0627\u0645\u0644\u0647' : 'Negotiated deal', data: sh.negotiatedDeal, borderColor: '#46d7b0', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0645\u062F\u0627\u062E\u0644\u0647 \u0628\u06CC\u0646\u200C\u0627\u0644\u0645\u0644\u0644\u06CC' : 'Int\'l intervention', data: sh.internationalIntervention, borderColor: '#ffd166', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0641\u0631\u0648\u067E\u0627\u0634\u06CC \u0631\u0698\u06CC\u0645' : 'Regime fracture', data: sh.regimeFracture, borderColor: '#b084ff', borderWidth: 2, pointRadius: 4, tension: .3 }
        ]
      },
      options: stackOpts
    });
  }

  // Cumulative strikes by country (stacked horizontal bar)
  kill('cumulByCountry');
  var cbc = state.cumulativeByCountry;
  if ($('cumulByCountryChart') && cbc) {
    var countries = Object.keys(cbc).filter(function(k) { return k !== '_note'; }).sort(function(a, b) {
      return ((cbc[b].missiles || 0) + (cbc[b].drones || 0)) - ((cbc[a].missiles || 0) + (cbc[a].drones || 0));
    });
    var cbcOpts = deepClone(BASE_OPTS);
    cbcOpts.indexAxis = 'y';
    cbcOpts.scales = {
      x: { stacked: true, ticks: { color: '#9eb5d0', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,.05)' }, beginAtZero: true },
      y: { stacked: true, ticks: { color: '#9eb5d0', font: { size: 11 } }, grid: { display: false } }
    };
    charts.cumulByCountry = new Chart($('cumulByCountryChart'), {
      type: 'bar',
      data: {
        labels: countries,
        datasets: [
          { label: currentLang === 'fa' ? 'موشک' : 'Missiles', data: countries.map(function(c) { return cbc[c].missiles || 0; }), backgroundColor: 'rgba(255,107,107,.7)', borderRadius: 4 },
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: countries.map(function(c) { return cbc[c].drones || 0; }), backgroundColor: 'rgba(255,159,67,.7)', borderRadius: 4 }
        ]
      },
      options: cbcOpts
    });
  }
}

/* ============================================================
   NEW RENDER FUNCTIONS — Stockpile, Oil Bands, Hormuz Transit
   ============================================================ */

function renderStockpile() {
  if (!$('stockpileCards')) return;
  var ds = state.dailySeries || {};
  var missiles = ds.missiles || [];
  var drones = ds.drones || [];
  var warDays = missiles.length;

  // Mode-aware header
  var stockHeader = $('stockpileCards') && $('stockpileCards').closest('.panel');
  if (stockHeader) {
    var h3 = stockHeader.querySelector('h3');
    var sub = stockHeader.querySelector('.sub');
    if (h3) h3.textContent = currentMode === 'ceasefire' ? 'Remaining arsenal' : 'Stockpile burn rate';
    if (sub) sub.textContent = currentMode === 'ceasefire'
      ? 'What Iran has left after ' + warDays + ' days of war.'
      : 'How long can Iran sustain fire?';
  }

  // COMPUTE from dailySeries — no static data
  var totalM = missiles.reduce(function(a,b){return a+b;}, 0);
  var totalD = drones.reduce(function(a,b){return a+b;}, 0);

  // Rate: prefer last 7 days, but if Iran is in a zero-fire streak
  // (ceasefire period), fall back to the most recent 7 ACTIVE days
  // so "days remaining" reflects combat tempo, not peacetime.
  function activeRate(arr) {
    var recent = arr.slice(-7);
    var sum = recent.reduce(function(a,b){return a+b;}, 0);
    if (sum > 0) return Math.round(sum / recent.length);
    // scan backwards for last 7 non-zero-sum days
    var active = [];
    for (var i = arr.length - 1; i >= 0 && active.length < 7; i--) {
      if ((arr[i] || 0) > 0) active.unshift(arr[i]);
    }
    if (!active.length) return 0;
    return Math.round(active.reduce(function(a,b){return a+b;}, 0) / active.length);
  }
  var dailyRateM = activeRate(missiles);
  var dailyRateD = activeRate(drones);

  // Three stockpile scenarios (estimated total pre-war stockpile)
  var scenarios = [
    { label: 'Western estimate (low)', totalM: totalM + 1500, totalD: totalD + 5000 },
    { label: 'Mid-range estimate', totalM: totalM + 2500, totalD: totalD + 9000 },
    { label: 'IRGC claim (high)', totalM: totalM + 4000, totalD: totalD + 15000 }
  ];

  $('stockpileCards').innerHTML = '<div class="model-cards" style="grid-template-columns:repeat(3,1fr)">' +
    scenarios.map(function(s) {
      var remainM = s.totalM - totalM;
      var remainD = s.totalD - totalD;
      var daysM = dailyRateM > 0 ? Math.round(remainM / dailyRateM) : 999;
      var daysD = dailyRateD > 0 ? Math.round(remainD / dailyRateD) : 999;
      var cls = daysM > 100 ? 'high' : daysM > 50 ? 'medium' : 'low';
      return '<div class="model-card">' +
        '<h4>' + s.label + '</h4>' +
        '<div class="confidence ' + cls + '">' + Math.min(daysM, daysD) + ' days</div>' +
        '<div class="detail">Missiles: <strong>' + remainM.toLocaleString() + '</strong> remaining (' + daysM + ' days)</div>' +
        '<div class="detail">Drones: <strong>' + remainD.toLocaleString() + '</strong> remaining (' + daysD + ' days)</div>' +
      '</div>';
    }).join('') + '</div>';

  if ($('burnedToDate')) {
    $('burnedToDate').innerHTML = totalM.toLocaleString() + ' missiles + ' + totalD.toLocaleString() + ' drones fired at ~' + dailyRateM + ' missiles/day + ~' + dailyRateD + ' drones/day';
  }
}

function renderOilBands() {
  kill('oilBands');
  var ob = state.oilScenarioBands;
  if (!ob || !$('oilBandsChart')) return;

  var bandOpts = deepClone(BASE_OPTS);
  bandOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) { return '$' + v; } };
  bandOpts.scales.y.suggestedMin = 60;

  charts.oilBands = new Chart($('oilBandsChart'), {
    type: 'line',
    data: {
      labels: ob.labels || [],
      datasets: [
        { label: currentLang === 'fa' ? 'آتش‌بس ۶ آوریل' : 'Ceasefire by Apr 6', data: ob.ceasefireApril6, borderColor: '#46d7b0', backgroundColor: 'rgba(70,215,176,.1)', fill: true, borderWidth: 2.5, pointRadius: 4, tension: .3, borderDash: [6, 3] },
        { label: currentLang === 'fa' ? 'ادامه جنگ' : 'War continues', data: ob.warContinues, borderColor: '#ffd166', backgroundColor: 'rgba(255,209,102,.1)', fill: true, borderWidth: 2.5, pointRadius: 4, tension: .3, borderDash: [6, 3] },
        { label: currentLang === 'fa' ? 'بستن باب‌المندب' : 'Bab al-Mandab closes', data: ob.babAlMandabCloses, borderColor: '#ff6b6b', backgroundColor: 'rgba(255,107,107,.1)', fill: true, borderWidth: 2.5, pointRadius: 4, tension: .3, borderDash: [6, 3] }
      ]
    },
    options: bandOpts
  });
}

function renderHormuzTransit() {
  kill('hormuzTransit');
  var ht = state.hormuzTransit;
  if (!ht || !$('hormuzTransitChart')) return;

  var htOpts = deepClone(BASE_OPTS);
  htOpts.scales.y.beginAtZero = true;
  htOpts.scales.y.suggestedMax = 70;

  charts.hormuzTransit = new Chart($('hormuzTransitChart'), {
    type: 'line',
    data: {
      labels: ht.labels || [],
      datasets: [
        { label: currentLang === 'fa' ? 'کشتی/روز' : 'Vessels/day', data: ht.vessels, borderColor: '#63b3ff', backgroundColor: 'rgba(99,179,255,.12)', fill: true, borderWidth: 2.5, pointRadius: 3, tension: .22 },
        { label: currentLang === 'fa' ? 'میانگین قبل جنگ' : 'Pre-war average', data: ht.vessels.map(function() { return ht.preWarAverage; }), borderColor: '#ff6b6b', borderDash: [8, 4], borderWidth: 1.5, pointRadius: 0 }
      ]
    },
    options: htOpts
  });

  if ($('hormuzTransitNote')) {
    var note = currentLang === 'fa' ? (ht.note_fa || ht.note) : ht.note;
    $('hormuzTransitNote').textContent = note || '';
  }
}

/* ============================================================
   NEW RENDER FUNCTIONS — Deadline, Coalition, Decapitation
   ============================================================ */

function tickDeadline() {
  var cd = state.ceasefireDeadline;
  if (!cd || !$('deadlineCountdown')) return;
  var deadline = new Date(cd.deadline);
  var now = new Date();
  var diff = deadline - now;
  if (diff <= 0) {
    $('deadlineCountdown').innerHTML = '<span style="color:var(--red)">DEADLINE PASSED</span>';
    return;
  }
  var days = Math.floor(diff / 864e5);
  var hours = Math.floor((diff % 864e5) / 36e5);
  var mins = Math.floor((diff % 36e5) / 6e4);
  var secs = Math.floor((diff % 6e4) / 1e3);
  var label = currentLang === 'fa' ? (cd.label_fa || cd.label) : cd.label;
  $('deadlineCountdown').innerHTML = '<span style="color:var(--red)">' + days + 'd ' + hours + 'h ' + mins + 'm ' + secs + 's</span> <span style="font-size:14px;color:var(--muted)">' + (currentLang === 'fa' ? 'تا ' : 'until ') + label + '</span>';
}

var deadlineInterval = null;

function renderDeadline() {
  var cd = state.ceasefireDeadline;
  if (!cd || !$('deadlineCountdown')) return;

  // Tick immediately then every second
  tickDeadline();
  if (deadlineInterval) clearInterval(deadlineInterval);
  deadlineInterval = setInterval(tickDeadline, 1000);

  var ctx = currentLang === 'fa' ? (cd.context_fa || cd.context) : cd.context;
  if ($('deadlineContext')) $('deadlineContext').textContent = ctx || '';

  // Branch: deal
  if ($('branchDeal') && cd.branchIfDeal) {
    $('branchDeal').innerHTML = cd.branchIfDeal.map(function(s) {
      return '<div class="tl-item partial"><div class="tl-milestone">' + s.step + '</div><div class="tl-estimate">' + s.timeline + '</div><div class="tl-detail">' + s.detail + '</div></div>';
    }).join('');
  }

  // Branch: no deal
  if ($('branchNoDeal') && cd.branchIfNoDeal) {
    $('branchNoDeal').innerHTML = cd.branchIfNoDeal.map(function(s) {
      return '<div class="tl-item blocked"><div class="tl-milestone">' + s.step + '</div><div class="tl-estimate">' + s.timeline + '</div><div class="tl-detail">' + s.detail + '</div></div>';
    }).join('');
  }
}

function renderCoalition() {
  var cf = state.coalitionFracture;
  if (!cf) return;

  // Chart
  kill('coalition');
  if ($('coalitionChart') && cf.labels) {
    var cfOpts = deepClone(BASE_OPTS);
    cfOpts.scales.y.beginAtZero = true;
    cfOpts.scales.y.suggestedMax = 10;
    cfOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) {
      return v === 10 ? 'Unified' : v === 5 ? 'Strained' : v === 0 ? 'Collapsed' : '';
    }};

    charts.coalition = new Chart($('coalitionChart'), {
      type: 'line',
      data: {
        labels: cf.labels,
        datasets: [{
          label: currentLang === 'fa' ? 'انسجام ائتلاف' : 'Coalition cohesion',
          data: cf.cohesionScore,
          borderColor: '#ff9f43',
          backgroundColor: 'rgba(255,159,67,.12)',
          fill: true,
          borderWidth: 3,
          pointRadius: 5,
          tension: .3
        }]
      },
      options: cfOpts
    });
  }

  // Events list
  if ($('coalitionEvents') && cf.events) {
    $('coalitionEvents').innerHTML = cf.events.map(function(e) {
      var color = e.type === 'fracture' ? 'var(--red)' : e.type === 'support' ? 'var(--cyan)' : 'var(--gold)';
      var icon = e.type === 'fracture' ? '\u25BC' : e.type === 'support' ? '\u25B2' : '\u25CF';
      return '<div style="display:flex;gap:10px;align-items:flex-start;padding:8px 0;border-bottom:1px solid var(--border)">' +
        '<span style="color:' + color + ';font-weight:800;min-width:20px">' + icon + '</span>' +
        '<div><strong style="font-size:12px">' + e.date + ' \u2014 ' + e.actor + '</strong><div style="font-size:12px;color:var(--soft);margin-top:2px">' + e.detail + '</div></div></div>';
    }).join('');
  }
}

function renderDecapitation() {
  var dt = state.decapitationTracker;
  if (!dt || !$('decapitationList')) return;

  $('decapitationList').innerHTML = dt.map(function(d) {
    var statusCls = d.statusColor === 'red' ? 'bad' : 'warn';
    var name = currentLang === 'fa' ? (d.name_fa || d.name) : d.name;
    return '<div class="route-card">' +
      '<div class="route-header"><div class="route-name">' + name + '</div><span class="route-status ' + d.statusColor + '">' + d.status + '</span></div>' +
      '<div style="font-size:12px;color:var(--muted);margin-bottom:4px">' + d.role + ' \u2014 ' + d.date + '</div>' +
      '<div class="route-detail">' + d.significance + '</div>' +
      '<div style="font-size:11px;color:var(--soft);margin-top:4px"><strong>Replacement:</strong> ' + d.replacement + '</div>' +
    '</div>';
  }).join('');
}

/* ============================================================
   NEW RENDER FUNCTIONS — Expanded Iranfarhang
   ============================================================ */

function renderExpandedIranfarhang() {
  var ex = currentLang === 'fa' ? (state.iranfarhangExpanded_fa || state.iranfarhangExpanded || {}) : (state.iranfarhangExpanded || {});

  function exL(key) {
    if (currentLang === 'fa') {
      var faKey = key + '_fa';
      if (state.iranfarhangExpanded && state.iranfarhangExpanded[faKey] && state.iranfarhangExpanded[faKey].length) return state.iranfarhangExpanded[faKey];
    }
    return (state.iranfarhangExpanded && state.iranfarhangExpanded[key]) || [];
  }

  // Supply Chain Timeline
  var timeline = exL('supplyChainTimeline');
  if ($('ifSupplyTimeline')) {
    $('ifSupplyTimeline').innerHTML = timeline.map(function(t) {
      return '<div class="tl-item ' + (t.status || 'blocked') + '">' +
        '<div class="tl-milestone">' + t.milestone + '</div>' +
        '<div class="tl-estimate">' + t.estimate + ' <span class="tag ' + (t.confidence === 'medium' ? 'warn' : t.confidence === 'high' ? 'good' : 'bad') + '">' + t.confidence + '</span></div>' +
        '<div class="tl-detail">' + t.detail + '</div>' +
      '</div>';
    }).join('');
  }

  // Route viability
  var routes = exL('routeViability');
  if ($('ifRouteViability')) {
    $('ifRouteViability').innerHTML = routes.map(function(r) {
      return '<div class="route-card"><div class="route-header"><div class="route-name">' + r.route + '</div><span class="route-status ' + (r.statusColor || 'yellow') + '">' + r.status + '</span></div>' +
      '<div class="route-detail">' + r.detail + '</div>' +
      '<div class="route-meta">' +
        '<span>' + (currentLang === 'fa' ? '\u0647\u0632\u06CC\u0646\u0647: ' : 'Cost: ') + '<strong>' + r.cost_vs_normal + '</strong></span>' +
        '<span>' + (currentLang === 'fa' ? '\u062A\u0631\u0627\u0646\u0632\u06CC\u062A: ' : 'Transit: ') + '<strong>' + r.transit_days + '</strong></span>' +
      '</div></div>';
    }).join('');
  }

  // OFAC card
  var ofac = (state.iranfarhangExpanded && state.iranfarhangExpanded.ofacStatus) || {};
  if ($('ifOfacCard')) {
    var riskText = currentLang === 'fa' ? (ofac.risk_fa || ofac.risk || '') : (ofac.risk || '');
    $('ifOfacCard').innerHTML =
      '<div class="sc-header"><span class="sc-title">' + (currentLang === 'fa' ? '\u0648\u0636\u0639\u06CC\u062A OFAC' : 'OFAC Status') + '</span>' +
      '<span class="tag ' + (ofac.exemptionValid ? 'good' : 'bad') + '">' + (ofac.exemptionValid ? (currentLang === 'fa' ? '\u0645\u0639\u062A\u0628\u0631' : 'VALID') : 'AT RISK') + '</span></div>' +
      '<div class="sc-detail"><strong>' + (ofac.citation || '') + '</strong></div>' +
      '<div class="sc-detail">' + (ofac.type || '') + '</div>' +
      '<div class="sc-detail" style="margin-top:6px">' + riskText + '</div>';
  }

  // Tehran comms card
  var comms = (state.iranfarhangExpanded && state.iranfarhangExpanded.tehranCommsStatus) || {};
  if ($('ifCommsCard')) {
    var commsDetail = currentLang === 'fa' ? (comms.detail_fa || comms.detail || '') : (comms.detail || '');
    $('ifCommsCard').innerHTML =
      '<div class="sc-header"><span class="sc-title">' + (currentLang === 'fa' ? '\u0627\u0631\u062A\u0628\u0627\u0637 \u062A\u0647\u0631\u0627\u0646' : 'Tehran Comms') + '</span>' +
      '<span class="tag ' + (comms.statusColor === 'red' ? 'bad' : 'warn') + '">' + (comms.status || '\u2014') + '</span></div>' +
      '<div class="sc-detail"><strong>' + (currentLang === 'fa' ? '\u0642\u0637\u0639 \u0627\u06CC\u0646\u062A\u0631\u0646\u062A: ' : 'Internet down: ') + (comms.internetDownHours || '?') + (currentLang === 'fa' ? ' \u0633\u0627\u0639\u062A' : ' hours') + '</strong></div>' +
      '<div class="sc-detail">' + commsDetail + '</div>';
  }

  // Inventory runway card
  var inv = (state.iranfarhangExpanded && state.iranfarhangExpanded.inventoryRunway) || {};
  if ($('ifInventoryCard')) {
    var invDetail = currentLang === 'fa' ? (inv.detail_fa || inv.detail || '') : (inv.detail || '');
    var months = inv.months_remaining || 0;
    var cls = months > 4 ? 'good' : months > 2 ? 'warn' : 'bad';
    $('ifInventoryCard').innerHTML =
      '<div class="sc-header"><span class="sc-title">' + (currentLang === 'fa' ? '\u0630\u062E\u06CC\u0631\u0647 \u0645\u0648\u062C\u0648\u062F\u06CC' : 'Inventory Runway') + '</span>' +
      '<span class="tag ' + cls + '">' + months + (currentLang === 'fa' ? ' \u0645\u0627\u0647' : ' months') + '</span></div>' +
      '<div class="sc-detail">' + invDetail + '</div>' +
      (inv.criticalDate ? '<div class="sc-detail" style="color:var(--red);margin-top:4px"><strong>' + (currentLang === 'fa' ? '\u062A\u0627\u0631\u06CC\u062E \u0628\u062D\u0631\u0627\u0646\u06CC: ' : 'Critical: ') + inv.criticalDate + '</strong></div>' : '');
  }

  // Publishing deep dive
  renderList('publishingDeepDiveBox', exL('publishingDeepDive'));
}

/* ============================================================
   NEW RENDER FUNCTIONS — Expanded KIP
   ============================================================ */

function renderExpandedKIP() {
  function kipL(key) {
    if (currentLang === 'fa') {
      var faKey = key + '_fa';
      if (state.kipExpanded && state.kipExpanded[faKey] && state.kipExpanded[faKey].length) return state.kipExpanded[faKey];
    }
    return (state.kipExpanded && state.kipExpanded[key]) || [];
  }
  var kip = state.kipExpanded || {};

  // Banking risk gauge
  var banking = kip.dubaiBankingRisk || {};
  if ($('kipBankingGauge')) {
    var score = banking.score || 0;
    var scoreColor = score >= 7 ? 'var(--red)' : score >= 4 ? 'var(--gold)' : 'var(--cyan)';
    var trendArrow = banking.trend === 'rising' ? '&#9650;' : banking.trend === 'falling' ? '&#9660;' : '&#9644;';
    var trendColor = banking.trend === 'rising' ? 'var(--red)' : banking.trend === 'falling' ? 'var(--cyan)' : 'var(--gold)';
    var detailText = currentLang === 'fa' ? (banking.detail_fa || banking.detail || '') : (banking.detail || '');
    $('kipBankingGauge').innerHTML =
      '<div><div class="gauge-score" style="color:' + scoreColor + '">' + score + '<span style="font-size:14px;color:var(--muted)">/10</span></div>' +
      '<div class="gauge-trend" style="color:' + trendColor + '">' + trendArrow + ' ' + (banking.trend || '') + '</div></div>' +
      '<div class="gauge-detail"><strong>' + (currentLang === 'fa' ? '\u0631\u06CC\u0633\u06A9 \u0628\u0627\u0646\u06A9\u06CC \u062F\u0628\u06CC' : 'Dubai Banking Risk') + '</strong><br>' + detailText + '</div>';
  }

  // Alternative hub matrix
  var hubs = kipL('alternativeHubs');
  if ($('kipHubMatrix') && hubs.length) {
    function sc(v) { return v >= 7 ? 'score-high' : v >= 5 ? 'score-mid' : 'score-low'; }
    $('kipHubMatrix').innerHTML = '<table class="hub-matrix"><thead><tr>' +
      '<th>' + (currentLang === 'fa' ? '\u0634\u0647\u0631' : 'City') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u0628\u0627\u0646\u06A9' : 'Banking') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u0644\u062C\u0633\u062A\u06CC\u06A9' : 'Logistics') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u0647\u0632\u06CC\u0646\u0647' : 'Cost') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u0627\u0645\u0646\u06CC\u062A' : 'Safety') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u06A9\u0644' : 'Overall') + '</th>' +
      '<th>' + (currentLang === 'fa' ? '\u06CC\u0627\u062F\u062F\u0627\u0634\u062A' : 'Notes') + '</th>' +
      '</tr></thead><tbody>' +
      hubs.map(function(h) {
        return '<tr><td><strong>' + h.city + '</strong></td>' +
        '<td class="score-cell ' + sc(h.banking) + '">' + h.banking + '</td>' +
        '<td class="score-cell ' + sc(h.logistics) + '">' + h.logistics + '</td>' +
        '<td class="score-cell ' + sc(h.cost) + '">' + h.cost + '</td>' +
        '<td class="score-cell ' + sc(h.risk) + '">' + h.risk + '</td>' +
        '<td class="score-cell ' + sc(h.overall) + '"><strong>' + h.overall + '</strong></td>' +
        '<td style="font-size:11px;color:var(--soft)">' + h.notes + '</td></tr>';
      }).join('') +
      '</tbody></table>';
  }

  // Hormuz reopening timeline
  var hormuzTL = kipL('hormuzReopeningTimeline');
  if ($('kipHormuzTimeline')) {
    $('kipHormuzTimeline').innerHTML = hormuzTL.map(function(t) {
      return '<div class="tl-item ' + (t.status || 'not_started') + '">' +
        '<div class="tl-milestone">' + t.milestone + '</div>' +
        '<div class="tl-estimate">' + t.estimate + '</div>' +
        '<div class="tl-detail">' + t.detail + '</div>' +
      '</div>';
    }).join('');
  }

  // Stranded cargo card
  var cargo = kip.strandedCargo || {};
  if ($('kipCargoCard')) {
    var cargoDetail = currentLang === 'fa' ? (cargo.detail_fa || cargo.detail || '') : (cargo.detail || '');
    $('kipCargoCard').innerHTML =
      '<div class="sc-header"><span class="sc-title">' + (currentLang === 'fa' ? '\u0628\u0627\u0631 \u0645\u0639\u0637\u0644' : 'Stranded Cargo') + '</span>' +
      '<span class="tag warn">' + (cargo.containers_estimated || '?') + ' containers</span></div>' +
      '<div class="sc-detail"><strong>' + (currentLang === 'fa' ? '\u0627\u0631\u0632\u0634: ' : 'Value: ') + (cargo.value_usd || '?') + '</strong> \u2014 ' + (cargo.location || '') + '</div>' +
      '<div class="sc-detail">' + cargoDetail + '</div>';
  }

  // Insurance cost index chart
  kill('insurance');
  var ins = kip.insuranceCostIndex || {};
  var insCanvas = $('insuranceChart');
  if (insCanvas && !ins.labels) {
    // Data pending placeholder
    var insParent = insCanvas.parentElement;
    if (insParent && !insParent.querySelector('.data-pending')) {
      var ph = document.createElement('div');
      ph.className = 'data-pending';
      ph.style.cssText = 'display:flex;align-items:center;justify-content:center;height:100%;color:var(--muted);font-size:12px;font-style:italic';
      ph.textContent = currentLang === 'fa' ? 'داده در انتظار' : 'Data pending';
      insCanvas.style.display = 'none';
      insParent.appendChild(ph);
    }
  }
  if (insCanvas && ins.labels) {
    var insOpts = deepClone(BASE_OPTS);
    insOpts.scales.y.ticks = { color: '#9eb5d0', font: { size: 10 }, callback: function(v) { return v + '%'; } };
    insOpts.scales.y.beginAtZero = true;
    insOpts.plugins.legend = { labels: { color: '#eef5fc', font: { size: 11 } } };

    charts.insurance = new Chart($('insuranceChart'), {
      type: 'line',
      data: {
        labels: ins.labels,
        datasets: [
          { label: currentLang === 'fa' ? '\u062D\u0642\u200C\u0628\u06CC\u0645\u0647 \u062C\u0646\u06AF' : 'War risk premium', data: ins.warRiskPremium_pct, borderColor: '#ff6b6b', borderWidth: 2, pointRadius: 4, tension: .3 },
          { label: currentLang === 'fa' ? '\u0628\u06CC\u0645\u0647 \u0628\u062F\u0646\u0647' : 'Hull insurance', data: ins.hullInsurance_pct, borderColor: '#ffd166', borderWidth: 2, pointRadius: 4, tension: .3 }
        ]
      },
      options: insOpts
    });
  }
}

/* ============================================================
   render() and loadDashboardData()
   ============================================================ */

function buildSectionNav() {
  var nav = document.getElementById('sectionNav');
  if (!nav) return;

  // Define clean grouped nav structure — map DOM element IDs/queries to labels
  // Ceasefire-specific nav items
  var cfItems = currentMode === 'ceasefire' ? [
    { group: 'Ceasefire', items: [
      { q: '.ceasefire-hero', label: 'Ceasefire Status' },
      { q: '#cfCountdown', label: 'Ceasefire Countdown', up: 1 },
      { q: '#cfViolationChart', label: 'Violation Tracker', up: 1 },
      { q: '#cfNegotiationTimeline', label: 'Peace Talks', up: 1 },
      { q: '#cfHormuzRecoveryChart', label: 'Hormuz Recovery', up: 1 }
    ]}
  ] : [];

  var groups = cfItems.concat([
    { group: 'Prediction', items: [
      { q: '.prediction-hero', label: 'Forecast & Decision Engine' },
      { q: '#simButtons', label: 'Scenario Simulator', up: 1 },
      { q: '#leadingIndicators', label: 'Leading Indicators', up: 1 },
      { q: '#sensitivityTable', label: 'Sensitivity Analysis', up: 1 },
      { q: '[data-i18n="kickerThesis"]', label: 'Capability Thesis', up: 1 },
      { q: '#stockpileCards', label: 'Stockpile Burn Rate', up: 1 },
      { q: '[data-i18n="kickerVectors"]', label: 'Pressure Index', up: 1 },
      { q: '#deadlineCountdown', label: 'April 7 Deadline', up: 1 },
      { q: '#escalationLadder', label: 'Escalation Ladder', up: 1 }
    ]},
    { group: 'Situation', items: [
      { q: '#theoryBox', label: 'Situation Report', up: 1 },
      { q: '#scenarioProbs', label: 'Scenarios', up: 1 }
    ]},
    { group: 'Military', items: [
      { q: '#missileChart', label: 'Launch Tempo', up: 1 },
      { q: '#comboChart', label: 'Combined & Cumulative', up: 1 },
      { q: '#cumulByCountryChart', label: 'Strikes by Country', up: 1 }
    ]},
    { group: 'Economic', items: [
      { q: '#oilOverlayChart', label: 'Oil & Conflict', up: 1 },
      { q: '#oilBandsChart', label: 'Oil Scenarios', up: 1 },
      { q: '#hormuzTransitChart', label: 'Hormuz Transit', up: 1 },
      { q: '#targetMissileChart', label: 'Target Breakdown', up: 1 }
    ]},
    { group: 'Geopolitical', items: [
      { q: '#diplomacyBox', label: 'Diplomacy', up: 1 },
      { q: '#coalitionChart', label: 'War Support Index', up: 1 },
      { q: '#decapitationList', label: 'Decapitation Tracker', up: 1 },
      { q: '#hormuzBox', label: 'Hormuz & Shipping', up: 1 }
    ]},
    { group: 'Business', items: [
      { q: '#impactIranfarhang', label: 'Iranfarhang', up: 2 },
      { q: '#impactKIP', label: 'KIP', up: 2 }
    ]},
    { group: 'Reference', items: [
      { q: '#timeline', label: 'Timeline & Evaluation', up: 1 },
      { q: '#dailyRows', label: 'Event Log', up: 2 }
    ]}
  ]);

  var html = '';
  groups.forEach(function(g) {
    html += '<div class="nav-group">' + g.group + '</div>';
    g.items.forEach(function(item) {
      var el = document.querySelector(item.q);
      if (!el) return;
      // Walk up to the section/panel parent
      var target = el;
      for (var i = 0; i < (item.up || 0); i++) {
        if (target.parentElement) target = target.parentElement;
      }
      if (!target.id) target.id = 'nav-' + item.label.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      html += '<a href="#' + target.id + '" onclick="document.getElementById(\'sectionNav\').classList.remove(\'open\')">' + item.label + '</a>';
    });
  });
  nav.innerHTML = html;

  // Close nav when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.nav-wrap')) {
      nav.classList.remove('open');
    }
  });
}

/* ============================================================
   Scenario Simulator
   ============================================================ */
var activeSimScenario = null;

function renderSensitivity() {
  var sens = (state.decisionEngine || {}).sensitivity;
  if (!sens || !$('sensitivityBars')) return;
  // Sort by impact descending
  var sorted = sens.slice().sort(function(a,b) { return b.impact - a.impact; });
  $('sensitivityBars').innerHTML = sorted.map(function(s) {
    var barWidth = Math.min(s.impact * 5, 100);
    var color = s.impact >= 10 ? 'var(--cyan)' : s.impact >= 3 ? 'var(--gold)' : 'var(--muted)';
    return '<div style="margin-bottom:8px">' +
      '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:2px"><span>' + s.input + '</span><strong style="color:' + color + '">+' + s.impact + '% impact</strong></div>' +
      '<div class="prob-track" style="margin:0"><div class="prob-bar" style="width:' + barWidth + '%;background:' + color + '"></div></div></div>';
  }).join('');
}

function renderLeadingIndicators() {
  var li = (state.decisionEngine || {}).leadingIndicators;
  if (!li || !$('leadingIndicators')) return;
  var arrows = { accelerating: '&#11014;&#11014;', rising: '&#11014;', steady: '&#10145;', falling: '&#11015;', decelerating: '&#11015;&#11015;' };
  // Context-aware: green=good for resolution, red=bad for resolution
  var goodIfRising = ['Hormuz', 'Diplomatic'];
  $('leadingIndicators').innerHTML = li.map(function(ind) {
    var up = ind.direction === 'rising' || ind.direction === 'accelerating';
    var down = ind.direction === 'falling' || ind.direction === 'decelerating';
    var risingIsGood = goodIfRising.some(function(g) { return ind.metric.indexOf(g) > -1; });
    var c = 'var(--muted)';
    if (up) c = risingIsGood ? 'var(--cyan)' : 'var(--red)';
    if (down) c = risingIsGood ? 'var(--red)' : 'var(--cyan)';
    var goodBad = (up && risingIsGood) || (down && !risingIsGood) ? 'good for resolution' : (up && !risingIsGood) || (down && risingIsGood) ? 'bad for resolution' : '';
    var tagColor = goodBad === 'good for resolution' ? 'good' : goodBad === 'bad for resolution' ? 'bad' : 'warn';
    return '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04)">' +
      '<div><span style="font-size:12px;color:var(--text)">' + ind.metric + '</span>' +
      (goodBad ? '<br><span class="tag ' + tagColor + '" style="font-size:9px;margin-top:2px">' + goodBad + '</span>' : '') + '</div>' +
      '<span style="font-size:16px;font-weight:900;color:' + c + '">' + ind.value + ' ' + (arrows[ind.direction]||'') + '</span></div>';
  }).join('');
}

function renderChangelog() {
  if (!$('probChangelog')) return;

  // Compute from engine for last 10 days — show deal/US/Iran scores + ensemble
  var ds = state.dailySeries || {};
  var maxDay = (ds.labels || []).length;
  var startDay = Math.max(0, maxDay - 8);
  var entries = [];

  for (var i = startDay; i < maxDay; i++) {
    var eng = computeEngineForDay(i);
    if (!eng) continue;
    var prev = i > 0 ? computeEngineForDay(i - 1) : null;
    var delta = prev ? eng.ensemble - prev.ensemble : null;
    entries.push({
      day: 'D' + (i + 1),
      label: ds.labels[i],
      ensemble: eng.ensemble,
      deal: Math.round(eng.dealScore * 100),
      iran: Math.round(eng.iranScore * 100),
      us: Math.round(eng.usExitScore * 100),
      delta: delta
    });
  }

  $('probChangelog').innerHTML = entries.reverse().map(function(e) {
    var dotColor = e.delta > 0 ? 'var(--cyan)' : e.delta < 0 ? 'var(--red)' : 'var(--muted)';
    var deltaStr = e.delta !== null ? (e.delta > 0 ? '+' + e.delta : String(e.delta)) : '—';
    return '<div style="display:flex;gap:8px;align-items:center;padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:12px">' +
      '<div style="width:8px;height:8px;border-radius:50%;background:' + dotColor + ';flex-shrink:0"></div>' +
      '<strong style="min-width:28px">' + e.ensemble + '%</strong>' +
      '<span style="color:' + dotColor + ';min-width:24px">' + deltaStr + '</span>' +
      '<span style="color:var(--muted)">' + e.day + '</span>' +
      '<span style="color:var(--soft);margin-left:auto;font-size:10px">Deal ' + e.deal + '% · Iran ' + e.iran + '% · US ' + e.us + '%</span>' +
    '</div>';
  }).join('');
}

function renderSimulator() {
  var sim = state.scenarioSimulator;
  if (!sim || !$('simButtons')) return;
  var scenarios = currentMode === 'ceasefire' ? (sim.ceasefireScenarios || []) : (sim.scenarios || []);

  $('simButtons').innerHTML = scenarios.map(function(s) {
    return '<button class="sim-btn' + (activeSimScenario === s.id ? ' active' : '') + '" data-sim="' + s.id + '">' +
      (currentLang === 'fa' ? (s.label_fa || s.label) : s.label) + '</button>';
  }).join('');

  // Attach click handlers
  $('simButtons').querySelectorAll('.sim-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var id = this.getAttribute('data-sim');
      activeSimScenario = activeSimScenario === id ? null : id;
      renderSimulator();
      showSimResult();
    });
  });

  if (!activeSimScenario) {
    if ($('simResult')) $('simResult').style.display = 'none';
  }
}

function showSimResult() {
  var sim = state.scenarioSimulator;
  if (!sim || !$('simResult') || !activeSimScenario) return;
  var scenarioList = currentMode === 'ceasefire' ? (sim.ceasefireScenarios || []) : (sim.scenarios || []);
  var scenario = scenarioList.find(function(s) { return s.id === activeSimScenario; });
  if (!scenario) return;

  // Ceasefire mode — simpler delta display from pre-computed deltas
  if (currentMode === 'ceasefire') {
    var maxDay = (state.dailySeries.labels || []).length;
    var baseCf = computeCeasefireForDay(maxDay - 1);
    if (!baseCf) return;
    var baseStab = baseCf.stabilityScore;
    var baseOilCf = (state.oil.brent || []).slice(-1)[0] || 100;
    var adjStab = Math.max(0, Math.min(100, baseStab + Math.round((scenario.pDeltaHolds || 0) * 100)));
    var adjOilCf = baseOilCf + (scenario.oilDelta || 0);
    var probDeltaCf = adjStab - baseStab;
    var oilDeltaCf = Math.round(adjOilCf - baseOilCf);
    var descCf = scenario.desc || scenario.description || '';

    function deltaCf(v, unit) {
      if (v === 0) return '';
      var cls = v > 0 ? 'up' : 'down';
      return '<span class="sim-delta ' + cls + '">' + (v > 0 ? '+' : '') + v + unit + '</span>';
    }

    $('simResult').style.display = 'block';
    $('simResult').innerHTML = '<div style="font-size:13px;margin-bottom:8px">' + descCf + '</div>' +
      '<div style="display:flex;gap:24px;flex-wrap:wrap">' +
      '<div>Ceasefire stability: <strong>' + adjStab + '%</strong> ' + deltaCf(probDeltaCf, 'pp') + '</div>' +
      '<div>Oil: <strong>$' + adjOilCf.toFixed(0) + '</strong> ' + deltaCf(oilDeltaCf, '') + '</div></div>';
    return;
  }

  // Compute baseline from engine (war mode)
  var maxDay = (state.dailySeries.labels || []).length;
  var baseEng = computeEngineForDay(maxDay - 1);
  if (!baseEng) return;
  var baseProb = baseEng.ensemble;
  var baseOil = (state.oil.brent || []).slice(-1)[0] || 100;

  // Build overrides for the scenario — no state mutation needed
  var ov = {};
  if (scenario.id === 'ceasefire_apr6') {
    ov.iranRejectedCeasefire = false;
    ov.deadlineDays = 30;
    ov.mediatorMeetings = 8;
    ov.proposalsRejected = 0;
    ov.coalitionScore = 9;
  } else if (scenario.id === 'power_grid') {
    ov.deadlineDays = 0;
    ov.proposalsRejected = 5;
    ov.iranRejectedCeasefire = true;
    ov.mediatorMeetings = 0;
    ov.coalitionScore = 4;
  } else if (scenario.id === 'bab_closes') {
    ov.deadlineDays = 0;
    ov.hormuzVessels = 0;
    ov.gasPrice = 6.5;
    ov.approvalWrong = 72;
    ov.coalitionScore = 3;
  } else if (scenario.id === 'ground_invasion') {
    ov.deadlineDays = 0;
    ov.coalitionScore = 2;
    ov.approvalWrong = 78;
    ov.usKIA = 50;
    ov.mediatorMeetings = 0;
  }

  // Recompute engine with overrides — no state mutation
  var adjEng = computeEngineForDay(maxDay - 1, ov);
  var adjProb = adjEng ? adjEng.ensemble : baseProb;

  var adjOil = scenario.oilTarget || baseOil;
  var probDelta = adjProb - baseProb;
  var oilDelta = Math.round(adjOil - baseOil);
  var desc = currentLang === 'fa' ? (scenario.description_fa || scenario.description) : scenario.description;

  // Use 1-decimal precision to surface small but real engine moves
  var ae = adjEng || baseEng;
  var adjProbF = (ae.pNegotiated * 100).toFixed(1);
  var baseProbF = (baseEng.pNegotiated * 100).toFixed(1);
  var adjEscF = (ae.pEscalation * 100).toFixed(1);
  var baseEscF = (baseEng.pEscalation * 100).toFixed(1);
  var adjProtF = (ae.pProtracted * 100).toFixed(1);
  var baseProtF = (baseEng.pProtracted * 100).toFixed(1);

  function delta(v, unit) {
    if (Math.abs(v) < 0.05) return '';
    var cls = v > 0 ? 'up' : 'down';
    return '<span class="sim-delta ' + cls + '">' + (v > 0 ? '+' : '') + v.toFixed(1) + unit + '</span>';
  }

  function row(label, adjVal, baseVal, unit) {
    var d = parseFloat(adjVal) - parseFloat(baseVal);
    return '<div class="sim-row"><span class="sim-label">' + label + '</span><span><span class="sim-value">' + adjVal + unit + '</span> ' + delta(d, unit) + ' <span style="color:var(--muted);font-size:11px">(was ' + baseVal + unit + ')</span></span></div>';
  }

  $('simResult').style.display = 'block';
  $('simResult').innerHTML =
    row('Negotiated resolution', adjProbF, baseProbF, '%') +
    row('Escalation', adjEscF, baseEscF, '%') +
    row('Protracted', adjProtF, baseProtF, '%') +
    row('Ensemble (combined)', String(adjProb), String(baseProb), '%') +
    '<div class="sim-row"><span class="sim-label">Brent crude</span><span><span class="sim-value">$' + adjOil + '</span> ' + delta(adjOil - baseOil, '') + '</span></div>' +
    '<div class="sim-desc">' + sanitizeHTML(desc) + '</div>';
}

/* ============================================================
   Escalation Ladder
   ============================================================ */
function renderEscalationLadder() {
  var ladder = state.escalationLadder;
  if (!ladder || !$('escalationLadder')) return;

  var statusLabels = { crossed: 'Crossed', imminent: 'Imminent', threatened: 'Threatened', preparing: 'Preparing', not_crossed: 'Not crossed', de_escalating: 'De-escalating', suspended: 'Suspended', reversed: 'Reversed' };

  $('escalationLadder').innerHTML = '<div class="esc-ladder">' +
    ladder.map(function(r, i) {
      var isLast = i === ladder.length - 1;
      return '<div class="esc-rung ' + r.status + '">' +
        '<div class="esc-line"><div class="esc-dot"></div>' + (isLast ? '' : '<div class="esc-connector"></div>') + '</div>' +
        '<div class="esc-content">' +
          '<div class="esc-title">' + r.rung + '<span class="esc-status-tag">' + (statusLabels[r.status] || r.status) + '</span></div>' +
          '<div class="esc-meta"><span class="esc-date">' + r.date + '</span>' + r.detail + '</div>' +
        '</div></div>';
    }).join('') +
  '</div>';
}

/* ============================================================
   Timeline Scrubber
   ============================================================ */
function scrubberLabel(day, maxDay) {
  var labels = (state.dailySeries || {}).labels || [];
  var label = labels[day - 1] || ('D' + day);
  var isLive = day === maxDay;
  var cfStartDay = state.ceasefireStartIdx || CEASEFIRE_START_IDX;
  if (day >= cfStartDay) {
    var cfDay = day - cfStartDay + 1;
    return 'D' + day + ' / CF Day ' + cfDay + ' (' + label + ')' + (isLive ? ' — Live' : '');
  }
  return 'D' + day + ' (' + label + ')' + (isLive ? ' — Live' : '');
}

function initScrubber() {
  var wrap = $('scrubberWrap');
  var slider = $('scrubberSlider');
  if (!wrap || !slider || !state.dailySeries || !state.dailySeries.labels) return;

  var maxDay = state.dailySeries.labels.length;
  slider.max = maxDay;
  slider.value = maxDay;
  wrap.style.display = 'flex';
  if ($('scrubberDay')) $('scrubberDay').textContent = scrubberLabel(maxDay, maxDay);

  var cfStartDay = state.ceasefireStartIdx || CEASEFIRE_START_IDX;
  var labels = state.dailySeries.labels;

  // Clear old ticks before rebuilding
  wrap.querySelectorAll('.scrubber-tick,.scrubber-cf-marker,.scrubber-cf-label').forEach(function(n){ n.remove(); });

  // Add phase ticks: D1 war start, Ceasefire start, Apr 21 expiry, Today
  function addTick(dayIdx, klass, content) {
    if (dayIdx < 0 || dayIdx >= maxDay) return;
    var sliderRect = slider.getBoundingClientRect();
    var wrapRect = wrap.getBoundingClientRect();
    if (!sliderRect.width || !wrapRect.width) return;
    var sliderLeftInWrap = sliderRect.left - wrapRect.left;
    var rawFrac = maxDay > 1 ? (dayIdx / (maxDay - 1)) : 0;
    var wrapPct = ((sliderLeftInWrap + rawFrac * sliderRect.width) / wrapRect.width) * 100;
    var tick = document.createElement('div');
    tick.className = 'scrubber-tick ' + klass;
    tick.style.left = wrapPct + '%';
    tick.textContent = content;
    wrap.appendChild(tick);
  }

  requestAnimationFrame(function() {
    addTick(0, 'war-start', 'D1');
    if (cfStartDay <= maxDay) addTick(cfStartDay - 1, 'ceasefire-start', 'Ceasefire');
    var expiryIdx = labels.indexOf('Apr 21');
    if (expiryIdx >= 0) addTick(expiryIdx, 'expiry', 'Expiry');
    addTick(maxDay - 1, 'today', 'Today');
  });

  var scrubTimer = null;
  slider.addEventListener('input', function() {
    var self = this;
    if (scrubTimer) clearTimeout(scrubTimer);
    scrubTimer = setTimeout(function() {
      var day = parseInt(self.value);
      if ($('scrubberDay')) $('scrubberDay').textContent = scrubberLabel(day, maxDay);
      updateMetricsForDay(day);
    }, 50);
  });
}

function resetScrubber() {
  var slider = $('scrubberSlider');
  if (!slider) return;
  var maxDay = (state.dailySeries.labels || []).length;
  slider.value = maxDay;
  slider.dispatchEvent(new Event('input'));
}
window.resetScrubber = resetScrubber;

function updateMetricsForDay(day) {
  var ds = state.dailySeries || {};
  var oil = state.oil || {};
  var idx = day - 1;
  if (!ds.labels || !ds.labels.length) return;
  var maxDay = ds.labels.length;
  var isLive = day === maxDay;
  var cfStartDay = state.ceasefireStartIdx || CEASEFIRE_START_IDX;

  // Ceasefire mode: update ceasefire hero + countdown for scrubbed day
  if (currentMode === 'ceasefire') {
    renderCeasefireHero(idx);
    renderCeasefireCountdown(isLive ? undefined : idx);
    renderPostConflictTree(idx);
  }

  // If live day, recompute from dailySeries (not stale JSON strings)
  if (isLive) {
    // Recompute war-mode engine for live
    var liveEng = computeEngineForDay(idx);
    if (liveEng) {
      renderDecisionEngine(state.decisionEngine || {});
    }
    // Recompute metric cards from dailySeries
    var cumMissiles = 0; for (var li = 0; li <= idx; li++) cumMissiles += (ds.missiles[li] || 0);
    var cumDrones = 0; for (var lj = 0; lj <= idx; lj++) cumDrones += (ds.drones[lj] || 0);
    var liveOilIdx = Math.min(idx, (oil.brent || []).length - 1);
    var liveOil = (oil.brent || [])[liveOilIdx] || 0;
    var liveMetrics = [
      { label: 'Day of war', value: String(day), desc: ds.labels[idx] || '' },
      { label: 'Total missiles', value: '~' + cumMissiles.toLocaleString(), desc: 'Cumulative' },
      { label: 'Total drones', value: '~' + cumDrones.toLocaleString(), desc: 'Cumulative' },
      { label: 'Brent crude', value: '$' + liveOil.toFixed(2), desc: 'Latest' }
    ];
    if ($('metrics')) {
      $('metrics').innerHTML = liveMetrics.map(function(m) {
        return '<div class="metric"><div class="label">' + esc(m.label) + '</div><div class="value">' + esc(m.value) + '</div><div class="desc">' + esc(m.desc) + '</div></div>';
      }).join('');
    }
    return;
  }

  // Historical day: recompute engine
  var histEng = computeEngineForDay(idx);
  if (histEng && $('convergenceScore')) {
    $('convergenceScore').textContent = histEng.ensemble + '%';
    if ($('convergenceRaw')) $('convergenceRaw').textContent = histEng.modelProb + '% model';
    if ($('probBar')) {
      $('probBar').style.width = histEng.ensemble + '%';
      $('probBar').style.background = histEng.ensemble >= 50 ? 'var(--cyan)' : histEng.ensemble >= 25 ? 'var(--gold)' : 'var(--red)';
    }
  }

  // Update metric cards with historical values
  var metrics = state.metrics || [];
  if ($('metrics') && metrics.length >= 4) {
    var cards = $('metrics').querySelectorAll('.metric');
    // Day card
    if (cards[0]) cards[0].querySelector('.value').textContent = day;
    // Missiles cumul
    if (cards[1]) {
      var cumM = 0; for (var i = 0; i <= idx; i++) cumM += (ds.missiles[i] || 0);
      cards[1].querySelector('.value').textContent = '~' + cumM.toLocaleString();
    }
    // Drones cumul
    if (cards[2]) {
      var cumD = 0; for (var j = 0; j <= idx; j++) cumD += (ds.drones[j] || 0);
      cards[2].querySelector('.value').textContent = '~' + cumD.toLocaleString();
    }
    // Oil
    if (cards[3] && oil.brent && oil.brent.length) {
      var oilIdx = Math.min(idx, oil.brent.length - 1);
      cards[3].querySelector('.value').textContent = '$' + (oil.brent[oilIdx] || '—');
    }
  }

  // Update convergence/probability if vector data available for this day
  var v = (state.predictive || {}).vectors || {};
  if (v.militaryExhaustion && idx < v.militaryExhaustion.length) {
    var weights = [0.25, 0.20, 0.20, 0.20, 0.15];
    var vals = [
      v.militaryExhaustion[idx],
      v.economicPain[idx],
      v.diplomaticMomentum[idx],
      10 - v.usPoliticalSustainability[idx],
      10 - v.escalationCeilingDistance[idx]
    ];
    var score = 0;
    for (var k = 0; k < 5; k++) score += vals[k] * weights[k];
    var prob = Math.round(100 / (1 + Math.exp(-1.2 * (score - 5))));
    if ($('convergenceScore')) $('convergenceScore').textContent = prob + '%';
    if ($('convergenceRaw')) $('convergenceRaw').textContent = score.toFixed(1) + '/10';
    if ($('probBar')) {
      $('probBar').style.width = prob + '%';
      $('probBar').style.background = prob >= 70 ? 'var(--cyan)' : prob >= 40 ? 'var(--gold)' : 'var(--red)';
    }
  }
}

/* ============================================================
   Source Confidence Shading
   ============================================================ */
function applyConfidenceShading() {
  var conf = (state.dailySeries || {}).confidence;
  var note = (state.dailySeries || {}).confidenceNote;
  if (!conf || !note) return;
  // Add confidence warning to both launch chart footnotes
  var targets = ['missileFoot', 'droneFoot'];
  targets.forEach(function(id) {
    var el = $(id);
    if (el && el.getAttribute('data-conf') !== 'done') {
      el.innerHTML = el.innerHTML + '<br><span style="color:var(--gold);font-size:11px">&#9888; ' + note + '</span>';
      el.setAttribute('data-conf', 'done');
    }
  });
}

function render() {
  // Wrap each renderer so one failure doesn't cascade and blank out every
  // section that comes after it. Log to console for debugging.
  var safe = function(fn, name) {
    try { fn(); }
    catch (e) { console.error('[render] ' + name + ' failed:', e); }
  };

  safe(mountDashboard, 'mountDashboard');
  safe(applyI18n, 'applyI18n');
  safe(setText, 'setText');
  safe(renderCharts, 'renderCharts');

  // Ceasefire mode renders
  if (currentMode === 'ceasefire') {
    safe(renderCeasefireHero, 'renderCeasefireHero');
    safe(renderCeasefireCountdown, 'renderCeasefireCountdown');
    safe(renderPostConflictTree, 'renderPostConflictTree');
    safe(renderViolationTracker, 'renderViolationTracker');
    safe(renderNegotiationTracker, 'renderNegotiationTracker');
    safe(renderCeasefireRecovery, 'renderCeasefireRecovery');
  }

  // War mode renders (always call — CSS hides them in ceasefire mode)
  safe(renderPredictiveSection, 'renderPredictiveSection');
  safe(renderSimulator, 'renderSimulator');
  safe(renderSensitivity, 'renderSensitivity');
  safe(renderLeadingIndicators, 'renderLeadingIndicators');
  safe(renderChangelog, 'renderChangelog');
  safe(renderStockpile, 'renderStockpile');
  safe(renderAdditionalCharts, 'renderAdditionalCharts');
  safe(renderOilBands, 'renderOilBands');
  safe(renderHormuzTransit, 'renderHormuzTransit');
  safe(renderDeadline, 'renderDeadline');
  safe(renderEscalationLadder, 'renderEscalationLadder');
  safe(renderCoalition, 'renderCoalition');
  safe(renderDecapitation, 'renderDecapitation');
  safe(renderExpandedIranfarhang, 'renderExpandedIranfarhang');
  safe(renderExpandedKIP, 'renderExpandedKIP');
  safe(applyConfidenceShading, 'applyConfidenceShading');
  safe(initScrubber, 'initScrubber');
  safe(buildSectionNav, 'buildSectionNav');
  safe(markChangedSections, 'markChangedSections');

  // Update mode toggle button state
  document.querySelectorAll('.mode-btn').forEach(function(b) {
    b.classList.toggle('active', b.getAttribute('data-mode') === currentMode);
  });
}

async function loadDashboardData() {
  try {
    var response = await fetch('./war-data.json?ts=' + Date.now(), { cache: 'no-store' });
    if (!response.ok) throw new Error('No data file');
    var json = await response.json();
    if (!json.meta || !json.dailySeries || !json.oil) throw new Error('Malformed');
    state = { ...structuredClone(DEFAULT_DATA), ...json };
    state.meta = { ...DEFAULT_DATA.meta, ...(json.meta || {}) };
    // Auto-detect ceasefire mode
    if (state.ceasefireMode && state.ceasefireMode.enabled) {
      currentMode = 'ceasefire';
    } else {
      currentMode = 'war';
    }
    document.body.classList.toggle('ceasefire-mode', currentMode === 'ceasefire');
    document.body.classList.toggle('war-mode', currentMode === 'war');
  } catch(e) {
    console.error('Dashboard load failed:', e);
    state = structuredClone(DEFAULT_DATA);
  } finally { render(); }
}

loadDashboardData();

/* ---------- Topbar event wiring (replaces inline onclick=) ---------- */
(function wireTopbar() {
  document.querySelectorAll('.mode-btn[data-mode]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var m = btn.getAttribute('data-mode');
      if (m) setMode(m);
    });
  });
  var langBtn = document.getElementById('langToggle');
  if (langBtn) langBtn.addEventListener('click', toggleLang);
  var navToggle = document.getElementById('navToggle');
  var sectionNav = document.getElementById('sectionNav');
  if (navToggle && sectionNav) {
    navToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      sectionNav.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!sectionNav.classList.contains('open')) return;
      if (e.target === navToggle || sectionNav.contains(e.target)) return;
      sectionNav.classList.remove('open');
    });
  }
  var scrubReset = document.getElementById('scrubberReset');
  if (scrubReset) scrubReset.addEventListener('click', resetScrubber);
})();

/* ============================================================
   "What Changed" badges — highlight updated sections
   ============================================================ */
function markChangedSections() {
  try {
    var lastVisit = localStorage.getItem('iwd_lastData');
    if (!lastVisit) {
      // First visit — save current state, no badges
      localStorage.setItem('iwd_lastData', JSON.stringify(getDataFingerprint()));
      return;
    }
    var prev = JSON.parse(lastVisit);
    var curr = getDataFingerprint();

    // Compare each section and add badge if changed
    var changes = [];
    if (prev.day !== curr.day) changes.push({ label: 'Day ' + curr.day, sections: ['sec-0'] });
    if (prev.missiles !== curr.missiles) changes.push({ label: 'Launch data', q: '#missileChart' });
    if (prev.brent !== curr.brent) changes.push({ label: 'Oil', q: '#oilOverlayChart' });
    if (prev.convergence !== curr.convergence) changes.push({ label: 'Vectors', q: '#vectorChart' });
    if (prev.escalation !== curr.escalation) changes.push({ label: 'Scenarios', q: '#scenarioProbs' });
    if (prev.sitrep !== curr.sitrep) changes.push({ label: 'SITREP', q: '#theoryBox' });
    if (prev.hormuz !== curr.hormuz) changes.push({ label: 'Hormuz', q: '#hormuzTransitChart' });

    if (changes.length > 0) {
      // Show a banner
      var banner = document.createElement('div');
      banner.className = 'change-banner';
      banner.innerHTML = '<span class="change-dot"></span> Updated since your last visit: ' +
        changes.map(function(c) { return '<strong>' + c.label + '</strong>'; }).join(', ') +
        ' <button onclick="this.parentElement.remove();localStorage.setItem(\'iwd_lastData\',JSON.stringify(getDataFingerprint()))" style="margin-left:8px;background:none;border:1px solid var(--gold);color:var(--gold);border-radius:8px;padding:3px 10px;cursor:pointer;font-size:11px">Dismiss</button>';
      var shell = document.getElementById('mainShell');
      if (shell) shell.insertBefore(banner, shell.firstChild);
    }

    // Save current state
    localStorage.setItem('iwd_lastData', JSON.stringify(curr));
  } catch(e) { /* localStorage unavailable */ }
}

function getDataFingerprint() {
  var ds = state.dailySeries || {};
  var oil = state.oil || {};
  var wo = (state.predictive || {}).warOutcome || {};
  var sp = state.scenarioProbabilities || [];
  return {
    day: (ds.labels || []).length,
    missiles: (ds.missiles || []).slice(-1)[0] || 0,
    brent: (oil.brent || []).slice(-1)[0] || 0,
    convergence: wo.convergenceScore || 0,
    escalation: sp.length > 0 ? sp[0].prob : '',
    sitrep: ((state.sitrep || [])[0] || '').substring(0, 50),
    hormuz: ((state.hormuzTransit || {}).vessels || []).slice(-1)[0] || 0,
    updated: (state.meta || {}).lastUpdated || ''
  };
}
// Make accessible for dismiss button
window.getDataFingerprint = getDataFingerprint;
