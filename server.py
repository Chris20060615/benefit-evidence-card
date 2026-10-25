"""Loopback-only demonstration server. No user questions are sent off-device."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from evidence import parse_document, search_document

ROOT = Path(__file__).resolve().parent
SOURCE_URL = 'https://www.nhsa.gov.cn/art/2025/3/16/art_14_16010.html'
EXPECTED_TITLE = '跨省异地就医如何直接报销？'
EXPECTED_PUBLISHER = '国家医疗保障局'
MAX_SOURCE_BYTES = 1_000_000
MAX_REQUEST_BYTES = 16_384
MAX_QUESTION_CHARS = 500


class SourceUnavailable(RuntimeError):
    pass


class SourceMetadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.values = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name'):
            self.values[attrs['name']] = attrs.get('content', '')


class SourceStore:
    """Load one fixed public document; validate cached bytes before parsing."""

    def __init__(self, cache_dir: Path, offline=False, refresh=False):
        self.cache_dir = Path(cache_dir)
        self.offline = offline
        self.refresh = refresh
        self.document = None
        self.error = None

    def _parse(self, raw: bytes, manifest: dict, cached: bool):
        if (not isinstance(manifest, dict)
                or not isinstance(manifest.get('sha256'), str)
                or not isinstance(manifest.get('retrieved_at'), str)):
            raise SourceUnavailable('The source cache metadata is invalid.')
        if len(raw) > MAX_SOURCE_BYTES:
            raise SourceUnavailable('The source response is too large.')
        try:
            text = raw.decode('utf-8')
            metadata = SourceMetadata()
            metadata.feed(text)
        except (UnicodeError, ValueError) as exc:
            raise SourceUnavailable('The source response could not be read.') from exc
        values = metadata.values
        if (values.get('ArticleTitle') != EXPECTED_TITLE
                or values.get('SiteName') != EXPECTED_PUBLISHER
                or not values.get('PubDate', '').startswith('2025-03-16')):
            raise SourceUnavailable('The source identity changed; review is required.')
        digest = hashlib.sha256(raw).hexdigest()
        if digest != manifest.get('sha256') or not manifest.get('retrieved_at'):
            raise SourceUnavailable('The source cache failed integrity checks.')
        source = {
            'source_id': 'nhsa-20250316-16010',
            'title': values['ArticleTitle'],
            'publisher': values['SiteName'],
            'published_date': values['PubDate'][:10],
            'url': SOURCE_URL,
            'retrieved_at': manifest['retrieved_at'],
            'snapshot_sha256': digest,
            'cache_state': 'verified cache' if cached else 'freshly retrieved',
        }
        try:
            return parse_document(text, source)
        except ValueError as exc:
            raise SourceUnavailable('The official article body could not be parsed.') from exc

    def initialize(self):
        raw_path = self.cache_dir / 'nhsa-16010.html'
        manifest_path = self.cache_dir / 'nhsa-16010.json'
        if not self.refresh and raw_path.is_file() and manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                self.document = self._parse(raw_path.read_bytes(), manifest, cached=True)
                return
            except (OSError, ValueError, SourceUnavailable):
                if self.offline:
                    raise SourceUnavailable('No valid verified cache is available in offline mode.')
        if self.offline:
            raise SourceUnavailable('No verified source cache is available in offline mode.')
        request = Request(SOURCE_URL, headers={'User-Agent': 'DocumentEvidencePrototype/0.1'})
        try:
            with urlopen(request, timeout=20) as response:
                if urlsplit(response.url).hostname != 'www.nhsa.gov.cn':
                    raise SourceUnavailable('The source redirected away from the expected publisher.')
                raw = response.read(MAX_SOURCE_BYTES + 1)
        except (OSError, URLError, TimeoutError) as exc:
            raise SourceUnavailable('The official source could not be reached.') from exc
        manifest = {
            'url': SOURCE_URL,
            'retrieved_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'sha256': hashlib.sha256(raw).hexdigest(),
        }
        document = self._parse(raw, manifest, cached=False)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        raw_temp = self.cache_dir / 'nhsa-16010.html.tmp'
        manifest_temp = self.cache_dir / 'nhsa-16010.json.tmp'
        raw_temp.write_bytes(raw)
        manifest_temp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        os.replace(raw_temp, raw_path)
        os.replace(manifest_temp, manifest_path)
        self.document = document


def create_server(host, port, store):
    static_routes = {
        '/': ('index.html', 'text/html; charset=utf-8'),
        '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
        '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
        '/favicon.svg': ('favicon.svg', 'image/svg+xml'),
    }

    class Handler(BaseHTTPRequestHandler):
        server_version = 'LocalEvidence/0.1'
        sys_version = ''

        def _headers(self, status, content_type, length):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(length))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers()

        def _json(self, status, data):
            raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self._headers(status, 'application/json; charset=utf-8', len(raw))
            self.wfile.write(raw)

        def _trusted_request(self):
            port = self.server.server_address[1]
            allowed_hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
            if self.headers.get('Host', '') not in allowed_hosts:
                self._json(403, {'error': 'Use the local address printed by the server.'})
                return False
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{name}' for name in allowed_hosts}:
                self._json(403, {'error': 'This local endpoint accepts same-origin requests only.'})
                return False
            return True

        def do_GET(self):
            if not self._trusted_request():
                return
            path = urlsplit(self.path).path
            if path in static_routes:
                filename, content_type = static_routes[path]
                try:
                    raw = (ROOT / 'web' / filename).read_bytes()
                except OSError:
                    self._json(500, {'error': 'A required interface file is missing.'})
                    return
                self._headers(200, content_type, len(raw))
                self.wfile.write(raw)
            elif path == '/api/health':
                self._json(200, {'server': 'ready', 'source_ready': bool(store.document)})
            elif path == '/api/source':
                if not store.document:
                    self._json(503, {'error': 'Source unavailable. Restart with network access or a verified cache.', 'status': 'source_unavailable'})
                    return
                self._json(200, {'status': 'ready', 'source': store.document['source'], 'capabilities': store.document.get('capabilities', [])})
            else:
                self._json(404, {'error': 'Route not found.'})

        def do_POST(self):
            if not self._trusted_request():
                return
            if urlsplit(self.path).path != '/api/search':
                self._json(404, {'error': 'Route not found.'})
                return
            if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
                self._json(415, {'error': 'Send a JSON request.'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                self._json(400, {'error': 'Invalid request length.'})
                return
            if not 0 < length <= MAX_REQUEST_BYTES:
                self._json(413, {'error': 'The request is empty or too large.'})
                return
            try:
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
            except (ValueError, UnicodeError):
                self._json(400, {'error': 'The request is not valid JSON.'})
                return
            question = payload.get('question') if isinstance(payload, dict) else None
            if not isinstance(question, str) or not question.strip():
                self._json(400, {'error': 'Enter a question first.'})
                return
            question = question.strip()
            if len(question) > MAX_QUESTION_CHARS:
                self._json(400, {'error': 'Keep the question within 500 characters.'})
                return
            if not store.document:
                self._json(503, {'error': 'No verified guide is available. Restart with network access or a verified cache.', 'status': 'source_unavailable'})
                return
            try:
                result = search_document(store.document, question)
            except Exception:
                self._json(500, {'error': 'The search could not be completed. No evidence has been inferred.'})
                return
            self._json(200, result)

        def log_message(self, format, *args):
            # Request bodies/questions are never logged or stored.
            sys.stderr.write(f'{self.command} {urlsplit(self.path).path} {args[1] if len(args) > 1 else ""}\n')

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def main():
    parser = argparse.ArgumentParser(description='Run the local one-document evidence prototype.')
    parser.add_argument('--host', default='127.0.0.1', choices=['127.0.0.1', 'localhost'])
    parser.add_argument('--port', type=int, default=8768)
    parser.add_argument('--cache-dir', type=Path, default=ROOT / '.cache')
    parser.add_argument('--offline', action='store_true', help='Require an existing verified source cache.')
    parser.add_argument('--refresh-source', action='store_true', help='Fetch and verify a fresh official source at startup.')
    args = parser.parse_args()
    store = SourceStore(args.cache_dir, offline=args.offline, refresh=args.refresh_source)
    try:
        store.initialize()
    except (OSError, SourceUnavailable) as exc:
        store.error = str(exc)
        print(f'Source unavailable: {exc}', file=sys.stderr)
    server = create_server(args.host, args.port, store)
    print(f'Local: http://127.0.0.1:{server.server_address[1]}/', flush=True)
    print(f'Source: {"verified" if store.document else "unavailable; interface remains accessible"}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
