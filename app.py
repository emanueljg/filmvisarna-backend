#!/usr/bin/env python3
from flask import Flask, current_app

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/api/header-title")
def header_title():
    return "IRONBOY THINGAMAJIGS"


if __name__ == '__main__':
    create_app().run(port=5000, debug=True)
