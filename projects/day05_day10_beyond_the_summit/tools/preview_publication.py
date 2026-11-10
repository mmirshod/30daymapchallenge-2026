"""Serve the staged Pages tree locally. Ctrl+C stops the server."""
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
root=Path(__file__).resolve().parents[3]/'docs'
with ThreadingHTTPServer(('127.0.0.1',8765),partial(SimpleHTTPRequestHandler,directory=str(root))) as server:
    print('Beyond the Summit: http://127.0.0.1:8765/day05/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
