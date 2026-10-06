#!/usr/bin/env python3
"""Bonus Challenge 6e: Real-time Multi-Agent Monitoring Dashboard.

Standard-library HTTP server that provides a real-time monitoring dashboard
displaying agent condition performance, token consumption, execution latencies,
and live execution logs from results/.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.render_dashboard_html().encode("utf-8"))
        elif path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(self.collect_metrics(), indent=2).encode("utf-8"))
        elif path == "/logs":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(self.collect_logs(), indent=2).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def collect_metrics(self):
        runs = []
        for p in sorted(RESULTS_DIR.glob("*/*/run.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                runs.append({
                    "task": data.get("task"),
                    "condition": data.get("condition"),
                    "role": data.get("role"),
                    "passed": data.get("passed", 0),
                    "total": data.get("total", 0),
                    "score": data.get("score", 0),
                    "tokens": data.get("tokens", {}).get("total", 0),
                    "seconds": data.get("seconds", 0),
                    "skills_read": data.get("skills_read", 0),
                    "error": bool(data.get("error"))
                })
            except Exception:
                pass
        return {"total_runs": len(runs), "runs": runs}

    def collect_logs(self):
        logs = []
        for p in sorted(RESULTS_DIR.glob("*/*/trace.md")):
            try:
                content = p.read_text(encoding="utf-8")
                logs.append({
                    "path": str(p.relative_to(ROOT)),
                    "preview": content[:500] + "..." if len(content) > 500 else content
                })
            except Exception:
                pass
        return logs

    def render_dashboard_html(self):
        metrics = self.collect_metrics()
        rows = "".join(
            f"<tr><td>{r['condition']}</td><td>{r['task']}</td><td>{r['role']}</td>"
            f"<td>{r['passed']}/{r['total']} ({r['score']:.2f})</td>"
            f"<td>{r['tokens']:,}</td><td>{r['seconds']}s</td><td>{r['skills_read']}</td>"
            f"<td>{'❌ Err' if r['error'] else '✅ OK'}</td></tr>"
            for r in metrics["runs"]
        )
        return f"""<!DOCTYPE html>
<html>
<head>
<title>Agent Harness Monitoring Dashboard</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 2rem; background: #0f172a; color: #f8fafc; }}
h1 {{ color: #38bdf8; }}
.card {{ background: #1e293b; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }}
th {{ background: #0f172a; color: #94a3b8; }}
.badge {{ background: #0284c7; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; }}
</style>
</head>
<body>
<h1>🚀 Multi-Agent Harness Dashboard <span class="badge">Live</span></h1>
<div class="card">
  <h2>Benchmark Summary</h2>
  <p>Total Runs Tracked: <strong>{metrics['total_runs']}</strong></p>
  <table>
    <thead><tr><th>Condition</th><th>Task</th><th>Role</th><th>Score</th><th>Tokens</th><th>Duration</th><th>Skills Read</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
</body>
</html>"""


def run_dashboard(port=8000):
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"Monitoring Dashboard running at http://localhost:{port}/dashboard")
    server.serve_forever()


if __name__ == "__main__":
    run_dashboard()
