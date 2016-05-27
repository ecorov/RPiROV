#!/usr/bin/pythonRoot

import RPi.GPIO as G     
from flup.server.fcgi import WSGIServer 
import sys, urlparse


G.setmode(G.BCM)
G.setup(17, G.OUT)


def app(environ, start_response):
	start_response("200 OK", [("Content-Type", "text/html")])
	i = urlparse.parse_qs(environ["QUERY_STRING"])
	yield ('&nbsp;') 
	if "q" in i:
		if i["q"][0] == "w": 
			G.output(17, True)  
		elif i["q"][0] == "s":
			G.output(17, False)  


WSGIServer(app).run()

