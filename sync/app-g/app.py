from flask import Flask
from datetime import datetime
import requests

app = Flask(__name__)

@app.route('/collect')
def collect():
    try:
        start = datetime.utcnow()
        a = requests.get('http://app-a-sync:5000/news')
        b = requests.get('http://app-b-sync:5000/news')
        finish = datetime.utcnow()

        return {
            "metrics": {
                "start": start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "finish": finish.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "difference": str (finish-start)
            },
            "A news":a.text,
            "B News": b.text
        }
    except Exception as e:
        return "Error when trying to pull info from A or B", 500



@app.route('/')
def index():
    return 'working fine'

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')