#!/usr/bin/env python3


from http.server import CGIHTTPRequestHandler
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
  server_address = ('', 8000)
  httpd = server_class(server_address, handler_class)
  try:
      httpd.serve_forever()
  except KeyboardInterrupt:
      httpd.server_close()

run(server_class=HTTPServer, handler_class=CGIHTTPRequestHandler)
