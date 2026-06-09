#!/usr/bin/env python3
import http.server
import json
import os
import subprocess

WEBUI_ADDR = os.environ.get('WEBUI_ADDR', '0.0.0.0:8080')
HOST, PORT = WEBUI_ADDR.rsplit(':', 1)
PORT = int(PORT)

STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

SETUP_DONE_FILE = '/etc/twingate/.setup-done'
NETWORK_FILE = '/etc/twingate/webui-network'

MIME_MAP = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
}


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


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/status':
            s, rc = get_status()
            self._json({'ok': rc == 0, 'status': s})
            return
        if self.path == '/resources':
            s, rc = get_resources()
            self._json({'ok': rc == 0, 'resources': s})
            return
        if self.path == '/config':
            self._json({'network': read_file(NETWORK_FILE)})
            return
        self._serve_static(self.path)

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

    def _serve_static(self, path):
        if path == '/':
            path = '/index.html'
        _, ext = os.path.splitext(path)
        mime = MIME_MAP.get(ext, 'application/octet-stream')
        filepath = os.path.join(STATIC_DIR, path.lstrip('/'))
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
        except (OSError, IOError):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    server = http.server.HTTPServer((HOST, PORT), Handler)
    server.serve_forever()
