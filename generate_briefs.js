// Store Coach scheduled brief generator.
// Runs the same rule-based logic as the public app (index.html + data.js),
// unattended, for every area manager. Weekly issue assignments are kept in
// state/weekly.json (the app's own retention mechanism, backed by a file
// instead of browser localStorage). The data snapshot is fixed at the pack's
// "today" (31 Oct 2026); the execution time is stamped separately below and
// no fresh inputs are implied.
const fs = require('fs');

// --- durable weekly state: file-backed localStorage -----------------------
fs.mkdirSync('state', { recursive: true });
fs.mkdirSync('generated', { recursive: true });
const STATE_PATH = 'state/weekly.json';
let storeMap = {};
try { storeMap = JSON.parse(fs.readFileSync(STATE_PATH, 'utf8')); } catch (e) {}
const localStorage = {
  getItem: k => (k in storeMap ? storeMap[k] : null),
  setItem: (k, v) => { storeMap[k] = String(v); },
  removeItem: k => { delete storeMap[k]; }
};

// --- browser stubs, installed as globals like a real page -----------------
const __els = {};
globalThis.window = globalThis;
globalThis.localStorage = localStorage;
globalThis.document = {
  querySelectorAll: () => [],
  getElementById: id => __els[id] || (__els[id] = { innerHTML: "", innerText: "", disabled: false, style: {}, value: "", scrollIntoView: () => {} }),
  createElement: () => ({ style: {}, setAttribute: () => {} }),
  addEventListener: () => {},
  body: { appendChild: () => {} }
};

// --- load data + app logic into the global scope (as the browser would) ---
const html = fs.readFileSync('index.html', 'utf8');
const appScript = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
(0, eval)(fs.readFileSync('data.js', 'utf8') + "\n" + appScript);
const A_AGG = window.AGG;
const storeAlerts = globalThis.storeAlerts, buildBrief = globalThis.buildBrief,
      buildTeam = globalThis.buildTeam, S = globalThis.S;

function strip(h) {
  return h.replace(/<br\s*\/?>/g, '\n').replace(/<\/(p|div|tr|h\d|li)>/g, '\n')
    .replace(/<\/t[dh]>/g, ' | ').replace(/<[^>]+>/g, '')
    .replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ').replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim();
}

const execDate = new Date().toISOString().slice(0, 10);
const execStamp = new Date().toISOString();
const eventName = process.env.GITHUB_EVENT_NAME || '';
const runEnvEarly = eventName === 'schedule' ? 'unattended scheduled run (cron, GitHub Actions)'
  : eventName === 'workflow_dispatch' ? 'manual dispatch (workflow_dispatch, GitHub Actions)'
  : 'manual local run';
const out = { generated_at_utc: execStamp, data_as_of: A_AGG.data_as_of, note: "Rule-based generation from the fixed synthetic snapshot; execution time is the run time, not new data.", run_environment: runEnvEarly, managers: [] };
let md = "# Store Coach - scheduled brief generation\n\n";
const runEnv = runEnvEarly;
md += "Executed: " + execStamp + " (" + runEnv + ")\n";
md += "Data as of: " + A_AGG.data_as_of + " (fixed synthetic snapshot; no fresh inputs)\n\n";

for (const m of A_AGG.managers) {
  S.mgr = m.id;
  buildBrief();
  const briefHtml = __els.briefOut.innerHTML;
  const mRec = { manager: m.name, id: m.id, brief_text: strip(briefHtml), stores: {} };
  md += "## " + m.name + " (" + m.city + ")\n\n" + strip(briefHtml) + "\n\n";
  for (const sid of m.stores) {
    buildTeam(sid);
    const teamText = strip(__els.teamOut.innerHTML);
    mRec.stores[sid] = { alerts: storeAlerts(sid).map(a => ({ lever: a.lever, title: a.t, why: a.why, action: a.act, rupees_rough: a.rs != null ? Math.round(a.rs) : null, rupees_basis: a.rsHow || null })), team_text: teamText };
  }
  out.managers.push(mRec);
}

// the app's own brief text says "generated automatically in this browser";
// this run is the scheduled job, so restate that one phrase honestly
function scheduleWording(t) {
  if (typeof t !== 'string') return t;
  return t.replace(/generated automatically in this browser/g,
    'generated automatically by the scheduled job (same rules as the in-browser brief)')
    .replace(/retained for this snapshot week in this browser only/g,
    'retained for this snapshot week in the repo state file (state/weekly.json)');
}
for (const m of out.managers) {
  m.brief_text = scheduleWording(m.brief_text);
  for (const sid of Object.keys(m.stores)) m.stores[sid].team_text = scheduleWording(m.stores[sid].team_text);
}
md = scheduleWording(md);
fs.writeFileSync(STATE_PATH, JSON.stringify(storeMap, null, 1));
fs.writeFileSync('generated/briefs-latest.json', JSON.stringify(out, null, 1));
fs.writeFileSync('generated/briefs-latest.md', md);
fs.writeFileSync('generated/briefs-' + execDate + '.md', md);
console.log('managers:', out.managers.length, '| state keys:', Object.keys(storeMap).join(','), '| md bytes:', md.length);
process.exit(0);
