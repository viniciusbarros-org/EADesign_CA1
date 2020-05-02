import sys
import os
sys.path.insert(0, "./vendor")
import requests
from datetime import datetime
import time
import MySQLdb
import json

class Tests:

    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')
    
    URL = {
        'SYNC':'http://35.205.206.0:5000/collect',
        'ASYNC': 'http://35.241.214.62:5000/collect'
    }

    analysis = []
    db = None
    db_c = None
    logs = []

    def __init__(self):
        self.analysis = []
        self.db=MySQLdb.connect(host=self.DB_HOST,db=self.DB_NAME, user=self.DB_USER,passwd=self.DB_PASS)
        self.db_c = self.db.cursor()


    def run(self, app:str, number:int=10, async_a_freq=None, async_b_freq=None, async_g_freq=None):
        url = self.URL[app]
        self.log('--------------------------------------------------------------------------------')
        self.log(f"Running {number} tests for app {app} in {url}")
        self.log('--------------------------------------------------------------------------------')
        for i in range(number):

            r = requests.get(url)
            response_time_ms = round(r.elapsed.total_seconds() * 1000)

            data = (
                app,
                r.status_code,
                response_time_ms,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                async_a_freq,
                async_b_freq,
                async_g_freq
            )
            self.analysis.append(data)
            self.log(f"End of test {i+1} -> {response_time_ms} ms")
            # if response_time_ms < 1000:
            #     sleep_gap = (1000 - response_time_ms)/1000
            #     time.sleep(sleep_gap)


        self.save_results()

    def save_results(self):
        self.log(f"Saving {len(self.analysis)} results to DB")
        self.db_c.executemany(
            # Change table name according to tests being performed.
            """INSERT INTO requests_ab (application, status_code, response_time_ms, exec_datetime, async_a_push_freq, async_b_push_freq, async_g_push_freq)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            self.analysis 
        )
        self.db.commit()
        self.analysis = []

    def log(self, msg):
        self.logs.append(msg)
        print(msg)

    def get_logs(self):
        return self.logs

def handler(request):
    tests = Tests()
    tests.run('ASYNC', 50, 2, 2, 0.05)
    

    return "<pre>"+json.dumps(tests.get_logs(), indent=2)


# for local only
handler(None)
