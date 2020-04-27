from datetime import datetime
import redis
import time

class App:
    redis = None
    pubsub = None
    redis_host = "redis-service"
    redis_port = 6379
    channel = 'app-a'
    # Frequency defaults to 1 if not set in Redis
    # Do not set it in here
    pushing_frequency_in_sec = None 
    frequency_key = 'app-a-frequency'

    def __init__(self):
        self.redis = redis.Redis(host=self.redis_host, port=self.redis_port)
        self.pubsub = self.redis.pubsub
        freq = self.redis.get(self.frequency_key)
        
        if freq is None:
            self.redis.set(self.frequency_key, 1)
            freq = self.redis.get(self.frequency_key)

        self.pushing_frequency_in_sec = int(freq)
        

    def run(self):
        while(True):
            now = datetime.now()
            message = f'Fresh news from A. <br/> Created at {now.day:02d}/{now.month:02d}/{now.year} {now.hour:02d}:{now.minute:02d}:{now.second:02d}'
            try:
                self.redis.publish(self.channel, message)
            except Exception as e:
                self.log_error(f"Unable to publish to redis {self.redis_host}:{self.redis_port}")
            
            self.log_info(f"sleeping for {self.pushing_frequency_in_sec} seconds")
            time.sleep(self.pushing_frequency_in_sec)

    def log_info(self, msg=''):
        print(f"[INFO] {msg}")
    
    def log_error(self, msg=''):
        print(f"[ERROR] {msg}")
        

app = App()
app.run()