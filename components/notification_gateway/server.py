import logging
import json
import threading
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

PORT = 5054

class NGHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        logger.info('I catch POST request')
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f'I catched your message {data}'.encode())

class NGServer:
    httpd: HTTPServer

    def start(self):
        server_addr = ('', PORT)
        self.httpd = ThreadingHTTPServer(server_addr, NGHandler)
        server_thread = threading.Thread(target=self.httpd.serve_forever)
        logging.info('Starting server in standalone thread')
        server_thread.start()

    def stop(self):
        self.httpd.server_close()
        self.httpd.shutdown()
