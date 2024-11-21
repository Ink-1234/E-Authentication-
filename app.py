from http.server import SimpleHTTPRequestHandler, HTTPServer
import socketserver
import os
from urllib.parse import parse_qs
from io import BytesIO
from otp_utils import generate_otp, verify_otp
from PIL import Image, ImageDraw
import qrcode

PORT = 8000

# Dummy user data
users = {
    "user1": "password123"
}

session = {}

class MyHandler(SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/templates/login.html'  # Serve login.html for the root URL
        elif self.path == '/qr':
            self.path = '/templates/qr.html'
        elif self.path == '/otp':
            self.path = '/templates/otp.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = parse_qs(post_data.decode('utf-8'))

        if self.path == '/login':
            username = data.get('username')[0]
            password = data.get('password')[0]
            
            if username in users and users[username] == password:
                otp_secret = generate_otp()
                session['otp_secret'] = otp_secret

                qr_img = qrcode.make(otp_secret)
                qr_img.save("static/qr.png")
                
                self.send_response(301)
                self.send_header('Location', '/qr')
                self.end_headers()
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid credentials")
        
        elif self.path == '/verify':
            otp = data.get('otp')[0]
            if verify_otp(session.get('otp_secret'), otp):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OTP Verified! Authentication successful.")
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid OTP")

def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {PORT}')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
