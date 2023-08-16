import http.server
import socketserver
import logging

from PIL import Image
import io
import json

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/hello':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Hello, World!")
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/send':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Extraia os valores do objeto JSON recebido
            id = data['id']
            valor = data['valor']

            print(f'O hidrômetro {id} enviou o valor {valor}')

            # Responda com um JSON de confirmação
            response = {'status': 'success'}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self.send_error(404)
            

            
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()