# main.py

from flask import Flask, render_template
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)