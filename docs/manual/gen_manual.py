#!/usr/bin/env python3
"""Generate docs/manual/{zh-tw,en}/index.html from shared section data."""
import html, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

CSS = """
:root{--bg:#f5f7f9;--card:#fff;--ink:#1a2330;--mut:#5a6776;--pri:#2f5fd0;--ok:#0f7b4d;--warn:#9a6a00;--line:#e3e8ee}
*{box-sizing:border-box}body{margin:0;font:16px/1.65 -apple-system,"Segoe UI",Roboto,"Noto Sans TC",sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--pri)}.wrap{display:flex;min-height:100vh}
nav{width:260px;flex:none;background:#10213c;color:#dce6f5;padding:24px 18px;position:sticky;top:0;height:100vh;overflow:auto}
nav h1{font-size:19px;margin:0 0 2px;color:#fff}nav .sub{font-size:12.5px;color:#9fb4d8;margin-bottom:14px}
nav a{display:block;color:#c9d8ef;text-decoration:none;padding:7px 10px;border-radius:8px;font-size:14.5px}
nav a:hover{background:#1d3457;color:#fff}nav .lang{margin-top:18px;border-top:1px solid #2a4470;padding-top:12px;font-size:13.5px}
main{flex:1;max-width:980px;padding:34px 44px;margin:0 auto}
.banner{background:#e8f3ec;border:1px solid #bfe0cd;border-left:6px solid var(--ok);border-radius:10px;padding:14px 18px;font-size:14.5px;margin-bottom:26px}
.warnbox{background:#fdf3dc;border:1px solid #ecd9a2;border-left:6px solid var(--warn);border-radius:10px;padding:13px 17px;font-size:14.5px;margin:14px 0}
h2{font-size:24px;margin:42px 0 10px;border-bottom:2px solid var(--line);padding-bottom:8px}
h3{font-size:18px;margin:26px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 1px 4px rgba(16,33,60,.07);padding:18px 20px;margin:16px 0}
.shot{margin:18px 0}.shot img{width:100%;border-radius:8px;border:1px solid var(--line);box-shadow:0 2px 10px rgba(16,33,60,.12)}
.cap{font-size:14px;color:var(--mut);margin-top:8px}
.chips{margin-top:6px}.chip{display:inline-block;font-size:12px;padding:2px 10px;border-radius:999px;margin-right:6px;border:1px solid}
.chip.src{color:#274b8f;border-color:#b9cdf2;background:#eef3fc}.chip.ok{color:var(--ok);border-color:#9ed4b8;background:#e8f6ee}
.chip.na{color:var(--warn);border-color:#e4cd8e;background:#fbf2da}
table{border-collapse:collapse;width:100%;font-size:14.5px;margin:12px 0}th,td{border:1px solid var(--line);padding:8px 11px;text-align:left}
th{background:#eef2f7}code{background:#eef2f7;padding:1px 6px;border-radius:5px;font-size:.92em}
pre{background:#10213c;color:#dbe7fb;padding:15px 18px;border-radius:10px;overflow:auto;font-size:13.5px;line-height:1.55}
pre code{background:none;color:inherit;padding:0}
.mermaid{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px;margin:14px 0}
footer{color:var(--mut);font-size:13px;margin:48px 0 10px}
@media(max-width:900px){.wrap{flex-direction:column}nav{width:100%;height:auto;position:static}main{padding:22px 18px}}
"""

def chips(tier_ok=True):
    src = '<span class="chip src">Evidence: live screenshot · seeded demo</span>'
    if tier_ok:
        return src + '<span class="chip ok">Coverage: full-integration</span><span class="chip ok">Readiness: PASS (review.md)</span>'
    return src.replace("live screenshot · seeded demo","live screenshot · graceful empty state") + \
        '<span class="chip na">Coverage: not_assessed</span><span class="chip na">Readiness: not_assessed</span><span class="chip na">DEMO_NOT_ASSESSED</span>'

def shot(name, cap, ok=True):
    return f'<figure class="shot"><img src="../assets/{name}.png" alt="{html.escape(cap[:80])}" loading="lazy"><figcaption class="cap">{cap}<div class="chips">{chips(ok)}</div></figcaption></figure>'

L = {
 "zh-tw": dict(
   lang="zh-Hant", title="Asynqmon 使用手冊", other=("en","English version"),
   subtitle="Asynq task queue 監控 Web UI — team fork",
   banner="本手冊所有截圖均為 <b>live evidence</b>:真實 Valkey 9.1 + 真實 asynq worker/scheduler + canonical demo 資料(<code>docs/manual/demo/main.go</code>)。Product-level readiness:<b>PASS</b>(來源:<code>.agents/specs/003-*/review.md</code>、<code>004-*/review.md</code> + 12/12 browser smoke)。再生方式見 <a href='../../MANUAL_GENERATION_GUIDE.md'>MANUAL_GENERATION_GUIDE.md</a>。",
   nav=[("start","快速開始"),("flow","操作動線"),("dashboard","Dashboard"),("states","任務狀態"),("detail","任務詳情"),("servers","Servers"),("schedulers","Schedulers"),("redis","Redis Info"),("settings","Settings"),("metrics","Metrics(gap)"),("flags","CLI flags")],
 ),
 "en": dict(
   lang="en", title="Asynqmon User Manual", other=("zh-tw","中文版"),
   subtitle="Monitoring Web UI for the Asynq task queue — team fork",
   banner="Every screenshot is <b>live evidence</b>: real Valkey 9.1 + a real asynq worker/scheduler + the canonical demo scenario (<code>docs/manual/demo/main.go</code>). Product-level readiness: <b>PASS</b> (authority: <code>.agents/specs/003-*/review.md</code>, <code>004-*/review.md</code> + the 12/12 browser smoke). Regeneration: <a href='../../MANUAL_GENERATION_GUIDE.md'>MANUAL_GENERATION_GUIDE.md</a>.",
   nav=[("start","Getting started"),("flow","UX flow"),("dashboard","Dashboard"),("states","Task states"),("detail","Task details"),("servers","Servers"),("schedulers","Schedulers"),("redis","Redis Info"),("settings","Settings"),("metrics","Metrics (gap)"),("flags","CLI flags")],
 ),
}

GETTING = """<pre><code># 1) standalone binary
asynqmon --port=8080 --redis-addr=localhost:6379

# 2) container
podman run --rm -p 8080:8080 localhost/local/asynqmon --redis-addr=host.containers.internal:6379

# 3) Go library embed (primary consumption mode; UI bundle is go:embed'ed)
h := asynqmon.New(asynqmon.Options{
    RootPath:     "/monitoring",
    RedisConnOpt: asynq.RedisClientOpt{Addr: "localhost:6379"},
})
mux.Handle(h.RootPath()+"/", h)</code></pre>"""

MERMAID = """<div class="mermaid">
flowchart LR
    A["Dashboard"] -->|%s| B["Queue detail<br/>8 state tabs"]
    B -->|%s| C["Task details"]
    B -->|%s| D["run / archive / kill / delete"]
    A --> E["Servers"]
    A --> F["Schedulers"]
    A --> G["Redis Info"]
    A --> H["Settings"]
</div>"""

def states_table(zh):
    rows = [
      ("Active", "worker 處理中" if zh else "being processed", "video:transcode"),
      ("Pending", "等待派工(demo:佇列 paused 故停留)" if zh else "awaiting dispatch (demo: queue paused)", "image:resize ×5"),
      ("Aggregating", "Group 聚合等待" if zh else "waiting in a group", "metrics:event ×5"),
      ("Scheduled", "未到 ProcessIn 時間" if zh else "future ProcessIn", "report:generate ×5 (+2h)"),
      ("Retry", "失敗待重試" if zh else "failed, will retry", "sync:export"),
      ("Archived", "重試耗盡/手動封存" if zh else "exhausted / manually archived", "billing:charge; image:resize ×2"),
      ("Completed", "成功且在 Retention 期內" if zh else "succeeded within Retention", "email:* ×14"),
    ]
    tr = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td><code>{c}</code></td></tr>" for a,b,c in rows)
    h1 = ("狀態","含意","demo 樣本") if zh else ("State","Meaning","Demo sample")
    return f"<table><tr><th>{h1[0]}</th><th>{h1[1]}</th><th>{h1[2]}</th></tr>{tr}</table>"

def flags_table(zh):
    rows=[("--port / PORT","監聽埠(預設 8080)" if zh else "listen port (default 8080)"),
      ("--redis-addr / REDIS_ADDR","Redis/Valkey 位址" if zh else "Redis/Valkey address"),
      ("--redis-url / REDIS_URL","redis:// 或 redis-sentinel:// URI" if zh else "redis:// or redis-sentinel:// URI"),
      ("--redis-cluster-nodes","cluster 節點列表" if zh else "cluster node list"),
      ("--read-only","唯讀 UI(隱藏寫操作)" if zh else "read-only UI (hides mutating actions)"),
      ("--enable-metrics-exporter + --prometheus-addr","啟用 Metrics 頁" if zh else "enables the Metrics page")]
    tr="".join(f"<tr><td><code>{a}</code></td><td>{b}</td></tr>" for a,b in rows)
    return f"<table><tr><th>Flag / Env</th><th>{'說明' if zh else 'Description'}</th></tr>{tr}</table>"

def build(lang):
    d=L[lang]; zh = lang=="zh-tw"
    nav="".join(f'<a href="#{i}">{t}</a>' for i,t in d["nav"])
    flow_labels = ("點佇列","點任務列","操作") if zh else ("click queue","click task row","actions")
    cap=lambda z,e: z if zh else e
    body=f"""
<section id="start"><h2>{'快速開始 / Starter Assets' if zh else 'Getting Started / Starter Assets'}</h2>
<div class="card">{GETTING}
<p>{'Starter assets(git-tracked):' if zh else 'Starter assets (git-tracked):'}
<a href="../demo/main.go" download>demo/main.go</a> — {'一鍵種出全部任務狀態 + live worker/scheduler' if zh else 'seeds every task state + a live worker/scheduler'};
<a href="../../../ui/e2e/manual-screenshots.spec.ts" download>manual-screenshots.spec.ts</a> — {'截圖/VRT spec' if zh else 'screenshot/VRT spec'}.</p></div></section>

<section id="flow"><h2>{'操作動線(UX Flow)' if zh else 'UX Flow'}</h2>{MERMAID % flow_labels}</section>

<section id="dashboard"><h2>Dashboard</h2>
{shot("dashboard-overview-01-queues", cap("佇列堆疊長條(各狀態著色)、7 日 processed/failed 趨勢、佇列表。<b>low</b> 佇列為紅色 <b>paused</b>;Actions(⋯)可 pause/resume/delete。","Stacked per-state queue sizes, 7-day processed/failed trend, queue table. The <b>low</b> queue shows red <b>paused</b>; the Actions menu offers pause/resume/delete."))}
{shot("dashboard-overview-02-dark", cap("Dark mode(Settings → Dark Theme → Always)。","Dark mode (Settings → Dark Theme → Always)."))}</section>

<section id="states"><h2>{'任務狀態(8 個 tabs)' if zh else 'Task states (8 tabs)'}</h2>
<div class="card">{states_table(zh)}</div>
{shot("queues-tasks-01-active", cap("Active tab:payload 與已執行時間;非 READ_ONLY 可 cancel。","Active tab: payload and elapsed time; cancellable unless READ_ONLY."))}
{shot("queues-tasks-02-pending-paused", cap("Pending tab(佇列 paused):任務停留不派工。","Pending tab on a paused queue: tasks stay queued."))}
{shot("queues-tasks-03-scheduled", cap("Scheduled tab:Process-In 倒數;Run now / Archive / Delete 單筆或批次。","Scheduled tab: Process-In countdown; Run now / Archive / Delete per row or in bulk."))}
{shot("queues-tasks-04-retry", cap("Retry tab:最後錯誤、重試次數/上限、下次重試時間。","Retry tab: last error, retry count/limit, next retry time."))}
{shot("queues-tasks-05-archived", cap("Archived tab:封存原因留在 Last Error;可 Run / Delete。","Archived tab: archival reason kept in Last Error; Run / Delete available."))}
{shot("queues-tasks-06-completed", cap("Completed tab:Retention 期內的成功任務。","Completed tab: successful tasks within Retention."))}
{shot("queues-tasks-07-aggregating", cap("Aggregating tab:group 下拉切換群組;等待 GracePeriod/MaxSize。","Aggregating tab: group selector; waiting for GracePeriod/MaxSize."))}</section>

<section id="detail"><h2>{'任務詳情' if zh else 'Task details'}</h2>
{shot("task-detail-01-retry-task", cap("完整 payload(JSON 高亮)、Retry 計數、Last Error、下次重試;麵包屑回佇列。","Full payload (JSON highlighted), retry counters, Last Error, next retry; breadcrumbs back to the queue."))}</section>

<section id="servers"><h2>Servers</h2>
{shot("servers-workers-01-live", cap("一列 = 一個 asynq server(host:PID、佇列權重)。展開可見 <b>Active Workers</b>:live worker 真實在跑的 video:transcode 與 payload。","One row per asynq server (host:PID, queue weights). Expanded: <b>Active Workers</b> — the live video:transcode task with payload."))}</section>

<section id="schedulers"><h2>Schedulers</h2>
{shot("schedulers-entries-01-list", cap("demo scheduler 的兩條 cron entries,含 next/prev enqueue 與歷史。","Two cron entries from the demo scheduler, with next/prev enqueue times and history."))}</section>

<section id="redis"><h2>Redis Info</h2>
{shot("redis-info-01-stats", cap("連線中 Valkey/Redis 的 INFO 摘要。","INFO summary of the connected Valkey/Redis."))}</section>

<section id="settings"><h2>Settings</h2>
{shot("settings-config-01-light", cap("輪詢間隔(預設 8s)與 Dark Theme 偏好。","Polling interval (default 8s) and Dark Theme preference."))}
{shot("settings-config-02-dark", cap("Dark mode 設定頁。","Settings page in dark mode."))}</section>

<section id="metrics"><h2>Metrics</h2>
<div class="card"><p>{('啟用:server 帶 <code>--enable-metrics-exporter --prometheus-addr=&lt;prom&gt;</code>;Prometheus 抓 server 的 <code>/metrics</code>(exporter 佔用此路徑,<b>UI 的 Metrics 頁在 <code>/q/metrics</code></b>,由側欄進入)。') if zh else ('Enable with <code>--enable-metrics-exporter --prometheus-addr=&lt;prom&gt;</code>; Prometheus scrapes <code>/metrics</code> on the server port (the exporter owns that path — <b>the UI Metrics view lives at <code>/q/metrics</code></b>, via the sidebar).')}</p></div>
{shot("metrics-live-01-charts", cap("真實圖表:Tasks Processed / Failed / Error Rate(Prometheus 5s scrape,demo worker 真實流量)。","Real charts: Tasks Processed / Failed / Error Rate (Prometheus 5s scrape, real demo-worker traffic)."))}
{shot("metrics-live-02-charts-more", cap("下半部:per-queue 序列;右上可切時間窗與佇列過濾。","Lower half: per-queue series; time-window and queue filters top-right."))}
{shot("metrics-gap-01-no-prometheus", cap("未配置 Prometheus 時的 graceful 空態(對照)。","Graceful empty state when no Prometheus is configured (for contrast)."))}</section>

<section id="flags"><h2>CLI flags</h2><div class="card">{flags_table(zh)}
<p><code>asynqmon --help</code>{'(Go flag 慣例,exit code 2)' if zh else ' (Go flag convention — exits with code 2)'}</p></div></section>

<footer>{'生成於' if zh else 'Generated'} 2026-06-07 · branch docs/manual-review-generation · {'證據與再生:' if zh else 'evidence & regeneration: '}<a href="../../MANUAL_GENERATION_GUIDE.md">MANUAL_GENERATION_GUIDE.md</a></footer>
"""
    other_href=f"../{d['other'][0]}/index.html"
    return f"""<!DOCTYPE html><html lang="{d['lang']}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{d['title']}</title><style>{CSS}</style></head><body><div class="wrap">
<nav><h1>{d['title']}</h1><div class="sub">{d['subtitle']}</div>{nav}
<div class="lang"><a href="{other_href}">🌐 {d['other'][1]}</a></div></nav>
<main><div class="banner">{d['banner']}</div>{body}</main></div>
<script type="module">import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";mermaid.initialize({{startOnLoad:true,theme:"neutral"}});</script>
</body></html>"""

for lang in L:
    out = ROOT/"docs/manual"/lang/"index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(lang))
    print("wrote", out)
