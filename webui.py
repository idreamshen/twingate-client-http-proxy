#!/usr/bin/env python3
import http.server
import json
import os
import subprocess
import urllib.parse

WEBUI_ADDR = os.environ.get('WEBUI_ADDR', '0.0.0.0:8080')
HOST, PORT = WEBUI_ADDR.rsplit(':', 1)
PORT = int(PORT)

SETUP_DONE_FILE = '/etc/twingate/.setup-done'
NETWORK_FILE = '/etc/twingate/webui-network'


def read_file(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except (OSError, IOError):
        return ''


def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def run_cmd(cmd, input_data=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, input=input_data, timeout=120)
        return r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return 'Command timed out', 1
    except Exception as e:
        return str(e), 1


def get_status():
    out, rc = run_cmd(['twingate', 'status'])
    return out, rc


def get_resources():
    out, rc = run_cmd(['twingate', 'resources'])
    return out, rc


def do_login(network):
    if os.path.exists(SETUP_DONE_FILE):
        os.remove(SETUP_DONE_FILE)
    write_file(NETWORK_FILE, network)
    setup_input = f'A\n{network}\nn\n\nn\nn\nn\n'
    run_cmd(['twingate', 'setup'], input_data=setup_input)
    run_cmd(['twingate', 'start'])


HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Twingate Client Web UI</title>
<style>
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; background: #fafafa; color: #222; }
h1 { font-size: 1.5rem; }
pre { background: #f4f4f4; padding: 1rem; overflow-x: auto; border-radius: 6px; font-size: 13px; line-height: 1.4; white-space: pre-wrap; word-break: break-all; }
pre#status { background: #fff; border: 1px solid #ddd; min-height: 3rem; }
label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
input[type=text] { width: 100%; padding: 0.5rem; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; }
input[type=text]:focus { border-color: #0066cc; outline: none; box-shadow: 0 0 0 2px rgba(0,102,204,0.2); }
button { padding: 0.5rem 1.5rem; font-size: 1rem; cursor: pointer; background: #0066cc; color: #fff; border: none; border-radius: 4px; }
button:hover { background: #0052a3; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
fieldset { border: 1px solid #ccc; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; background: #fff; }
legend { font-weight: 700; padding: 0 0.5rem; }
small { display: block; margin-top: 0.25rem; color: #666; }
.card { background: #fff; border: 1px solid #ddd; border-radius: 6px; padding: 1rem; margin-bottom: 1rem; }
.card h2 { margin: 0 0 0.5rem 0; font-size: 1.1rem; }
</style>
</head>
<body>
<h1>Twingate Client</h1>

<form id="login-form">
<fieldset>
<legend>Network Configuration</legend>
<label for="network">Twingate Network Name</label>
<input type="text" id="network" name="network" value="SAVED_NETWORK" placeholder="e.g. acme" required pattern="[A-Za-z0-9-]+" title="Letters, numbers, and hyphens only">
<small>Twingate network name (e.g. <code>acme</code> for <code>acme.twingate.com</code>)</small>
</fieldset>
<button type="submit" id="login-btn">Login</button>
</form>

<div class="card">
<h2>Status</h2>
<pre id="status">Loading...</pre>
</div>

<div class="card">
<h2>Resources</h2>
<pre id="resources">Loading...</pre>
</div>

<script>
const savedNetwork = 'SAVED_NETWORK';

async function fetchStatus() {
  try {
    const r = await fetch('/status');
    const data = await r.json();
    document.getElementById('status').textContent = data.status || 'Unable to get status';
  } catch {
    document.getElementById('status').textContent = 'Failed to fetch status';
  }
}

async function fetchResources() {
  try {
    const r = await fetch('/resources');
    const data = await r.json();
    document.getElementById('resources').textContent = data.resources || 'Unable to get resources';
  } catch {
    document.getElementById('resources').textContent = 'Failed to fetch resources';
  }
}

fetchStatus();
setInterval(fetchStatus, 2000);
fetchResources();
setInterval(fetchResources, 2000);

document.getElementById('login-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const network = document.getElementById('network').value;
  btn.disabled = true;
  btn.textContent = 'Logging in...';
  try {
    await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ network })
    });
  } catch {}
  btn.disabled = false;
  btn.textContent = 'Login';
});
</script>
</body>
</html>'''


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/status':
            s, rc = get_status()
            ok = rc == 0
            self._json({'ok': ok, 'status': s})
            return
        if self.path == '/resources':
            s, rc = get_resources()
            ok = rc == 0
            self._json({'ok': ok, 'resources': s})
            return
        self._serve_page()

    def do_POST(self):
        if self.path != '/login':
            self._json({'ok': False, 'error': 'not found'}, 404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        try:
            params = json.loads(body)
        except json.JSONDecodeError:
            self._json({'ok': False, 'error': 'invalid json'}, 400)
            return
        network = (params.get('network') or '').strip()
        if not network:
            self._json({'ok': False, 'error': 'network is required'}, 400)
            return
        do_login(network)
        self._json({'ok': True})

    def _serve_page(self):
        saved = read_file(NETWORK_FILE)
        page = HTML.replace('SAVED_NETWORK', saved)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(page.encode())

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    server = http.server.HTTPServer((HOST, PORT), Handler)
    server.serve_forever()
