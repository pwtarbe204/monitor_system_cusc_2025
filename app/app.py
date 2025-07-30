from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS
from routes import register_routes
from config import db

app = Flask(__name__)
app.secret_key = 'banacetamol'
CORS(app)

register_routes(app)
    
if __name__ == '__main__':
    app.run(debug=True)
