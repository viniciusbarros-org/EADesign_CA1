from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/news')
def news():
    now = datetime.now()
    return f'Fresh news from B. <br/> Created at {now.day:02d}/{now.month:02d}/{now.year} {now.hour:02d}:{now.minute:02d}:{now.second:02d}'

@app.route('/')
def index():
    return 'working fine'

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')