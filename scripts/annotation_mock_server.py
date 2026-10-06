"""Local stand-in for the Vercel API (in-memory). Usage: python scripts/annotation_mock_server.py <public_dir> <img_dir>; code abc123 -> A1."""
import json, sys, os, shutil
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
PUBLIC=sys.argv[1]; IMG=sys.argv[2]; CODES={'abc123':'A1'}; DB={}
class H(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path=path.split('?')[0]
        if path.startswith('/img/'): return os.path.join(IMG, path[5:])
        if path in ('/',''): path='/index.html'
        return os.path.join(PUBLIC, path.lstrip('/'))
    def log_message(self,*a): pass
    def _json(self, code, obj):
        b=json.dumps(obj).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or b'{}')
        ann=CODES.get(body.get('code'))
        if not ann: return self._json(401,{'error':'Mã người chấm không hợp lệ'})
        if self.path=='/api/session': return self._json(200,{'annotator_id':ann,'done':[p for (a,p) in DB if a==ann]})
        if self.path=='/api/submit':
            a=body['answers']; need=['faithful','coverage','language','layout','aesthetic','overall']
            if not all(a.get(k) in ('A','B','tie') for k in need): return self._json(400,{'error':'Thiếu câu trả lời'})
            DB[(ann,body['pair_id'])]=a; return self._json(200,{'ok':True})
        if self.path=='/api/_dump': return self._json(200,{f'{a}|{p}':v for (a,p),v in DB.items()})
        self._json(404,{})
ThreadingHTTPServer(('127.0.0.1',8765),H).serve_forever()
