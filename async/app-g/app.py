from flask import Flask
from datetime import datetime
import requests
import time
import redis

app = Flask(__name__)

@app.route('/collect')
def collect():
    try:
        start = datetime.utcnow()
        
        redis_host = "redis-service"
        redis_port = 6379
        channel_a = 'app-a'
        channel_b = 'app-b'

        r = redis.Redis(host=redis_host, port=redis_port)

        pooling_frequency_in_sec = get_frequency(r)

        pubsub_a = r.pubsub(ignore_subscribe_messages=True)
        pubsub_b = r.pubsub(ignore_subscribe_messages=True)
        pubsub_a.subscribe(channel_a)
        pubsub_b.subscribe(channel_b)
        

        a = None 
        b = None 

        while (a is None or b is None):
            if a is None:
                a = pubsub_a.get_message()
            if b is None:
                b = pubsub_b.get_message()
            
            if (a is None or b is None):
                print(f"Not all messages ready, sleeping for {pooling_frequency_in_sec}")
                time.sleep(pooling_frequency_in_sec)
            else:
                print(a)
                print(b)
    

        finish = datetime.utcnow()

        return {
            "metrics": {
                "start": start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "finish": finish.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                "difference": str (finish-start)
            },
            "A news":a['data'].decode("utf-8"),
            "B News": b['data'].decode("utf-8")
        }
    except Exception as e:
        print(e)
        return f"Error when trying to pull info from A or B: {e}", 500


def get_frequency(redis):
    freq = redis.get('app-g-frequency')
    return int(freq) if freq is not None else 1
            


@app.route('/')
def index():
    return 'working fine'

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')