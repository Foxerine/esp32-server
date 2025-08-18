import http.server
import socketserver
import os

PORT = 8005  # 你可以修改端口号
DIRECTORY = "./test"  # 指定要对外服务的目录

print(f"当前工作目录：{os.getcwd()}")

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 更改当前工作目录到指定目录
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"serving files from {DIRECTORY} at port {PORT}")
    print("Server is running. Press Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Server stopped.")
    httpd.server_close()
    print("Server closed.")
