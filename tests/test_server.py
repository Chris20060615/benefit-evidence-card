import hashlib
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from server import SourceStore, SourceUnavailable, create_server


class EmptyStore:
    document = None
    error = 'No source fixture.'


class HTTPBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server('127.0.0.1', 0, EmptyStore())
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method='GET', path='/', body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read()
        result = response.status, dict(response.getheaders()), data
        connection.close()
        return result

    def test_only_frontend_files_are_served(self):
        status, headers, data = self.request()
        self.assertEqual(status, 200)
        self.assertIn(b'Document evidence search', data)
        self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
        for path in ['/devpost/learner-profile.md', '/.git/config', '/server.py',
                     '/.cache/nhsa-16010.html', '/%2e%2e/server.py', '/../server.py']:
            with self.subTest(path=path):
                self.assertEqual(self.request(path=path)[0], 404)

    def test_source_unavailable_is_explicit(self):
        status, _, raw = self.request(path='/api/source')
        self.assertEqual(status, 503)
        self.assertEqual(json.loads(raw)['status'], 'source_unavailable')
        status, _, raw = self.request(path='/api/health')
        self.assertEqual(status, 200)
        self.assertFalse(json.loads(raw)['source_ready'])
        status, _, raw = self.request('POST', '/api/search', json.dumps({'question': 'Where is progress?'}), {'Content-Type': 'application/json'})
        self.assertEqual(status, 503)
        self.assertNotIn('evidence', json.loads(raw))

    def test_malformed_and_oversized_requests(self):
        for body in ['not json', '[]', '{}', '{"question":false}', '{"question":"   "}']:
            with self.subTest(body=body):
                self.assertEqual(self.request('POST', '/api/search', body, {'Content-Type': 'application/json'})[0], 400)
        oversized_question = json.dumps({'question': 'x' * 501})
        self.assertEqual(self.request('POST', '/api/search', oversized_question, {'Content-Type': 'application/json'})[0], 400)
        self.assertEqual(self.request('POST', '/api/search', 'x' * 17000, {'Content-Type': 'application/json'})[0], 413)
        self.assertEqual(self.request('POST', '/api/search', '{}', {'Content-Type': 'text/plain'})[0], 415)

    def test_cross_origin_and_untrusted_host_are_rejected(self):
        self.assertEqual(self.request(headers={'Host': 'attacker.example'})[0], 403)
        self.assertEqual(self.request(headers={'Origin': 'https://attacker.example'})[0], 403)
        self.assertEqual(self.request(headers={'Origin': f'http://127.0.0.1:{self.port}'})[0], 200)


class SourceCacheTests(unittest.TestCase):
    @staticmethod
    def fixture():
        return ('<html><head><meta name="ArticleTitle" content="跨省异地就医如何直接报销？">'
                '<meta name="SiteName" content="国家医疗保障局">'
                '<meta name="PubDate" content="2025-03-16 09:12"></head>'
                '<body><div id="zoom"><p>第四步：查看备案进度</p>'
                '<p>点击首页【备案记录】按钮。</p></div></body></html>').encode('utf-8')

    @staticmethod
    def write_cache(directory, raw, digest=None):
        (directory / 'nhsa-16010.html').write_bytes(raw)
        (directory / 'nhsa-16010.json').write_text(json.dumps({
            'sha256': digest or hashlib.sha256(raw).hexdigest(),
            'retrieved_at': '2026-01-01T00:00:00Z',
        }), encoding='utf-8')

    def test_verified_cache_loads_offline_with_acquisition_time(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.write_cache(directory, self.fixture())
            store = SourceStore(directory, offline=True)
            store.initialize()
            self.assertEqual(store.document['source']['cache_state'], 'verified cache')
            self.assertEqual(store.document['source']['retrieved_at'], '2026-01-01T00:00:00Z')

    def test_missing_corrupt_and_wrong_identity_caches_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            with self.assertRaises(SourceUnavailable):
                SourceStore(directory, offline=True).initialize()
            self.write_cache(directory, self.fixture(), digest='wrong-digest')
            with self.assertRaises(SourceUnavailable):
                SourceStore(directory, offline=True).initialize()
            changed = self.fixture().replace(b'2025-03-16', b'2025-03-17')
            self.write_cache(directory, changed)
            with self.assertRaises(SourceUnavailable):
                SourceStore(directory, offline=True).initialize()

    def test_invalid_manifest_structures_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / 'nhsa-16010.html').write_bytes(self.fixture())
            for manifest in [[], None, 42, {'sha256': [], 'retrieved_at': 'time'},
                             {'sha256': 'hash', 'retrieved_at': {'invalid': True}}]:
                with self.subTest(manifest=manifest):
                    (directory / 'nhsa-16010.json').write_text(json.dumps(manifest), encoding='utf-8')
                    with self.assertRaises(SourceUnavailable):
                        SourceStore(directory, offline=True).initialize()


if __name__ == '__main__':
    unittest.main()
