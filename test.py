from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/gps', methods=['POST'])
def post_data():
    print(request.data)
    return ('', 200)
