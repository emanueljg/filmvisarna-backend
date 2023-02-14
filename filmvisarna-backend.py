#!/usr/bin/env python3
from flask import Flask, current_app
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)



@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/api/header-title")
def header_title():
    return "IRONBOY THINGAMAJIGS"


if __name__ == '__main__':
    pass
    # use_reloader=False should fix the systemd
    # service quitting (don't ask me why...)
 #   app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
