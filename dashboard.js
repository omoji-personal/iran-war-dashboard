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
let dashboardMounted = false;
let state = {};
const charts = {};

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
  casualties: [], casualties_fa: [],
  humanitarian: [], humanitarian_fa: [],
  diplomacy: [], diplomacy_fa: [],
  publicOpinion: [], publicOpinion_fa: [],
  hormuz: [], hormuz_fa: [],
  keyActors: [], keyActors_fa: [],
  predictive: {},
  additionalCharts: {},
  iranfarhangExpanded: {},
  kipExpanded: {}
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
    if (s[key] !== undefined) el.innerHTML = s[key];
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
  var m = d.match(/D(\d+)/);
  return m ? parseInt(m[1], 10) : 0;
}

function kill(key) {
  if (charts[key]) { charts[key].destroy(); charts[key] = null; }
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
  el.innerHTML = items.map(function(t) { return '<li>' + t + '</li>'; }).join('');
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
  var out = [];
  var sum = 0, sumX = 0, sumXY = 0, sumX2 = 0, n = 0;
  for (var i = 0; i <= last; i++) {
    if (data[i] !== null && data[i] !== undefined) {
      sum += data[i]; sumX += i; sumXY += i * data[i]; sumX2 += i * i; n++;
    }
  }
  if (n < 2) return data.map(function() { return null; });
  var slope = (n * sumXY - sumX * sum) / (n * sumX2 - sumX * sumX);
  var intercept = (sum - slope * sumX) / n;
  for (var j = 0; j < data.length; j++) {
    out.push(j <= last ? Math.max(0, Math.round((slope * j + intercept) * 10) / 10) : null);
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
    x: { ticks: { color: '#7d8da1', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,.04)' } },
    y: { ticks: { color: '#7d8da1', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,.06)' } }
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
  if ($('lastUpdated')) $('lastUpdated').textContent = ts ? new Date(ts).toLocaleString() : '—';
  var fr = computeFreshness();
  if ($('freshnessStatus')) {
    $('freshnessStatus').innerHTML = '<span class="tag ' + fr.cls + '">' + fr.label + '</span>';
  }
  if ($('seriesThrough')) $('seriesThrough').textContent = state.dailySeries.throughDate || '—';

  // Theory box
  var theory = currentLang === 'fa' ? (state.theoryBox_fa || state.theoryBox) : state.theoryBox;
  if ($('theoryBox')) $('theoryBox').innerHTML = theory || '';

  // Metrics grid
  var metricsArr = currentLang === 'fa' ? (state.metrics_fa && state.metrics_fa.length ? state.metrics_fa : state.metrics) : state.metrics;
  if ($('metrics') && metricsArr) {
    $('metrics').innerHTML = metricsArr.map(function(m) {
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
    $('sourceNotes').innerHTML = '<div>' + short + '</div>';
  }

  // Footnotes
  if ($('missileFoot')) $('missileFoot').textContent = state.dailySeries.sourceLabel || '';
  if ($('droneFoot')) $('droneFoot').textContent = state.dailySeries.sourceLabel || '';
  if ($('oilFoot')) $('oilFoot').textContent = state.oil.note || '';

  // Target breakdown footnotes
  if ($('targetMissileFoot')) $('targetMissileFoot').textContent = (state.latestTargetBreakdown && state.latestTargetBreakdown.note) || '';
  if ($('targetDroneFoot')) $('targetDroneFoot').textContent = (state.latestTargetBreakdown && state.latestTargetBreakdown.note) || '';

  // Casualties
  var cas = L('casualties');
  if ($('casualtyBox') && cas.length) {
    $('casualtyBox').innerHTML = cas.map(function(c) {
      var color = c.statusColor === 'red' ? 'var(--red)' : c.statusColor === 'yellow' ? 'var(--gold)' : 'var(--cyan)';
      return '<div class="casualty-row"><div class="cas-group">' + c.group + '</div>' +
        '<div class="cas-figure" style="color:' + color + '">' + c.figure + '</div>' +
        '<div class="cas-detail">' + c.detail + '</div></div>';
    }).join('');
  }

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
      if (typeof r === 'string') return '<div class="route-card"><div class="route-detail">' + r + '</div></div>';
      return '<div class="route-card"><div class="route-header"><div class="route-name">' + (r.route || '') + '</div>' +
        '<span class="route-status ' + (r.statusColor || 'yellow') + '">' + (r.status || '') + '</span></div>' +
        '<div class="route-detail">' + (r.detail || '') + '</div>' +
        '<div class="route-meta"><span>' + (currentLang === 'fa' ? 'قابلیت: ' : 'Viability: ') + '<strong>' + (r.viability || '') + '</strong></span>' +
        '<span>' + (currentLang === 'fa' ? 'زمان: ' : 'ETA: ') + '<strong>' + (r.eta || '') + '</strong></span></div></div>';
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
    $('dailyRows').innerHTML = rows.map(function(r) {
      return '<tr><td>' + r.date + '</td><td><span class="pill missile">' + (r.missiles != null ? r.missiles : '\u2014') + '</span></td><td><span class="pill drone">' + (r.drones != null ? r.drones : '\u2014') + '</span></td>' +
        '<td>' + (r.primary || '\u2014') + '</td><td>' + (r.capability || '\u2014') + '</td><td>' + (r.cost || '\u2014') + '</td><td>' + (r.assessment || '\u2014') + '</td></tr>';
    }).join('');
  }

  // Timeline (array of {title, body} objects)
  var tl = L('timeline');
  if ($('timeline') && tl.length) {
    $('timeline').innerHTML = tl.map(function(t) {
      if (typeof t === 'string') return '<li>' + t + '</li>';
      return '<li><strong>' + (t.title || '') + ':</strong> ' + (t.body || '') + '</li>';
    }).join('');
  }

  // Scenario probabilities
  var sp = L('scenarioProbabilities');
  if ($('scenarioProbs') && sp.length) {
    $('scenarioProbs').innerHTML = sp.map(function(s) {
      return '<div class="scenario"><div><strong>' + s.name + '</strong><div style="font-size:12px;color:var(--soft);margin-top:4px;line-height:1.45">' + s.body + '</div></div><div class="prob">' + s.prob + '</div></div>';
    }).join('');
  }

  // Theory evaluation (array of {title, body} objects)
  var te = L('theoryEvaluation');
  if ($('theoryEval') && te.length) {
    $('theoryEval').innerHTML = te.map(function(t) {
      if (typeof t === 'string') return '<li>' + t + '</li>';
      return '<li><strong>' + (t.title || '') + ':</strong> ' + (t.body || '') + '</li>';
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
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: drones, backgroundColor: 'rgba(99,179,255,.5)', borderColor: '#63b3ff', borderWidth: 1, borderRadius: 4 },
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
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: drones, borderColor: '#63b3ff', backgroundColor: 'rgba(99,179,255,.08)', fill: true, tension: .22, borderWidth: 2.5, pointRadius: 3 }
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
          { label: currentLang === 'fa' ? 'پهپاد تجمعی' : 'Cumul. drones', data: cumD, borderColor: '#63b3ff', borderWidth: 2.5, tension: .22, pointRadius: 2 }
        ]
      },
      options: cuOpts
    });
  }

  // 5. Oil chart
  kill('oil');
  if ($('oilChart') && state.oil.labels) {
    var oOpts = deepClone(BASE_OPTS);
    oOpts.scales.y.ticks = { color: '#7d8da1', font: { size: 10 }, callback: function(v) { return '$' + v; } };
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
   NEW RENDER FUNCTIONS — Predictive Section
   ============================================================ */

function renderPredictiveSection() {
  var p = state.predictive || {};
  var outcome = p.warOutcome || {};
  var models = p.models || {};
  var vectors = p.vectors || {};

  // War outcome forecast
  var forecastText = currentLang === 'fa' ? (outcome.prediction_fa || outcome.prediction || '') : (outcome.prediction || '');
  if ($('outcomeForecast')) $('outcomeForecast').innerHTML = forecastText;

  // Convergence score
  if ($('convergenceScore')) $('convergenceScore').textContent = outcome.convergenceScore || '\u2014';
  var interpText = currentLang === 'fa' ? (outcome.convergenceInterpretation_fa || '') : (outcome.convergenceInterpretation || '');
  if ($('convergenceInterpretation')) $('convergenceInterpretation').textContent = interpText;

  // Model cards
  renderModelCards(models);

  // Thesis chart (two-model comparison)
  renderThesisChart(models);

  // Vector chart
  renderVectorChart(vectors);

  // Vector cards
  renderVectorCards(p.vectorNotes || {}, vectors);
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
  vecOpts.scales.y.ticks = { color: '#7d8da1', font: { size: 10 }, callback: function(v) {
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
    stackOpts.scales.y.ticks = { color: '#7d8da1', font: { size: 10 }, callback: function(v) { return v + '%'; } };

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
          { label: currentLang === 'fa' ? 'پهپاد' : 'Drones', data: countries.map(function(c) { return cbc[c].drones || 0; }), backgroundColor: 'rgba(99,179,255,.7)', borderRadius: 4 }
        ]
      },
      options: cbcOpts
    });
  }
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
  if ($('insuranceChart') && ins.labels) {
    var insOpts = deepClone(BASE_OPTS);
    insOpts.scales.y.ticks = { color: '#7d8da1', font: { size: 10 }, callback: function(v) { return v + '%'; } };
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

function render() {
  mountDashboard();
  applyI18n();
  setText();
  renderCharts();
  renderPredictiveSection();
  renderAdditionalCharts();
  renderExpandedIranfarhang();
  renderExpandedKIP();
}

async function loadDashboardData() {
  try {
    var response = await fetch('./war-data.json?ts=' + Date.now(), { cache: 'no-store' });
    if (!response.ok) throw new Error('No data file');
    var json = await response.json();
    if (!json.meta || !json.dailySeries || !json.oil) throw new Error('Malformed');
    state = { ...structuredClone(DEFAULT_DATA), ...json };
    state.meta = { ...DEFAULT_DATA.meta, ...(json.meta || {}) };
  } catch(e) {
    console.error('Dashboard load failed:', e);
    state = structuredClone(DEFAULT_DATA);
  } finally { render(); }
}

loadDashboardData();
