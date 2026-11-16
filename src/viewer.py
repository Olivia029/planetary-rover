"""Viewer: data computed with the project's code and a self-contained page."""
import json
import re
from pathlib import Path

from experiment import BLOCK_SIZE, BLOCKS, CONFIGS, curve
from tools import NAMES, env, table, world
from world import MAX_STEPS, ROCK, Cell

ROOT = Path(__file__).parent.parent
TRACES = ROOT / "data" / "traces.txt"
REQUIREMENTS = ROOT / "docs" / "requirements.md"
CASE = re.compile(r"^=== case \d+ ===$")
CALL = re.compile(r"^\[\d+\] (\w+) -> (.*)$")
REQ_ROW = re.compile(r"^\| (R\d) ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|")
# Requirements each tab shows evidence of; R6 and R7 are not in the viewer.
TAB_REQUIREMENTS = {"Map": ["R1"], "Route": ["R1", "R2"], "Policy": ["R2"],
                    "Learning": ["R3"], "Agent": ["R4", "R5"]}
NOT_SHOWN = ["R6", "R7"]


def record_route(start: Cell, letter: str) -> dict:
    """The loop of run_policy, recording every step."""
    goal = world.places[letter]
    state, _ = env.reset(options={"start": start, "destination": letter})
    cell, total, moves = start, 0.0, []
    done = start == goal
    while not done and len(moves) < MAX_STEPS:
        action = table.best_action(state)
        q = table.q[state].tolist()
        _, outcome = world.move(cell, action)  # label of the step only
        next_state, reward, terminated, truncated, _ = env.step(action)
        total += reward
        next_cell = env.unwrapped.cell
        moves.append({"cell": list(cell), "state": state, "q": q,
                      "action": action, "outcome": outcome,
                      "reward": reward, "next": list(next_cell),
                      "total": total})
        cell, state = next_cell, next_state
        done = terminated or truncated
    return {"origin": list(start), "destination": letter,
            "reached": cell == goal, "steps": len(moves), "return": total,
            "shortest": world.shortest_steps(start, goal), "moves": moves}


def policy_of(letter: str) -> list[dict]:
    entries = []
    for cell in world.free_cells():
        options = {"start": cell, "destination": letter}
        state, _ = env.reset(options=options)
        entries.append({"cell": list(cell), "state": state,
                        "action": table.best_action(state),
                        "value": float(table.q[state].max())})
    return entries


def parse_traces(text: str) -> list[dict]:
    """Cases printed by src/main.py: request, tool lines and answer."""
    cases: list[dict] = []
    case, in_answer = None, False
    for line in text.splitlines():
        line = line.rstrip()
        if CASE.match(line):
            case = {"request": "", "trace": [], "answer": ""}
            cases.append(case)
            in_answer = False
        elif case is None:
            continue
        elif in_answer:
            case["answer"] += "\n" + line
        elif line.startswith("request: "):
            case["request"] = line.removeprefix("request: ")
        elif match := CALL.match(line):
            case["trace"].append({"tool": match[1], "result": match[2]})
        elif line.startswith("answer: "):
            case["answer"] = line.removeprefix("answer: ")
            in_answer = True
    for case in cases:
        case["answer"] = case["answer"].strip()
    return cases


def parse_requirements(text: str) -> dict[str, dict]:
    """R1-R7 from the table of docs/requirements.md: name, demand, where."""
    requirements = {}
    for line in text.splitlines():
        match = REQ_ROW.match(line)
        if not match:
            continue
        rid, name, demands, where = match.groups()
        tokens = re.findall(r"`([^`]+)`", where)
        refs = [token for token in tokens if "::" in token]
        files = []
        for token in tokens:
            path = token.split("::")[0]
            if (ROOT / path).exists() and path not in files:
                files.append(path)
        requirements[rid] = {"id": rid, "name": name,
                             "demands": demands.replace("`", ""),
                             "files": files, "refs": refs}
    return requirements

def build_data() -> dict:
    cells = [(r, c) for r in range(world.rows) for c in range(world.cols)]
    places = {letter: {"cell": list(cell), "name": NAMES[letter]}
              for letter, cell in world.places.items()}
    routes = [record_route(start, letter)
              for letter, goal in world.places.items()
              for start in world.free_cells() if start != goal]
    episodes = [BLOCK_SIZE * (i + 1) for i in range(BLOCKS)]
    curves = [{"label": f"alpha={alpha} gamma={gamma}", "alpha": alpha,
               "gamma": gamma, "episodes": episodes,
               "rates": curve(alpha, gamma)} for alpha, gamma in CONFIGS]
    text = TRACES.read_text(encoding="utf-8")
    requirements = parse_requirements(
        REQUIREMENTS.read_text(encoding="utf-8"))
    used = [rid for ids in TAB_REQUIREMENTS.values() for rid in ids]
    missing = sorted(set(used + NOT_SHOWN) - set(requirements))
    if missing:
        raise ValueError(f"not in docs/requirements.md: {missing}")
    return {
        "world": {"rows": world.rows, "cols": world.cols,
                  "symbols": world.grid, "heights": world.heights,
                  "places": places,
                  "max_height": max(world.height(cell) for cell in cells
                                    if world.symbol(cell) != ROCK)},
        "routes": routes,
        "policy": {letter: policy_of(letter) for letter in world.places},
        "curves": curves,
        "traces": parse_traces(text),
        "requirements": requirements,
        "tab_requirements": TAB_REQUIREMENTS,
        "not_shown": NOT_SHOWN,
    }


def page(data: dict) -> str:
    """The page with the data inline (also served by src/serve.py)."""
    payload = json.dumps(data).replace("</", "<\\/")
    return PAGE.replace("__DATA__", payload)


def write_html(path: str | Path) -> dict:
    data = build_data()
    Path(path).write_text(page(data), encoding="utf-8")
    return data


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rover viewer</title>
<style>
:root{--bg:#1a1210;--panel:#241915;--line:#3d2b22;--ink:#f1e4d0;
--muted:#bfa98d;--sand:#e0b97a;--rust:#c4522a}
*{box-sizing:border-box}
html,body{margin:0;height:100%;overflow:hidden}
body{background:var(--bg);color:var(--ink);min-width:960px;height:100vh;
font:14px/1.45 system-ui,-apple-system,sans-serif;display:grid;
grid-template-columns:220px 1fr;grid-template-rows:auto 1fr auto}
aside{grid-row:1/3;background:var(--panel);padding:16px;overflow:auto;
border-right:1px solid var(--line)}
aside h1{font-size:18px;margin:0;color:var(--sand)}
aside h2{font-size:15px;color:var(--sand);margin:22px 0 2px;
padding-bottom:4px;border-bottom:1px solid var(--line)}
aside h3{font-size:12px;text-transform:uppercase;letter-spacing:.08em;
color:var(--muted);margin:14px 0 6px}
.icon{display:flex;gap:8px;align-items:center;margin:4px 0;font-size:13px}
.reqs{display:flex;gap:6px;flex-wrap:wrap;align-items:flex-start;
margin-bottom:12px;font-size:12px}
.reqs>span{color:var(--muted);padding-top:4px}
details.req{background:#2a1d17;border:1px solid #5a3a28;border-radius:6px;
padding:3px 9px;max-width:560px}
details.req[open]{border-color:var(--sand)}
.req summary{cursor:pointer}
.req summary:focus-visible{outline:2px solid var(--sand);outline-offset:2px}
.req summary b{color:var(--sand)}
.req .files{color:var(--muted);font:11px ui-monospace,Menlo,monospace}
.req p{margin:6px 0 2px}
.req code{display:block;font-size:11px}
.out{font-size:12px;margin:6px 0}
.out b{color:var(--sand)}
.icon svg{width:28px;height:28px;flex:none;border-radius:4px}
nav{display:flex;gap:6px;padding:10px 16px;border-bottom:1px solid
var(--line)}
main{overflow:auto;padding:16px 20px}
footer{grid-column:1/3;display:flex;gap:16px;align-items:center;
padding:6px 16px;background:var(--panel);border-top:1px solid var(--line);
font-size:13px}
button{font:inherit;color:var(--ink);background:#2e211b;cursor:pointer;
border:1px solid var(--line);border-radius:6px;padding:4px 12px}
button:hover:not(:disabled){border-color:var(--sand)}
button:focus-visible,.pick:focus-visible{outline:2px solid var(--sand);
outline-offset:2px}
button[aria-pressed=true]{background:var(--rust);border-color:var(--rust);
color:#fff}
button:disabled{opacity:.55;cursor:not-allowed}
.bar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;
margin-bottom:12px}
.row{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}
.card{background:var(--panel);border:1px solid var(--line);
border-radius:8px;padding:10px 14px}
.muted{color:var(--muted)}
.mode{background:#3a281e;color:var(--sand);border-radius:10px;
padding:2px 10px;font-weight:600}
.badge{display:inline-block;background:#3a281e;color:var(--sand);
border-radius:9px;padding:0 8px;font-size:12px;margin-right:4px}
.place{display:flex;gap:8px;align-items:center;margin:6px 0}
.dot{width:24px;height:24px;border-radius:50%;background:var(--rust);
display:grid;place-items:center;font-weight:700;color:#fff;
border:2px solid var(--sand)}
.legend{display:flex}
.legend span{flex:1;text-align:center;font-size:11px;padding:2px 0;
color:#fff;text-shadow:0 0 2px #000}
svg.grid{width:470px;height:auto;display:block;flex:none}
svg.small{width:340px}
.hn{font-size:10px;fill:#fff;stroke:#000;stroke-width:2px;
paint-order:stroke}
.pb{fill:var(--rust);stroke:var(--sand);stroke-width:2}
.pl{fill:#fff;font-weight:700;font-size:13px;text-anchor:middle}
.arrow{fill:#fff;stroke:#000;stroke-width:2px;paint-order:stroke;
font-size:22px;text-anchor:middle}
.qv{fill:#fff;stroke:#000;stroke-width:2px;paint-order:stroke;
font-size:11px;text-anchor:middle}
.pick{cursor:pointer}
.origin rect{stroke:var(--sand);stroke-width:3}
.trail{fill:none;stroke:var(--sand);stroke-width:3;stroke-dasharray:5 4}
.rover{fill:#fff;stroke:var(--rust);stroke-width:4}
.bump{animation:bump .3s 2}
@keyframes bump{50%{stroke:#ffd166;stroke-width:8}}
.flash rect{animation:flash .35s 4}
@keyframes flash{50%{fill:#ff3b1f}}
table{border-collapse:collapse;font-size:12px}
th,td{border-bottom:1px solid var(--line);padding:3px 5px;
text-align:right;white-space:nowrap}
th{color:var(--muted);font-weight:600}
.q span{margin-left:6px}
.best{color:var(--sand);font-weight:700;text-decoration:underline}
.o-hazard{color:#ff6b4a;font-weight:700}
.o-blocked{color:#ffd166}
.gl{stroke:#3d2b22}
.ax{fill:var(--muted);font-size:11px}
.dl{fill:var(--ink);font-size:11px}
.target{stroke:#9a8f85;stroke-dasharray:6 4}
.case{margin-bottom:12px;max-width:900px}
.call{margin:4px 0}
code{font:12px ui-monospace,Menlo,monospace;color:var(--muted)}
pre{white-space:pre-wrap;font:inherit;margin:4px 0 0}
pre strong{color:var(--sand)}
code.inline{color:var(--ink);background:#2e211b;border-radius:4px;
padding:1px 5px}
input{font:inherit;color:var(--ink);background:#2e211b;width:560px;
border:1px solid var(--line);border-radius:6px;padding:5px 10px}
input:focus-visible{outline:2px solid var(--sand)}
.live{background:#1f3b2c;color:#9be3b5}
.error{color:#ff8a6b}
</style>
</head>
<body>
<aside>
<h1>Planetary rover</h1>
<div class="muted">Mars grid, Q table and agent</div>
<h2>Legend</h2>
<h3>Places</h3><div id="places"></div>
<h3>Height</h3><div class="legend" id="legend"></div>
<div class="muted" style="font-size:12px">low (dark) to high (sand)</div>
<h3>Terrain</h3><div id="terrain"></div>
<h2>Requirements</h2>
<div class="muted" style="font-size:12px">Each tab lists the requirements
it shows. Not shown in the viewer:</div>
<div id="notshown"></div>
</aside>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<defs>
<linearGradient id="g-rock" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#b3aaa0"/><stop offset=".45"
stop-color="#7a716a"/><stop offset="1" stop-color="#3d3733"/>
</linearGradient>
<radialGradient id="g-bowl" cx=".42" cy=".4" r=".7" fx=".3" fy=".25">
<stop offset="0" stop-color="#0d0805"/><stop offset=".55"
stop-color="#2b1a10"/><stop offset="1" stop-color="#8a6240"/>
</radialGradient>
<radialGradient id="g-rim" cx=".5" cy=".5" r=".5">
<stop offset=".7" stop-color="#8f6a47"/><stop offset=".9"
stop-color="#c9a27a"/><stop offset="1" stop-color="#6b4a30"/>
</radialGradient>
</defs></svg>
<nav>
<button id="b-Map">Map</button>
<button id="b-Route">Route</button>
<button id="b-Policy">Policy</button>
<button id="b-Learning">Learning</button>
<button id="b-Agent">Agent</button>
</nav>
<main>
<section id="tab-Map">
<div class="bar dests"></div>
<div class="row"><svg id="gmap" class="grid"></svg>
<div class="card" id="hover">Hover a cell to see its symbol, height
and state number.</div></div>
</section>
<section id="tab-Route" hidden>
<div class="bar dests"></div>
<div class="bar"><button id="play">Run</button>
<button id="pause">Pause</button><button id="next">Step</button>
<button id="back">Back</button><button id="reset">Reset</button>
<label class="muted">Speed <select id="speed">
<option value="900">slow</option><option value="500" selected>normal
</option><option value="200">fast</option></select></label>
<span class="muted">Click a free cell to choose the origin.</span></div>
<div class="row"><div><svg id="groute" class="grid small"></svg>
<div class="card" id="result" style="margin-top:10px"></div></div>
<table><thead><tr><th>#</th><th>cell, h</th>
<th>state = d x cells + r x cols + c</th><th>Q up, right, down, left
</th><th>action</th><th>outcome</th><th>reward</th><th>return</th></tr>
</thead><tbody id="steps"></tbody></table></div>
</section>
<section id="tab-Policy" hidden>
<div class="bar dests"></div>
<div class="bar"><span class="muted">Show:</span>
<button id="v-arrows">Arrows</button><button id="v-heat">Heat map
</button><span class="muted" id="heatlegend"></span></div>
<svg id="gpol" class="grid"></svg>
</section>
<section id="tab-Learning" hidden>
<div class="bar" id="series"></div>
<svg id="chart" style="width:680px;height:auto;display:block"></svg>
<table id="values" style="margin-top:12px"></table>
</section>
<section id="tab-Agent" hidden>
<div class="bar"><button id="m-saved" aria-pressed="true">Saved results
</button><button id="m-live" disabled>Live chat</button>
<span class="muted" id="why">Live chat: start it with
<code>uv run python src/serve.py</code> (needs Ollama and qwen3:4b).
</span></div>
<div id="saved">
<p class="muted">Saved output of <code>src/main.py</code>; tool results
are cut at 52 characters, as the agent printed them.</p>
<div id="cases"></div></div>
<div id="live" hidden>
<p class="muted">Live chat with qwen3:4b via Ollama. Nothing is saved:
closing the page loses the chat.</p>
<form class="bar" id="ask"><label for="text" class="muted">Request</label>
<input id="text" maxlength="500" autocomplete="off"
placeholder="The rover is at the base. How does it reach the antenna?">
<button id="send">Send</button></form>
<div class="muted" id="wait" hidden>qwen3:4b is thinking...</div>
<div id="chat"></div></div>
</section>
</main>
<footer><span class="mode" id="mode">Saved results - no model</span>
<span id="st"></span></footer>
<script type="application/json" id="data">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const W = D.world, L = Object.keys(W.places);
const NS = 'http://www.w3.org/2000/svg', C = 50;
const TABS = ['Map', 'Route', 'Policy', 'Learning', 'Agent'];
const ACT = ['↑ up', '→ right', '↓ down', '← left'];
const ARROW = ['↑', '→', '↓', '←'];
const SER = ['#3987e5', '#d95926', '#199e70'];
const S = {dest: 'M', origin: W.places.B.cell, idx: 0, timer: null,
           view: 'arrows'};
const R = {}, P = {};
D.routes.forEach(x => { R[x.origin + '>' + x.destination] = x; });
L.forEach(d => { P[d] = {};
  D.policy[d].forEach(p => { P[d][p.cell] = p; }); });
const $ = id => document.getElementById(id);
const f1 = x => x.toFixed(1), f2 = x => x.toFixed(2);
const sym = (r, c) => W.symbols[r][c];
function h(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}
function s(tag, attrs, text) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs || {}) e.setAttribute(k, attrs[k]);
  if (text != null) e.textContent = text;
  return e;
}
function mix(lo, hi, t) {
  return 'rgb(' + lo.map((v, i) => Math.round(v + (hi[i] - v) * t))
    .join(',') + ')';
}
const HMAX = 9;  // heights are the digits 0-9
const hcol = v => mix([59, 36, 22], [236, 217, 176], v / HMAX);

const ROCK_GROUND = '#3a312b';
function rock(g) {  // a boulder with facets, a cast shadow and a pebble
  const k = s('g', {transform: `scale(${C / 50})`});
  k.append(
    s('ellipse', {cx: 26, cy: 42, rx: 19, ry: 4.5, fill: 'rgba(0,0,0,.45)'}),
    s('polygon', {points: '8,38 6,27 12,16 24,9 36,11 45,22 44,35 34,41 18,42',
      fill: 'url(#g-rock)', stroke: '#221d1a', 'stroke-width': 1.5,
      'stroke-linejoin': 'round'}),
    s('path', {d: 'M12 16 L23 23 L24 9 M23 23 L31 28 L45 22 M31 28 L34 41'
      + ' M23 23 L16 34', fill: 'none', stroke: 'rgba(0,0,0,.35)',
      'stroke-width': 1.2}),
    s('path', {d: 'M7 27 L12 16 L24 9 L36 11', fill: 'none',
      stroke: 'rgba(255,255,255,.35)', 'stroke-width': 1.5}),
    s('ellipse', {cx: 43, cy: 43, rx: 4, ry: 2.8, fill: '#857c74',
      stroke: '#2a2421'}),
    s('ellipse', {cx: 8, cy: 43, rx: 2.5, ry: 1.8, fill: '#6f665f'}));
  g.append(k);
}
function crater(g) {  // ejecta, a lit rim and a shaded bowl
  const k = s('g', {transform: `scale(${C / 50})`});
  k.append(s('ellipse', {cx: 25, cy: 26, rx: 20, ry: 17,
    fill: 'rgba(60,35,20,.4)'}));
  [[6, 14], [44, 13], [45, 38], [7, 40], [17, 6], [36, 46], [3, 27]]
    .forEach(([x, y]) => k.append(s('circle', {cx: x, cy: y, r: 1.5,
      fill: '#4a3020'})));
  k.append(
    s('ellipse', {cx: 25, cy: 26, rx: 16, ry: 13.5, fill: 'url(#g-rim)'}),
    s('ellipse', {cx: 25, cy: 26.5, rx: 12, ry: 10, fill: 'url(#g-bowl)'}),
    s('path', {d: 'M14 29 A12 10 0 0 0 36 29', fill: 'none',
      stroke: 'rgba(255,225,180,.5)', 'stroke-width': 1.5}),
    s('path', {d: 'M12 25 A13 11 0 0 1 35 17', fill: 'none',
      stroke: 'rgba(0,0,0,.45)', 'stroke-width': 2}));
  g.append(k);
}

function grid(svg, o) {
  svg.replaceChildren();
  svg.setAttribute('viewBox', `0 0 ${W.cols * C} ${W.rows * C}`);
  for (let r = 0; r < W.rows; r++) for (let c = 0; c < W.cols; c++) {
    const k = sym(r, c), hgt = W.heights[r][c];
    const g = s('g', {transform: `translate(${c * C},${r * C})`});
    const fill = k === '#' ? ROCK_GROUND
      : (o.fill ? o.fill(r, c) : hcol(hgt));
    g.append(s('rect', {x: 1, y: 1, width: C - 2, height: C - 2, rx: 4,
                        fill}));
    if (k === '#') rock(g);
    if (k === '~') crater(g);
    if (k !== '#') g.append(s('text', {x: 4, y: 12, class: 'hn'}, hgt));
    if (W.places[k]) g.append(
      s('circle', {cx: C / 2, cy: C / 2, r: 12, class: 'pb'}),
      s('text', {x: C / 2, y: C / 2 + 5, class: 'pl'}, k));
    if (o.cell) o.cell(g, r, c);
    if (o.pick && P[S.dest][r + ',' + c]) {
      g.setAttribute('tabindex', 0); g.classList.add('pick');
      g.onclick = () => o.pick(r, c);
      g.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); o.pick(r, c); } };
    }
    if (o.hover) g.onmouseenter = g.onfocus = () => o.hover(r, c);
    svg.append(g);
  }
}

function showCell(r, c) {
  const k = sym(r, c), p = P[S.dest][r + ',' + c];
  const what = W.places[k] ? `place ${k} (${W.places[k].name})`
    : {'.': 'free ground', '#': 'rock', '~': 'crater'}[k];
  const state = p ? `State for destination ${S.dest}: ${p.state}`
    : k === '#' ? 'Rock: the rover never enters it'
    : 'Crater: entering it is a hazard (-50, end)';
  $('hover').replaceChildren(h('h3', null, `Cell (${r}, ${c})`),
    h('div', null, `Symbol '${k}': ${what}`),
    h('div', null, k === '#' ? 'Height: ignored (rock)'
      : `Height: ${W.heights[r][c]}`), h('div', null, state));
}

const cur = () => R[S.origin + '>' + S.dest];
function stop() { clearInterval(S.timer); S.timer = null; }
function reset() { stop(); S.idx = 0; renderRoute(); }
function step(d) {
  const x = cur(); if (!x) return;
  S.idx = Math.max(0, Math.min(x.moves.length, S.idx + d));
  if (S.idx >= x.moves.length) stop();
  renderRoute();
}
function play() {
  const x = cur(); if (!x || S.timer) return;
  if (S.idx >= x.moves.length) S.idx = 0;
  S.timer = setInterval(() => step(1), +$('speed').value);
}
function renderRoute() {
  const x = cur(), mv = x ? x.moves.slice(0, S.idx) : [];
  const last = mv[mv.length - 1], svg = $('groute');
  grid(svg, {pick: (r, c) => { S.origin = [r, c]; reset(); },
    cell: (g, r, c) => { const key = r + ',' + c;
      if (last && last.outcome === 'hazard' && last.next + '' === key)
        g.classList.add('flash');
      if (S.origin + '' === key) g.classList.add('origin'); }});
  const pts = [S.origin, ...mv.map(m => m.next)]
    .map(([r, c]) => `${c * C + C / 2},${r * C + C / 2}`).join(' ');
  svg.append(s('polyline', {points: pts, class: 'trail'}));
  const [r, c] = last ? last.next : S.origin;
  svg.append(s('circle', {cx: c * C + C / 2, cy: r * C + C / 2, r: 9,
    class: 'rover' + (last && last.outcome === 'blocked' ? ' bump' : '')}));
  const di = L.indexOf(S.dest), n = W.rows * W.cols;
  $('steps').replaceChildren(...mv.map((m, i) => {
    const [mr, mc] = m.cell, q = h('td', 'q'), tr = h('tr');
    m.q.forEach((v, a) =>
      q.append(h('span', a === m.action ? 'best' : '', f2(v))));
    tr.append(h('td', null, i + 1),
      h('td', null, `(${mr}, ${mc}) ${W.heights[mr][mc]}`),
      h('td', null, `${di}x${n} + ${mr}x${W.cols} + ${mc} = ${m.state}`),
      q, h('td', null, ACT[m.action]), h('td', 'o-' + m.outcome, m.outcome),
      h('td', null, f1(m.reward)), h('td', null, f1(m.total)));
    return tr;
  }));
  const rows = x ? [['reached', x.reached ? 'yes' : 'no'],
    ['steps', x.steps], ['return', f1(x['return'])],
    ['BFS shortest steps', x.shortest ?? 'none']]
    : [['origin is the destination', '0 steps']];
  $('result').replaceChildren(...rows.map(([k, v]) => {
    const d = h('div'); d.append(h('span', 'muted', k + ': '),
      h('b', null, v)); return d; }));
  const m = last;
  $('st').textContent = `origin (${S.origin.join(', ')}) | destination `
    + `${S.dest} | steps ${S.idx}${x ? ' / ' + x.steps : ''} | return `
    + `${f1(m ? m.total : 0)} | last step: ${m ? m.outcome : '-'}`;
}

function renderPolicy() {
  const ps = D.policy[S.dest], vs = ps.map(p => p.value);
  const lo = Math.min(...vs), hi = Math.max(...vs);
  const goal = W.places[S.dest].cell + '', heat = S.view === 'heat';
  grid($('gpol'), {fill: heat ? (r, c) => { const p = P[S.dest][r + ',' + c];
      return p ? mix([40, 24, 16], [240, 176, 96],
        (p.value - lo) / ((hi - lo) || 1)) : hcol(W.heights[r][c]); }
      : null,
    cell: (g, r, c) => { const p = P[S.dest][r + ',' + c];
      if (!p || r + ',' + c === goal) return;
      g.append(s('title', null,
        `(${r}, ${c}) best ${ACT[p.action]}, max Q ${f2(p.value)}`));
      const corner = W.places[sym(r, c)];
      if (heat) g.append(s('text', {x: C / 2, y: corner ? C - 4 : C / 2 + 4,
        class: 'qv'}, f1(p.value)));
      else g.append(s('text', {x: corner ? C - 10 : C / 2,
        y: corner ? C - 4 : C / 2 + 8, class: 'arrow'}, ARROW[p.action]));
    }});
  $('heatlegend').textContent = heat
    ? `largest Q: dark ${f2(lo)} to bright ${f2(hi)}` : '';
  $('v-arrows').setAttribute('aria-pressed', !heat);
  $('v-heat').setAttribute('aria-pressed', heat);
}

function renderLearning() {
  const svg = $('chart'), w = 680, ht = 320;
  const m = {l: 48, r: 140, t: 14, b: 42}, eps = D.curves[0].episodes;
  const X = e => m.l + (e - eps[0]) / (eps.at(-1) - eps[0])
    * (w - m.l - m.r);
  const Y = v => ht - m.b - v / 105 * (ht - m.t - m.b);
  svg.setAttribute('viewBox', `0 0 ${w} ${ht}`);
  for (let v = 0; v <= 100; v += 20) svg.append(
    s('line', {x1: m.l, x2: w - m.r, y1: Y(v), y2: Y(v), class: 'gl'}),
    s('text', {x: m.l - 8, y: Y(v) + 4, class: 'ax',
               'text-anchor': 'end'}, v));
  eps.forEach(e => svg.append(s('text', {x: X(e), y: ht - m.b + 16,
    class: 'ax', 'text-anchor': 'middle'}, e)));
  svg.append(s('text', {x: (m.l + w - m.r) / 2, y: ht - 6, class: 'ax',
    'text-anchor': 'middle'}, 'training episodes'),
    s('text', {x: 12, y: ht / 2, class: 'ax', 'text-anchor': 'middle',
      transform: `rotate(-90 12 ${ht / 2})`}, '% of shortest routes'),
    s('line', {x1: m.l, x2: w - m.r, y1: Y(95), y2: Y(95),
               class: 'target'}),
    s('text', {x: m.l + 6, y: Y(95) - 6, class: 'ax'}, '95 % target'));
  D.curves.forEach((k, i) => {
    svg.append(s('polyline', {fill: 'none', stroke: SER[i],
      'stroke-width': 2, points: k.episodes
        .map((e, j) => X(e) + ',' + Y(k.rates[j])).join(' ')}));
    k.episodes.forEach((e, j) => { const g = s('g');
      g.append(s('circle', {cx: X(e), cy: Y(k.rates[j]), r: 4,
          fill: SER[i], stroke: '#241915', 'stroke-width': 2}),
        s('circle', {cx: X(e), cy: Y(k.rates[j]), r: 10,
          fill: 'transparent'}),
        s('title', null, `${k.label}: ${f1(k.rates[j])} % after ${e}`
          + ' episodes'));
      svg.append(g); });
    const y = Y(k.rates.at(-1));
    svg.append(s('line', {x1: w - m.r + 6, x2: w - m.r + 18, y1: y,
      y2: y, stroke: SER[i], 'stroke-width': 3}),
      s('text', {x: w - m.r + 22, y: y + 4, class: 'dl'}, k.label));
  });
  $('series').replaceChildren(...D.curves.map((k, i) => {
    const b = h('span', 'badge'); b.style.borderLeft = `12px solid ${SER[i]}`;
    b.textContent = k.label; return b; }));
  const head = h('tr'); head.append(h('th', null, 'episodes'),
    ...eps.map(e => h('th', null, e)));
  $('values').replaceChildren(head, ...D.curves.map(k => {
    const tr = h('tr'); tr.append(h('th', null, k.label),
      ...k.rates.map(v => h('td', null, f1(v)))); return tr; }));
}

function caseCard(t, title) {
  const card = h('article', 'card case'), head = h('div', 'bar');
  head.append(h('b', null, title),
    ...t.trace.map(x => h('span', 'badge', x.tool)));
  if (!t.trace.length) head.append(h('span', 'muted', 'no tool called'));
  card.append(head, h('div', null, 'Request: ' + t.request));
  t.trace.forEach(x => { const d = h('div', 'call');
    d.append(h('span', 'badge', x.tool), h('code', null, x.result));
    card.append(d); });
  card.append(h('div', 'muted', 'Answer'), markdown(t.answer));
  return card;
}
function markdown(text) {  // **bold** and `code`; everything else as text
  const out = h('pre');
  text.split(/(\*\*[^*\n]+\*\*|`[^`\n]+`)/).forEach(part => {
    if (/^\*\*[^*]+\*\*$/.test(part))
      out.append(h('strong', null, part.slice(2, -2)));
    else if (/^`[^`]+`$/.test(part))
      out.append(h('code', 'inline', part.slice(1, -1)));
    else if (part) out.append(part);
  });
  return out;
}
function renderAgent() {
  $('cases').replaceChildren(...D.traces.map((t, i) =>
    caseCard(t, `Case ${i + 1}`)));
}

const MODEL = 'qwen3:4b';
function setMode(live) {
  $('m-saved').setAttribute('aria-pressed', !live);
  $('m-live').setAttribute('aria-pressed', live);
  $('saved').hidden = live; $('live').hidden = !live;
  $('mode').classList.toggle('live', live);
  $('mode').textContent = live ? `Live - Ollama - ${MODEL}`
    : 'Saved results - no model';
}
async function checkLive() {
  let st = null;
  if (location.protocol.startsWith('http')) {
    try { const r = await fetch('api/status'); if (r.ok) st = await r.json(); }
    catch (e) { st = null; }
  }
  if (!st) return;  // not started with serve.py: keep the saved results
  if (!st.ollama) { $('why').textContent = 'Live chat is off: Ollama is '
    + 'not running. Open the Ollama app, then reload this page.'; return; }
  if (!st.installed) { $('why').textContent = `Live chat is off: ${MODEL} `
    + `is not installed. Run ollama pull ${MODEL}, then reload.`; return; }
  $('why').textContent = `Connected: ${MODEL} via Ollama.`;
  $('m-live').disabled = false; setMode(true);
}
async function send(e) {
  e.preventDefault();
  const text = $('text').value.trim(); if (!text) return;
  $('send').disabled = true; $('wait').hidden = false;
  let card;
  try {
    const r = await fetch('api/chat', {method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({request: text})});
    const x = await r.json();
    if (!r.ok) throw new Error(x.error || `the server answered ${r.status}`);
    card = caseCard({request: text, trace: x.trace, answer: x.answer},
      `${MODEL} via Ollama`);
    card.append(h('div', 'muted',
      'The numbers come from the tools, not from the model.'));
    if (x.route) {
      stop(); S.origin = x.route.origin; S.dest = x.route.destination;
      S.idx = 0; renderAll(); play();
      const b = h('button', null, 'See the route on the Route tab');
      b.onclick = () => show('Route'); card.append(b);
    }
  } catch (err) {
    const why = err instanceof TypeError
      ? 'the server did not answer. Is serve.py still running?'
      : err.message;
    card = h('article', 'card case');
    card.append(h('b', null, `${MODEL} via Ollama`),
      h('div', null, 'Request: ' + text),
      h('div', 'error', 'The request failed: ' + why));
  }
  $('chat').append(card); card.scrollIntoView({block: 'nearest'});
  $('send').disabled = false; $('wait').hidden = true; $('text').value = '';
}

function dests() {
  document.querySelectorAll('.dests').forEach(box => {
    box.replaceChildren(h('span', 'muted', 'Destination:'),
      ...L.map(d => { const b = h('button', null,
        `${d} ${W.places[d].name}`);
        b.setAttribute('aria-pressed', d === S.dest);
        b.onclick = () => { S.dest = d; stop(); S.idx = 0; renderAll(); };
        return b; }));
  });
}
function renderAll() {
  dests(); grid($('gmap'), {hover: showCell, pick: showCell});
  renderRoute(); renderPolicy();
}
function show(t) {
  TABS.forEach(n => { $('tab-' + n).hidden = n !== t;
    $('b-' + n).setAttribute('aria-pressed', n === t); });
}
TABS.forEach(n => { $('b-' + n).onclick = () => show(n); });
$('play').onclick = play; $('pause').onclick = stop;
$('next').onclick = () => { stop(); step(1); };
$('back').onclick = () => { stop(); step(-1); };
$('reset').onclick = reset;
$('speed').onchange = () => { if (S.timer) { stop(); play(); } };
$('v-arrows').onclick = () => { S.view = 'arrows'; renderPolicy(); };
$('v-heat').onclick = () => { S.view = 'heat'; renderPolicy(); };
$('places').replaceChildren(...L.map(d => { const p = h('div', 'place');
  p.append(h('span', 'dot', d), h('span', null, `${W.places[d].name} `
    + `(${W.places[d].cell.join(', ')})`)); return p; }));
$('legend').replaceChildren(...Array.from({length: HMAX + 1},
  (_, v) => { const e = h('span', null, v);
    e.style.background = hcol(v); return e; }));
function reqBadge(id) {  // name and files; open it for demand and refs
  const r = D.requirements[id], d = h('details', 'req'), sm = h('summary');
  sm.append(h('b', null, `${r.id} ${r.name}`), ' ',
    h('span', 'files', r.files.join(', ')));
  d.append(sm, h('p', null, 'Demands: ' + r.demands));
  if (r.refs.length) d.append(h('p', 'muted', 'Met in:'),
    ...r.refs.map(ref => h('code', null, ref)));
  return d;
}
TABS.forEach(t => {
  const strip = h('div', 'reqs');
  strip.append(h('span', null, 'Requirements shown here:'),
    ...D.tab_requirements[t].map(reqBadge));
  $('tab-' + t).prepend(strip);
});
$('notshown').replaceChildren(...D.not_shown.map(id => {
  const r = D.requirements[id], d = h('div', 'out');
  d.append(h('b', null, `${r.id} ${r.name}`), h('br'),
    h('span', 'muted', r.files.join(', ')));
  return d;
}));
$('terrain').replaceChildren(...[
  [ROCK_GROUND, rock, 'Rock: obstacle, blocks the move'],
  [hcol(1), crater, 'Crater: hazard, -50 and end'],
].map(([ground, draw, text]) => {
  const row = h('div', 'icon'), svg = s('svg', {viewBox: `0 0 ${C} ${C}`});
  const g = s('g');
  g.append(s('rect', {width: C, height: C, rx: 4, fill: ground}));
  draw(g); svg.append(g); row.append(svg, h('span', null, text));
  return row;
}));
$('m-saved').onclick = () => setMode(false);
$('m-live').onclick = () => setMode(true);
$('ask').onsubmit = send;
renderAll(); renderLearning(); renderAgent(); show('Map'); checkLive();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    data = write_html(ROOT / "results" / "viewer.html")
    print("viewer: results/viewer.html")
    print(f"routes: {len(data['routes'])}")
    print(f"curves: {len(data['curves'])}")
    print(f"traces: {len(data['traces'])}")
